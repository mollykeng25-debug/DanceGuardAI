import json
from app import app, PROFILE_FILE

original = PROFILE_FILE.read_text(encoding='utf-8') if PROFILE_FILE.exists() else None
try:
    if PROFILE_FILE.exists():
        PROFILE_FILE.unlink()
    with app.test_client() as c:
        r = c.get('/')
        print('LANDING_NO_PROFILE', r.status_code, getattr(r, 'location', ''))
        r = c.get('/survey')
        print('SURVEY_NO_PROFILE', r.status_code, getattr(r, 'location', ''))

    PROFILE_FILE.write_text(json.dumps({'name': 'Test User'}), encoding='utf-8')
    with app.test_client() as c:
        r = c.get('/')
        print('LANDING_WITH_PROFILE', r.status_code, getattr(r, 'location', ''))
        r = c.get('/survey')
        print('SURVEY_WITH_PROFILE', r.status_code, getattr(r, 'location', ''))
        r = c.post('/api/chat', json={'message': 'Hi there! How are you doing?', 'history': []})
        payload = r.get_json()
        print('GENERAL_CHAT', r.status_code, payload.get('is_json'), str(payload.get('reply', ''))[:120])
        r = c.post('/api/chat', json={'message': 'My ankle hurts after dancing.', 'history': []})
        payload = r.get_json()
        print('INJURY_CHAT', r.status_code, payload.get('is_json'), str(payload.get('reply', ''))[:120])
finally:
    if original is None:
        if PROFILE_FILE.exists():
            PROFILE_FILE.unlink()
    else:
        PROFILE_FILE.write_text(original, encoding='utf-8')
