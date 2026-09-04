(() => {
  const nativeFetch = window.fetch.bind(window);
  const getAccessToken = () => {
    for (let index = 0; index < localStorage.length; index += 1) {
      const key = localStorage.key(index);
      try {
        const session = JSON.parse(localStorage.getItem(key));
        if (session && session.access_token) return session.access_token;
      } catch (error) {}
    }
    return null;
  };

  window.fetch = (input, init = {}) => {
    const token = getAccessToken();
    const url = typeof input === 'string' ? input : input.url;
    const isSameOrigin = url.startsWith('/') || url.startsWith(window.location.origin);
    if (!token || !isSameOrigin) return nativeFetch(input, init);
    const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
    if (!headers.has('Authorization')) headers.set('Authorization', `Bearer ${token}`);
    return nativeFetch(input, { ...init, headers });
  };

  window.addEventListener('load', async () => {
    if (!getAccessToken()) return;
    try {
      const response = await window.fetch('/api/profile');
      if (!response.ok) return;
      const profile = await response.json();
      localStorage.setItem('danceguard_profile_created', 'true');
      localStorage.setItem('danceguard_profile_data', JSON.stringify(profile));
    } catch (error) {}
  });

  const STORAGE_KEY = 'danceguard_theme_preferences';
  const defaults = { mode: 'dark', accent: '#14b8a6' };
  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') || defaults;
  const state = { ...defaults, ...saved };

  const root = document.documentElement;
  const apply = () => {
    root.dataset.theme = state.mode;
    root.style.setProperty('--accent', state.accent);
    root.style.setProperty('--teal', state.accent);
    root.style.setProperty('--teal-glow', state.accent);
    root.style.setProperty('--accent-soft', `${state.accent}26`);
    root.style.setProperty('--accent-glow', state.accent);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  };

  const style = document.createElement('style');
  style.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --accent: #2ec7d7;
      --accent-soft: rgba(46, 199, 215, 0.16);
      --accent-glow: #7ee4ee;
      --bg: #07131d;
      --bg-2: #0e1f2d;
      --panel: #162a38;
      --panel-2: #1d3448;
      --panel-3: #0f1e2b;
      --line: #36516a;
      --line-soft: #4d6f89;
      --text: #edf6ff;
      --text-muted: #aac1d6;
      --success: #2ecb8e;
      --warning: #f5be5b;
      --danger: #ef6c62;
      --shadow-outer: 0 20px 40px rgba(2, 8, 18, 0.6), 0 6px 18px rgba(2, 8, 18, 0.35);
      --shadow-inset: inset 1px 1px 0 rgba(255,255,255,0.12), inset -2px -2px 5px rgba(2, 8, 18, 0.68);
      --shadow-raised: 0 8px 0 rgba(4, 10, 17, 0.52), 0 12px 26px rgba(3, 9, 17, 0.42), inset 1px 1px 0 rgba(255,255,255,0.1);
      --radius-lg: 20px;
      --radius-md: 14px;
      --radius-sm: 10px;
    }

    * {
      box-sizing: border-box;
    }

    html {
      min-height: 100%;
      background: var(--bg);
    }

    body {
      position: relative;
      margin: 0;
      min-height: 100vh;
      overflow-x: hidden;
      background:
        radial-gradient(circle at 15% 10%, rgba(126, 228, 238, 0.12), transparent 26rem),
        radial-gradient(circle at 80% 10%, rgba(245, 190, 91, 0.08), transparent 22rem),
        linear-gradient(160deg, #091722 0%, #0f1f2d 26%, #0b1722 100%);
      color: var(--text);
      font-family: "Plus Jakarta Sans", "Segoe UI", sans-serif;
      letter-spacing: 0.01em;
      line-height: 1.5;
      isolation: isolate;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
      background-size: 32px 32px;
      mask-image: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent 80%);
      z-index: -1;
    }

    h1, h2, h3, .logo, .sidebar-brand h2, .section-title, .card-title, .page-heading h1, .btn, .btn-cta, .nav-btn, .routine-btn, button {
      font-family: "Space Grotesk", "Plus Jakarta Sans", sans-serif;
      letter-spacing: 0.01em;
    }

    h1, h2, h3, .logo, .sidebar-brand h2, .section-title {
      margin: 0;
      font-weight: 800;
      letter-spacing: 0;
    }

    header h1, .page-heading h1, .logo, .hero h1 span, .section-title, .form-card h2, .profile-card h1 {
      background: linear-gradient(135deg, var(--accent-glow), #f6c75a 78%, #f4a261);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
      -webkit-text-fill-color: transparent;
    }

    a, button, input, select, textarea {
      font: inherit;
    }

    nav, header, .glass-card, .form-card, .chat-box, .input-area, .assistant-intro, .theme-panel, #onboarding-modal > div, #sidebar-panel, #app-hamburger, .day-label, .item-box, .msg-ai, .hud, .schedule-banner, .routine-instructions .inner {
      background: linear-gradient(160deg, rgba(32, 48, 62, 0.98), rgba(12, 22, 31, 0.98));
      border: 1px solid var(--line);
      box-shadow: var(--shadow-outer), var(--shadow-inset);
      backdrop-filter: none !important;
      -webkit-backdrop-filter: none !important;
    }

    nav, header {
      background: linear-gradient(180deg, rgba(22, 36, 49, 0.95), rgba(13, 22, 31, 0.98));
    }

    .glass-card, .form-card, .chat-box, .input-area, .assistant-intro {
      border-radius: var(--radius-lg);
    }

    input, select, textarea, .item-box, .msg-ai, .hud, .schedule-banner, .routine-instructions .inner {
      background: linear-gradient(180deg, #0d1925, #101f2d);
      color: var(--text);
      border: 1px solid var(--line);
      box-shadow: inset 3px 3px 7px rgba(0, 0, 0, 0.3), inset -2px -2px 5px rgba(255,255,255,0.03);
    }

    input::placeholder, textarea::placeholder {
      color: rgba(170, 193, 214, 0.9);
    }

    button, .btn, .nav-btn, .btn-cta, .routine-btn, .day-label {
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.8rem 1.1rem;
      border: 1px solid var(--line-soft);
      border-radius: var(--radius-sm);
      color: var(--text);
      cursor: pointer;
      font-weight: 700;
      background: linear-gradient(180deg, #264a63, #132738);
      box-shadow: 0 6px 0 rgba(4, 11, 18, 0.55), inset 1px 1px 0 rgba(255,255,255,0.15), inset -2px -2px 3px rgba(0, 0, 0, 0.36);
      transition: transform 0.16s ease, filter 0.16s ease, box-shadow 0.16s ease;
    }

    button:hover, .btn:hover, .nav-btn:hover, .btn-cta:hover, .routine-btn:hover, .day-label:hover {
      transform: translateY(-1px);
      filter: brightness(1.08);
    }

    button:active, .btn:active, .nav-btn:active, .btn-cta:active, .routine-btn:active, .day-label:active {
      transform: translateY(2px);
      box-shadow: inset 3px 3px 6px rgba(0,0,0,0.34), inset -1px -1px 2px rgba(255,255,255,0.08);
    }

    .btn-cta, .btn-primary, .routine-btn:not(.secondary):not(.coral) {
      background: linear-gradient(180deg, #2ec7d7, #1a9bb0);
      border-color: rgba(126, 228, 238, 0.45);
    }

    .btn-secondary, .nav-btn, .routine-btn.secondary {
      background: linear-gradient(180deg, #243d4f, #162b38);
    }

    .btn-coral, .routine-btn.coral {
      background: linear-gradient(180deg, #ef6c62, #c74a44);
      border-color: rgba(255, 173, 168, 0.45);
    }

    .theme-controls {
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 200;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .profile-link, .theme-toggle, .theme-color {
      display: grid;
      place-items: center;
      width: 2.4rem;
      height: 2.4rem;
      border-radius: 50%;
      border: 1px solid var(--line);
      background: linear-gradient(180deg, #233d4d, #122533);
      color: var(--text);
      box-shadow: var(--shadow-raised), var(--shadow-inset);
      text-decoration: none;
      cursor: pointer;
    }

    .profile-link:hover, .theme-toggle:hover, .theme-color:hover {
      transform: translateY(-1px);
      filter: brightness(1.08);
    }

    .profile-link {
      position: relative;
    }

    .profile-icon {
      display: block;
      position: relative;
      width: 1.15rem;
      height: 1.15rem;
      border-radius: 50%;
      background: rgba(212, 231, 241, 0.9);
    }

    .profile-icon::before {
      content: "";
      position: absolute;
      left: 50%;
      top: 0.18rem;
      width: 0.42rem;
      height: 0.42rem;
      transform: translateX(-50%);
      border-radius: 50%;
      background: #3b4b5a;
    }

    .profile-icon::after {
      content: "";
      position: absolute;
      left: 50%;
      bottom: 0.14rem;
      width: 0.7rem;
      height: 0.42rem;
      transform: translateX(-50%);
      border-radius: 12px 12px 7px 7px;
      background: #3b4b5a;
    }

    .theme-toggle {
      font-size: 1rem;
    }

    .theme-color {
      padding: 0.15rem;
      overflow: hidden;
    }

    .theme-color::-webkit-color-swatch-wrapper {
      padding: 0;
    }

    .theme-color::-webkit-color-swatch {
      border: none;
      border-radius: 50%;
    }

    [data-theme="light"] {
      --bg: #dfe7e5;
      --bg-2: #edf4f2;
      --panel: #e8f0ee;
      --panel-2: #d7e7e6;
      --panel-3: #cfdbd9;
      --line: #b6c9c5;
      --line-soft: #9ab2ad;
      --text: #1b2c31;
      --text-muted: #50656d;
      --shadow-outer: 0 20px 35px rgba(70, 94, 92, 0.16), 0 6px 14px rgba(70, 94, 92, 0.1);
      --shadow-inset: inset 1px 1px 0 rgba(255,255,255,0.95), inset -2px -2px 6px rgba(118, 135, 132, 0.18);
      --shadow-raised: 0 7px 0 rgba(150, 172, 169, 0.55), 0 12px 22px rgba(88, 110, 106, 0.2), inset 1px 1px 0 rgba(255,255,255,0.9);
    }

    [data-theme="light"] body {
      background:
        radial-gradient(circle at 15% 12%, rgba(255,255,255,0.92), transparent 26rem),
        linear-gradient(160deg, #e7f0ed 0%, #d8e7e4 35%, #cadfe1 100%);
      color: var(--text);
    }

    [data-theme="light"] input, [data-theme="light"] select, [data-theme="light"] textarea,
    [data-theme="light"] .item-box, [data-theme="light"] .msg-ai, [data-theme="light"] .hud,
    [data-theme="light"] .schedule-banner, [data-theme="light"] .routine-instructions .inner {
      background: linear-gradient(180deg, #f5faf9, #edf2f1);
      color: var(--text);
    }

    @media (max-width: 720px) {
      .theme-controls {
        top: 0.7rem;
        right: 0.7rem;
      }
    }
  `;
  document.head.appendChild(style);

  apply();

  const controls = document.createElement('div');
  controls.className = 'theme-controls';
  controls.innerHTML = `
    <a class="profile-link" href="/profile" aria-label="Open profile" title="Profile">
      <span class="profile-icon" aria-hidden="true"><span></span></span>
    </a>
    <button class="theme-toggle" type="button" aria-label="Switch to light mode" title="Switch theme"></button>
    <input class="theme-color" type="color" aria-label="Choose accent color" title="Choose accent color">
  `;
  document.body.appendChild(controls);

  const toggle = controls.querySelector('.theme-toggle');
  const color = controls.querySelector('.theme-color');
  const updateToggle = () => {
    const light = state.mode === 'light';
    toggle.textContent = light ? '☀' : '☾';
    toggle.setAttribute('aria-label', light ? 'Switch to dark mode' : 'Switch to light mode');
    color.value = state.accent;
  };
  toggle.addEventListener('click', () => {
    state.mode = state.mode === 'dark' ? 'light' : 'dark';
    apply();
    updateToggle();
  });
  color.addEventListener('input', (event) => {
    state.accent = event.target.value;
    apply();
  });
  updateToggle();
})();
