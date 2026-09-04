document.addEventListener("DOMContentLoaded", () => {
  const sidebarHTML = `
    <div id="sidebar-backdrop" aria-hidden="true"></div>
    <button id="app-hamburger" type="button" aria-label="Open navigation" aria-expanded="false">
      <span></span><span></span><span></span>
    </button>
    <aside id="sidebar-panel" aria-label="Sidebar navigation">
      <div class="sidebar-header">
        <div class="sidebar-brand">
          <h2>DanceGuard</h2>
          <p>Recovery Hub</p>
        </div>
      </div>
      <nav class="sidebar-nav">
        <ul>
          <li><a href="/landing">Landing Page</a></li>
          <li><a href="/dance">Practice Studio</a></li>
          <li><a href="/chatbot">AI Assistant</a></li>
          <li><a href="/settings">Settings</a></li>
          <li id="onboarding-sidebar-link"><a href="/survey">Onboarding Survey</a></li>
        </ul>
      </nav>
    </aside>
    <style>
      :root {
        --sidebar-width: 240px;
        --sidebar-bg: linear-gradient(180deg, rgba(22, 36, 49, 0.98), rgba(11, 20, 30, 0.98));
      }

      body {
        padding-left: var(--sidebar-width) !important;
        transition: padding-left 0.25s ease;
      }

      body.sidebar-collapsed {
        padding-left: 0 !important;
      }

      #app-hamburger {
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 220;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 5px;
        border: 1px solid rgba(120, 151, 170, 0.8);
        border-radius: 14px;
        background: linear-gradient(180deg, #213d4f, #122534);
        box-shadow: 0 8px 0 rgba(4, 10, 17, 0.52), 0 12px 26px rgba(2, 6, 18, 0.4), inset 1px 1px 0 rgba(255,255,255,0.14);
        cursor: pointer;
        transition: transform 0.2s ease, filter 0.2s ease;
      }

      #app-hamburger:hover {
        transform: translateY(-1px);
        filter: brightness(1.08);
      }

      #app-hamburger span {
        display: block;
        width: 22px;
        height: 2.5px;
        border-radius: 999px;
        background: #edf6ff;
      }

      #sidebar-backdrop {
        position: fixed;
        inset: 0;
        display: none;
        background: rgba(2, 6, 20, 0.56);
        z-index: 90;
      }

      #sidebar-backdrop.visible {
        display: block;
      }

      #sidebar-panel {
        position: fixed;
        top: 0;
        left: 0;
        width: var(--sidebar-width);
        height: 100vh;
        z-index: 120;
        overflow-y: auto;
        padding: 1rem 0.9rem 1.2rem;
        background: var(--sidebar-bg);
        border-right: 1px solid rgba(131, 163, 182, 0.7);
        box-shadow: 12px 0 30px rgba(2, 6, 18, 0.32), inset -1px 0 0 rgba(255,255,255,0.08);
        transition: transform 0.25s ease;
        box-sizing: border-box;
      }

      #sidebar-panel.collapsed {
        transform: translateX(-100%);
      }

      .sidebar-header {
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 4.25rem 0 1.25rem;
      }

      .sidebar-brand h2 {
        margin: 0;
        font-size: 1.32rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7ee4ee, #f6c75a 82%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        -webkit-text-fill-color: transparent;
      }

      .sidebar-brand p {
        margin: 0.35rem 0 0;
        color: #9bb7c9;
        font-size: 0.65rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
      }

      .sidebar-nav ul {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
      }

      .sidebar-nav a {
        display: flex;
        align-items: center;
        padding: 0.8rem 0.9rem;
        border-radius: 12px;
        border: 1px solid transparent;
        color: #d8ecfb;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.92rem;
        background: linear-gradient(180deg, rgba(27, 47, 60, 0.82), rgba(14, 24, 32, 0.9));
        box-shadow: inset 1px 1px 0 rgba(255,255,255,0.08), inset -1px -1px 0 rgba(0,0,0,0.22);
        transition: transform 0.18s ease, border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
      }

      .sidebar-nav a:hover {
        transform: translateX(2px);
        border-color: rgba(126, 228, 238, 0.5);
        color: #8df0ff;
        background: linear-gradient(180deg, rgba(33, 58, 72, 0.9), rgba(17, 29, 38, 0.98));
      }

      @media (max-width: 900px) {
        body {
          padding-left: 0 !important;
        }

        #app-hamburger {
          top: 0.8rem;
          left: 0.9rem;
        }

        #sidebar-panel {
          width: min(78vw, 260px);
          transform: translateX(-110%);
          box-shadow: 0 12px 30px rgba(0,0,0,0.35);
        }

        #sidebar-panel.sidebar-visible {
          transform: translateX(0);
        }
      }
    </style>
  `;

    document.body.insertAdjacentHTML("afterbegin", sidebarHTML);

    const sidePanel = document.getElementById("sidebar-panel");
    const appHamburger = document.getElementById("app-hamburger");
    const backdrop = document.getElementById("sidebar-backdrop");
    const onboardingLink = document.getElementById("onboarding-sidebar-link");
    const mediaQuery = window.matchMedia("(max-width: 900px)");

    fetch('/api/profile-status')
      .then((response) => response.ok ? response.json() : { has_profile: false })
      .then((data) => {
        if (data.has_profile && onboardingLink) {
          onboardingLink.style.display = 'none';
        }
      })
      .catch(() => {
        if (onboardingLink) onboardingLink.style.display = 'block';
      });

    const updateHamburger = (isOpen) => {
      if (!appHamburger) return;
      appHamburger.setAttribute("aria-expanded", String(isOpen));
    };

    const setDesktopExpanded = (expanded) => {
      document.body.classList.toggle("sidebar-collapsed", !expanded);
      sidePanel.classList.toggle("collapsed", !expanded);
      updateHamburger(expanded);
    };

    const syncSidebar = () => {
      if (mediaQuery.matches) {
        sidePanel.classList.remove("collapsed");
        sidePanel.classList.remove("sidebar-visible");
        backdrop.classList.remove("visible");
        document.body.classList.remove("sidebar-collapsed");
        updateHamburger(false);
      } else {
        setDesktopExpanded(false);
        backdrop.classList.remove("visible");
        sidePanel.classList.remove("sidebar-visible");
      }
    };

    const toggleSidebar = () => {
      if (mediaQuery.matches) {
        const isVisible = sidePanel.classList.contains("sidebar-visible");
        sidePanel.classList.toggle("sidebar-visible", !isVisible);
        backdrop.classList.toggle("visible", !isVisible);
        updateHamburger(!isVisible);
      } else {
        const isCollapsed = sidePanel.classList.contains("collapsed");
        setDesktopExpanded(isCollapsed);
      }
    };

    if (appHamburger) {
      appHamburger.addEventListener("click", toggleSidebar);
    }

    if (backdrop) {
      backdrop.addEventListener("click", () => {
        if (mediaQuery.matches) {
          sidePanel.classList.remove("sidebar-visible");
          backdrop.classList.remove("visible");
          updateHamburger(false);
        }
      });
    }

    document.querySelectorAll(".sidebar-nav a").forEach((link) => {
      link.addEventListener("click", () => {
        if (mediaQuery.matches) {
          sidePanel.classList.remove("sidebar-visible");
          backdrop.classList.remove("visible");
          updateHamburger(false);
        }
      });
    });

    syncSidebar();
    window.addEventListener("resize", syncSidebar);
  });