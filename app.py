import json
import os
import random
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, redirect, render_template

try:
    from groq import Groq
except ImportError:
    Groq = None

app = Flask(__name__)
app.config['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY', '')
app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL', 'https://rnwoebohgcdwpijyyekq.supabase.co')
app.config['SUPABASE_ANON_KEY'] = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJud29lYm9ob2djd3Bpanl5ZWtxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxMjM4MTYsImV4cCI6MjEwMzY5OTgxNn0.6Le1ib4awX5ukOtGYfMzgSTOgUtl5m9NousEfajGsyY')
PROFILE_FILE = Path(app.root_path) / 'profile_data.json'
KNOWLEDGE_FILE = Path(app.root_path) / 'data' / 'recovery_knowledge.json'


def load_profile():
    if not PROFILE_FILE.exists():
        return None
    try:
        return json.loads(PROFILE_FILE.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None


def save_profile(profile):
    PROFILE_FILE.write_text(json.dumps(profile, indent=2), encoding='utf-8')


def calculate_hours_between(start_time, end_time):
    try:
        start_dt = datetime.strptime(start_time, '%H:%M')
        end_dt = datetime.strptime(end_time, '%H:%M')
        duration = (end_dt - start_dt).total_seconds() / 3600
        return round(max(0.0, duration), 2)
    except ValueError:
        return 0.0


def load_recovery_knowledge():
    if not KNOWLEDGE_FILE.exists():
        return {"injuries": {"general": {"treatment": [], "pt_exercises": [], "strengthening": [], "helpful_links": []}}, "links": []}
    try:
        return json.loads(KNOWLEDGE_FILE.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return {"injuries": {"general": {"treatment": [], "pt_exercises": [], "strengthening": [], "helpful_links": []}}, "links": []}


GROQ_API_KEY = app.config.get('GROQ_API_KEY') or os.getenv('GROQ_API_KEY', '')
client = Groq(api_key=GROQ_API_KEY) if Groq is not None and GROQ_API_KEY else None

# Exercise bank categorized for dynamic generation
EXERCISE_BANK = {
    "warmup": {
        "foot_articulation": ["Relevés", "Elevés", "Pliés in 1st", "Ankle Circles"],
        "core": ["Plank Holds", "Ab Crunches", "Bicycle Kicks", "Hollow Body Holds"],
        "legs": ["Walking Lunges", "Leg Swings", "Squat Pulses", "High Knees"],
        "cardio_hiphop": ["Jumping Jacks", "Groove Steps", "Mountain Climbers", "Pop Squats"],
        "ballet_flex": ["Dynamic Battements", "Port de Bras", "Cat-Cow Flow", "Side Swipes"]
    },
    "cooldown": [
        "Hamstring Hold", "Hip Flexor Stretch", "Child's Pose", "Butterfly Stretch",
        "Calf Wall Stretch", "Deep Diaphragmatic Breathing", "Quad Stretch", "Seated Torso Twist"
    ]
}

CHALLENGE_EXERCISES = [
    "Jumping Jacks", "High Knees", "Butt Kicks", "Ab Crunches",
    "Mountain Climbers", "Squat Pulses", "Marching Knees", "Fast Toe Taps",
    "Standing Cross Crunches"
]

STATIONARY_WARMUP_EXERCISES = {
    "Plank Holds",
    "Hollow Body Holds",
    "Squat Pulses",
    "High Knees"
}

EXERCISE_GUIDANCE = {
    "Relevés": "Stand tall, feet under hips, and rise onto the balls of your feet with soft knees.",
    "Elevés": "Feet under hips, lift up onto the balls of your feet, and keep your body long and steady.",
    "Pliés in 1st": "Turn the feet out, bend both knees, and keep the heels down as you rise back up.",
    "Ankle Circles": "Keep one leg bent, lift the foot slightly, and circle the ankle slowly in both directions.",
    "Plank Holds": "Hands under shoulders, body in one line, and keep the hips level as you brace your core.",
    "Ab Crunches": "Lie down, bend the knees, and lift just your shoulders off the floor as you exhale.",
    "Bicycle Kicks": "Bring one knee toward your chest and switch sides with smooth control.",
    "Hollow Body Holds": "Lift your head, arms, and legs a little off the floor and keep your lower back gently rounded.",
    "Walking Lunges": "Step one foot forward, bend both knees, and push through the front heel to stand tall again.",
    "Leg Swings": "Stand on one leg, swing the other leg gently forward and back, and stay balanced.",
    "Squat Pulses": "Stand with feet a little wider than hips, squat down, and pulse up and down with control.",
    "High Knees": "Drive one knee up at a time, stay tall, and keep your chest lifted.",
    "Jumping Jacks": "Jump wide, raise your arms overhead, and come back to center with control.",
    "Groove Steps": "Step side to side with a soft bounce and keep your knees relaxed and your rhythm steady.",
    "Mountain Climbers": "Start in a high plank, drive one knee in, switch sides, and keep your back flat.",
    "Pop Squats": "Drop into a squat, pause, then spring up small and smooth.",
    "Dynamic Battements": "Stand tall, extend one leg out, and switch legs smoothly with a lifted torso.",
    "Port de Bras": "Keep your shoulders relaxed and lift your arms gently through each position with an open chest.",
    "Cat-Cow Flow": "On hands and knees, arch your back like a cat and then lift the chest like a cow.",
    "Side Swipes": "Step wide, swing one arm across the body, and alternate sides with easy control.",
    "Butt Kicks": "Run in place, bring each heel toward the glute, and keep your chest tall and light.",
    "Marching Knees": "Lift the knees toward the chest, keep the pelvis steady, and stay tall on your feet.",
    "Fast Toe Taps": "Tap one foot quickly in front of the other and stay balanced over the standing leg.",
    "Standing Cross Crunches": "Lift one knee toward the opposite elbow and alternate sides with a tall chest.",
    "Hamstring Hold": "Hinge forward from the hips, keep the back long, and hold the stretch with soft knees.",
    "Hip Flexor Stretch": "Step one foot back, bend the front knee gently, and feel the stretch in the front of the back hip.",
    "Child's Pose": "Sit back toward your heels, stretch the arms forward, and let the chest relax down.",
    "Butterfly Stretch": "Sit tall, bring the feet together, and let the knees relax out as you fold forward gently.",
    "Calf Wall Stretch": "Place your hands on a wall, step one foot back, and press the heel down with a soft front knee.",
    "Deep Diaphragmatic Breathing": "Sit tall, inhale slowly through the nose, and let your ribs expand before you exhale.",
    "Quad Stretch": "Pull one heel toward the glute, keep the knees together, and stay tall in the standing leg.",
    "Seated Torso Twist": "Sit tall, twist gently through the chest, and keep the movement easy and controlled."
}


def challenge_rank(duration, reps):
    thresholds = {
        5: (30, 41, 61),
        10: (60, 71, 91),
        15: (90, 101, 121)
    }
    bronze, silver, gold = thresholds.get(duration, thresholds[5])
    if reps >= gold:
        return 'Gold'
    if reps >= silver:
        return 'Silver'
    if reps >= bronze:
        return 'Bronze'
    return 'Keep practicing'


def parse_bool(value):
    return value is True or str(value).lower() in ('1', 'true', 'yes', 'on')

def get_rep_count(age, is_challenge=False):
    if is_challenge:
        return None  # AMRAP (As Many Reps As Possible)
    return 15 if age <= 14 else 25


def build_routine_instructions(name, routine_type, duration_seconds):
    if name in EXERCISE_GUIDANCE:
        return EXERCISE_GUIDANCE[name]

    generic = {
        "warmup": f"Keep it smooth and easy. Move through {name.lower()} with control, stand tall, and breathe normally.",
        "cooldown": f"Ease into {name.lower()} slowly, breathe out as you relax, and stop before anything feels forced."
    }
    return generic.get(routine_type, f"Stay relaxed, stay controlled, and keep your movement easy with {name.lower()}.")


def build_routine_description(name, routine_type, duration_seconds):
    if name in EXERCISE_GUIDANCE:
        return EXERCISE_GUIDANCE[name]

    generic = {
        "warmup": f"Stay tall, move with control, and keep your body lined up as you {name.lower()}.",
        "cooldown": f"Breathe slowly and let the stretch settle in without forcing it."
    }
    return generic.get(routine_type, f"Keep it smooth and easy with {name.lower()}.")


def get_num_exercises_for_duration(duration):
    return {5: 3, 10: 6, 15: 9}.get(duration, 3)


def build_routine(routine_type, duration, age=15, style='ballet', is_challenge=False):
    num_exercises = get_num_exercises_for_duration(duration)
    time_per_exercise = (duration * 60) // num_exercises
    routine = []

    if routine_type == "warmup":
        pool = EXERCISE_BANK["warmup"]["foot_articulation"] + EXERCISE_BANK["warmup"]["core"] + EXERCISE_BANK["warmup"]["legs"]
        if style in ["hip-hop", "jazz"]:
            pool += EXERCISE_BANK["warmup"]["cardio_hiphop"]
        if style in ["ballet", "contemporary"]:
            pool += EXERCISE_BANK["warmup"]["ballet_flex"]

        if is_challenge:
            selected = CHALLENGE_EXERCISES[:num_exercises]
        else:
            selected = random.sample(pool, min(num_exercises, len(pool)))

        for ex in selected:
            description = build_routine_description(ex, "warmup", time_per_exercise)
            is_stationary = ex in STATIONARY_WARMUP_EXERCISES
            hold_text = f"Hold {time_per_exercise} sec"
            routine.append({
                "name": ex,
                "duration_sec": time_per_exercise,
                "reps": None if is_stationary else get_rep_count(age, is_challenge),
                "is_challenge": is_challenge,
                "is_stationary": is_stationary,
                "instruction": build_routine_instructions(ex, "warmup", time_per_exercise),
                "description": description,
                "short_description": description,
                "target_reps": "AMRAP" if is_challenge else (hold_text if is_stationary else get_rep_count(age, is_challenge)),
                "challenge_mode": is_challenge
            })
    else:
        selected = random.sample(EXERCISE_BANK["cooldown"], min(num_exercises, len(EXERCISE_BANK["cooldown"])))
        for ex in selected:
            description = build_routine_description(ex, "cooldown", time_per_exercise)
            routine.append({
                "name": ex,
                "hold_duration_sec": time_per_exercise,
                "type": "stationary_stretch",
                "instruction": build_routine_instructions(ex, "cooldown", time_per_exercise),
                "description": description,
                "short_description": description,
                "target_reps": f"Hold {time_per_exercise} sec"
            })

    return routine


@app.route('/')
def landing_page():
    return render_template('index.html', profile=load_profile() or {})

@app.route('/login')
def login_page():
    return render_template('login.html', supabase_url=app.config['SUPABASE_URL'], supabase_anon_key=app.config['SUPABASE_ANON_KEY'])

@app.route('/survey')
def survey_page():
    if load_profile():
        return redirect('/dance')
    return render_template('survey.html')

@app.route('/hourtracker')
def hourtracker_page():
    return render_template('hourtracker.html', profile=load_profile() or {})

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html', profile=load_profile() or {})

@app.route('/settings')
def settings_page():
    return render_template('settings.html', profile=load_profile() or {})

@app.route('/api/profile-status')
def profile_status():
    return jsonify({'has_profile': bool(load_profile())})

@app.route('/api/profile', methods=['GET', 'POST'])
def update_profile():
    profile = load_profile() or {}
    data = request.get_json(silent=True) or {}

    if request.method == 'GET':
        return jsonify(profile)

    avatar = data.get('avatar', profile.get('avatar', ''))
    if avatar and not avatar.startswith('data:image/'):
        return jsonify({'error': 'Please provide a valid image.'}), 400

    if 'name' in data:
        profile['name'] = str(data.get('name', '')).strip()
    if 'age' in data:
        profile['age'] = data.get('age', '')
    if 'hours_per_week' in data:
        profile['hours_per_week'] = data.get('hours_per_week', '')
    if 'dance_days' in data:
        profile['dance_days'] = data.get('dance_days', [])
    if 'style' in data:
        profile['style'] = data.get('style', '')
    if 'injuries' in data:
        profile['injuries'] = str(data.get('injuries', '')).strip()
    if 'avatar' in data:
        profile['avatar'] = avatar
    if 'dance_hours_log' in data:
        profile['dance_hours_log'] = data.get('dance_hours_log', [])

    save_profile(profile)
    return jsonify({'status': 'saved', 'profile': profile})

@app.route('/api/challenge-result', methods=['POST'])
def challenge_result():
    profile = load_profile()
    if not profile:
        return jsonify({'error': 'No profile has been created yet.'}), 404

    data = request.get_json(silent=True) or {}
    duration = int(data.get('duration', 5))
    reps = max(0, int(data.get('reps', 0)))
    if duration not in (5, 10, 15):
        return jsonify({'error': 'Challenge duration must be 5, 10, or 15 minutes.'}), 400

    result = {'duration': duration, 'reps': reps, 'ranking': challenge_rank(duration, reps)}
    profile.setdefault('challenge_results', []).append(result)
    save_profile(profile)
    return jsonify({'result': result, 'profile': profile})

@app.route('/app')
def main_app():
    return render_template('dance.html')

@app.route('/dance')
def dance_app():
    return render_template('dance.html')

@app.route('/submit-survey', methods=['POST'])
def submit_survey():
    data = request.get_json(silent=True) or {}
    profile = {
        'name': str(data.get('name', '')).strip(),
        'age': data.get('age', ''),
        'hours_per_week': data.get('hours_per_week', ''),
        'dance_days': data.get('dance_days', []),
        'style': data.get('style', ''),
        'injuries': str(data.get('injuries', '')).strip(),
        'dance_hours_log': []
    }
    if not profile['name'] or not profile['age'] or not profile['hours_per_week']:
        return jsonify({'error': 'Name, age, and dance hours are required.'}), 400
    save_profile(profile)
    return jsonify({"redirect": "/hourtracker"})


@app.route('/api/dance-hours', methods=['GET', 'POST'])
def api_dance_hours():
    profile = load_profile() or {}
    if request.method == 'GET':
        return jsonify({'dance_hours_log': profile.get('dance_hours_log', [])})

    data = request.get_json(silent=True) or {}
    if data.get('skip_for_now'):
        return jsonify({'status': 'skipped', 'redirect': '/dance'})

    dance_date = (data.get('date') or '').strip()
    start_time = (data.get('start_time') or '').strip()
    end_time = (data.get('end_time') or '').strip()
    if not dance_date or not start_time or not end_time:
        return jsonify({'error': 'Please enter your start and end time.'}), 400

    duration_hours = calculate_hours_between(start_time, end_time)
    if duration_hours <= 0:
        return jsonify({'error': 'End time must be later than the start time.'}), 400

    record = {
        'date': dance_date,
        'start_time': start_time,
        'end_time': end_time,
        'hours': round(duration_hours, 2),
        'logged_at': datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    }
    log = profile.setdefault('dance_hours_log', [])
    log.append(record)
    save_profile(profile)
    return jsonify({'status': 'saved', 'record': record, 'redirect': '/dance'})


@app.route('/api/warmup', methods=['GET', 'POST'])
def api_warmup():
    data = request.get_json(silent=True) or {}
    style = request.args.get('style', data.get('style', 'ballet'))
    duration = int(request.args.get('duration', data.get('duration', 5)))
    age = int(request.args.get('age', data.get('age', 15)))
    is_challenge = parse_bool(request.args.get('challenge_mode', data.get('challenge_mode', False)))
    return jsonify({"routine": build_routine("warmup", duration, age, style, is_challenge), "total_duration": duration})


@app.route('/api/cooldown', methods=['GET', 'POST'])
def api_cooldown():
    data = request.get_json(silent=True) or {}
    duration = int(request.args.get('duration', data.get('duration', 5)))
    return jsonify({"routine": build_routine("cooldown", duration), "total_duration": duration})


@app.route('/api/log-pain', methods=['POST'])
def log_pain():
    data = request.get_json(silent=True) or {}
    return jsonify({"status": "logged", "area": data.get('area', ''), "level": data.get('level', 0)})


@app.route('/api/pt-directory', methods=['POST'])
def pt_directory():
    data = request.get_json(silent=True) or {}
    location = data.get('location', '')
    if not location:
        return jsonify({"error": "Please enter a location or zip code."}), 400

    directory = [
        {"name": "Peak Performance Physical Therapy", "type": "Sports Rehab", "location": f"Near {location}", "phone": "(555) 014-2211", "map_url": "https://maps.google.com"},
        {"name": "Motion Lab Therapy", "type": "Dance Medicine", "location": f"Nearby {location}", "phone": "(555) 014-3322", "map_url": "https://maps.google.com"}
    ]
    return jsonify({"directory": directory})


def is_medical_request(message):
    text = (message or '').lower()
    if not text:
        return False

    medical_markers = [
        'injury', 'pain', 'sprain', 'strain', 'fracture', 'swelling', 'soreness', 'aches',
        'twist', 'tendon', 'muscle', 'knee', 'ankle', 'hip', 'back', 'shoulder', 'wrist',
        'leg', 'foot', 'shin', 'calf', 'hip flexor', 'numbness', 'burning', 'bruise', 'treatment',
        'rehab', 'therapy', 'doctor', 'urgent', 'medical', 'imaging', 'dislocated', 'stiffness'
    ]
    return any(marker in text for marker in medical_markers)


def extract_pain_level(message):
    text = (message or '').lower()
    for level in range(10, 0, -1):
        patterns = [f'{level}/10', f'level {level}', f'{level} out of 10', f'{level} pain', f'pain is {level}']
        if any(pattern in text for pattern in patterns):
            return level
    if 'mild' in text:
        return 3
    if 'moderate' in text:
        return 5
    if 'severe' in text or 'sharp' in text or 'excruciating' in text:
        return 8
    return None


def detect_injury_area(message):
    text = (message or '').lower()
    mapping = {
        'ankle': ['ankle', 'ankle pain', 'outside ankle', 'inside ankle'],
        'knee': ['knee', 'kneecap', 'patella', 'inside knee', 'outside knee'],
        'hip': ['hip', 'hip flexor', 'groin', 'glute', 'buttock'],
        'back': ['back', 'lower back', 'lumbar', 'spine'],
        'shoulder': ['shoulder', 'rotator cuff', 'arm', 'upper arm'],
        'foot': ['foot', 'arch', 'heel', 'toe', 'metatarsal'],
        'shin': ['shin', 'shin splint', 'front lower leg'],
        'calf': ['calf', 'calves'],
        'hamstring': ['hamstring', 'back of thigh'],
        'quad': ['quad', 'quadriceps', 'front thigh']
    }
    for area, keywords in mapping.items():
        if any(keyword in text for keyword in keywords):
            return area
    return 'general'


def build_medical_context(message):
    knowledge = load_recovery_knowledge()
    text = (message or '').strip()
    area = detect_injury_area(text)
    injury_info = knowledge.get('injuries', {}).get(area, knowledge.get('injuries', {}).get('general', {}))
    pain_level = extract_pain_level(text)

    treatment = list(injury_info.get('treatment', []))
    pt_exercises = list(injury_info.get('pt_exercises', []))
    strengthening = list(injury_info.get('strengthening', []))
    links = list(injury_info.get('helpful_links', [])) + list(knowledge.get('links', []))

    if pain_level is not None:
        if pain_level >= 7:
            treatment.insert(0, 'Reduce dancing and avoid jumping, pivoting, or impact loading until pain settles and your mobility is normal.')
        elif pain_level >= 4:
            treatment.insert(0, 'Modify your class or rehearsal volume and keep movement pain-free while you rebuild control.')
        else:
            treatment.insert(0, 'Keep the area moving gently and avoid any movement that sharpens the pain or causes swelling.')

    if area == 'general':
        answer = 'I can help narrow this down by location, pain level, and what makes it worse. If it hurts during jumps, landings, or turns, I can suggest a plan for recovery and strengthening.'
    else:
        answer = f'I would treat this as a {area}-focused recovery issue and focus on reducing irritating load, restoring pain-free motion, and rebuilding strength in the surrounding muscles.'

    return {
        'disclaimer': 'This is general information, not a diagnosis. An AI system is not a medical doctor.',
        'observation': f"The message suggests a {area} issue with pain level {pain_level if pain_level else 'not specified'} and timing that should be considered when planning recovery.",
        'answer': answer,
        'first_aid': [
            'Stop the activity that aggravates the pain.',
            'Use a wrapped cold pack for 10-20 minutes if there is swelling or heat.',
            'Protect the region with a brace or support only if it improves comfort and does not limit circulation.'
        ],
        'treatment': treatment[:5],
        'pt_exercises': pt_exercises[:5],
        'strengthening': strengthening[:5],
        'warning_signs': [
            'You cannot bear weight or continue a normal dance step.',
            'There is swelling, numbness, tingling, severe weakness, or visible deformity.',
            'The pain is sharp, constant, or getting worse despite rest and modification.'
        ],
        'helpful_links': links[:5],
        'follow_up_questions': [
            'Where exactly is the pain, and when does it happen: during jumps, turns, stretching, or at rest?',
            'How long have you had it, and what is the pain level from 1 to 10?',
            'Is it swollen, weak, or limited in range of motion?'
        ],
        'return_to_dance': injury_info.get('return_to_dance', 'Return to full dance only when the area is pain-free in rehearsal and you can complete the movement pattern without compensation.'),
    }


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get('message', '')
    image_data = data.get('image', None)
    history = data.get('history', []) if isinstance(data.get('history', []), list) else []

    if not user_message and not image_data:
        return jsonify({'reply': 'Please provide a message or an image.'}), 400

    medical_mode = bool(image_data) or is_medical_request(user_message)

    if client is None:
        fallback_reply = build_chat_fallback(user_message, medical_mode)
        return jsonify({'reply': fallback_reply, 'is_json': False, 'service_notice': 'Live AI is unavailable right now.'})

    if medical_mode:
        medical_context = json.dumps(build_medical_context(user_message), ensure_ascii=False)
        system_instruction = (
            "You are DanceGuard AI, a friendly AI assistant for dancers. You are not a doctor. "
            "You are a helpful chat assistant. "
            f"Use this recovery context for the answer: {medical_context}"
        )
    else:
        system_instruction = (
            "You are DanceGuard AI, a warm and helpful dance coach and conversational assistant. "
        )

    messages = [{"role": "system", "content": system_instruction}]

    for msg in history:
        if not isinstance(msg, dict):
            continue
        role = "assistant" if msg.get("role") == "assistant" else "user"
        messages.append({"role": role, "content": msg.get("content", "")})

    if image_data:
        user_content = [
            {"type": "text", "text": user_message},
            {"type": "image_url", "image_url": {"url": image_data}}
        ]
        model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
    else:
        user_content = user_message
        model_name = "openai/gpt-oss-120b"

    messages.append({"role": "user", "content": user_content})

    try:
        response_kwargs = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.9 if not medical_mode else 0.3,
            "max_tokens": 420,
        }

        completion = client.chat.completions.create(**response_kwargs)
        ai_reply = completion.choices[0].message.content.strip()
        return jsonify({'reply': ai_reply, 'is_json': False})

    except Exception as e:
        print(f"Groq API Error: {e}")
        fallback_reply = build_chat_fallback(user_message, medical_mode)
        return jsonify({'reply': fallback_reply, 'is_json': False, 'service_notice': 'Live AI is temporarily unavailable.'})


def build_chat_fallback(user_message, medical_mode=False):
    """Keep the assistant useful when the external model cannot be reached."""
    if medical_mode:
        medical_context = build_medical_context(user_message)
        treatment = medical_context['treatment'][0] if medical_context['treatment'] else 'Reduce load and keep the area pain-free.'
        follow_up = medical_context['follow_up_questions'][0] if medical_context['follow_up_questions'] else 'Where exactly is it hurting and when does it happen?'
        return (
            f"I’m a DanceGuard AI assistant, not a doctor. {medical_context['answer']} "
            f"{treatment} A simple next step is to keep the area moving in a pain-free range and avoid impact or deep loading. "
            f"Try a gentle PT cue like controlled mobility or single-leg balance work, then rebuild strength gradually. "
            f"{follow_up} If the pain is severe, you cannot bear weight, there is major swelling, numbness, or it keeps getting worse, seek medical help right away."
        )

    return (
        f"I can help with that. For a practical answer, start with the basics: define the goal, check your form, and keep the movement controlled. "
        f"If you want, I can help with dance technique, practice planning, motivation, stretching, or general performance questions."
    )

@app.route('/api/generate-routine', methods=['POST'])
def generate_routine():
    data = request.json or {}
    routine_type = data.get('type')  # 'warmup' or 'cooldown'
    duration = int(data.get('duration', 5))  # 5, 10, or 15
    age = int(data.get('age', 15))
    style = data.get('dance_style', 'ballet')
    is_challenge = parse_bool(data.get('challenge_mode', False))

    routine = build_routine(routine_type, duration, age, style, is_challenge) if routine_type == 'warmup' else build_routine('cooldown', duration)
    return jsonify({"routine": routine, "total_duration": duration})

if __name__ == '__main__':
    app.run(debug=True)