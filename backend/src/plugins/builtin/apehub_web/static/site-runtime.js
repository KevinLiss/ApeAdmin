/* Public-site runtime: shared navigation, theme sync, session state, and mobile menu. */
(() => {
  /* ---------- Theme ---------- */
  const root = document.documentElement;
  const savedTheme = localStorage.getItem('ape-theme') || 'dark';
  root.setAttribute('data-theme', savedTheme);

  function updateToggleIcons() {
    const theme = root.getAttribute('data-theme') || 'dark';
    document.querySelectorAll('#themeToggle').forEach(btn => {
      if (btn) btn.textContent = theme === 'dark' ? '🌙' : '☀️';
    });
  }

  function toggleTheme() {
    const current = root.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('ape-theme', next);
    updateToggleIcons();
    // Sync with VitePress if present
    try {
      const vpKey = 'vitepress-theme-appearance';
      if (next === 'dark') {
        root.classList.remove('light');
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
        root.classList.add('light');
      }
      localStorage.setItem(vpKey, next);
    } catch {}
  }

  // Apply theme immediately (before async init to prevent flash)
  updateToggleIcons();
  // Bind theme toggle buttons (after DOM is ready)
  document.addEventListener('DOMContentLoaded', () => {
    updateToggleIcons();
    document.querySelectorAll('#themeToggle').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });

    /* ---------- Mobile menu ---------- */
    document.querySelectorAll('#menuToggle').forEach(toggle => {
      toggle.addEventListener('click', () => {
        const links = toggle.closest('nav')?.querySelector('.nav-links');
        if (!links) return;
        const visible = links.style.display === 'flex';
        links.style.display = visible ? 'none' : 'flex';
        links.style.flexDirection = visible ? '' : 'column';
        links.style.position = visible ? '' : 'absolute';
        links.style.top = visible ? '' : '68px';
        links.style.left = visible ? '' : '0';
        links.style.right = visible ? '' : '0';
        links.style.background = visible ? '' : 'var(--bg-soft, #0c0e1a)';
        links.style.padding = visible ? '' : '20px 24px';
        links.style.borderBottom = visible ? '' : '1px solid var(--panel-border, rgba(255,255,255,.08))';
        links.style.gap = visible ? '' : '18px';
        links.style.alignItems = visible ? '' : 'flex-start';
        links.style.zIndex = visible ? '' : '99';
      });
    });
    window.addEventListener('resize', () => {
      if (window.innerWidth > 900) {
        document.querySelectorAll('nav .nav-links').forEach(links => {
          links.style.display = 'flex';
          links.style.flexDirection = '';
          links.style.position = '';
          links.style.top = '';
          links.style.left = '';
          links.style.right = '';
          links.style.background = '';
          links.style.padding = '';
          links.style.borderBottom = '';
          links.style.gap = '';
          links.style.alignItems = '';
          links.style.zIndex = '';
        });
      }
    });
  });

  /* ---------- Auth & Navigation ---------- */
  const api = '/api/v1/apehub-web/site/public';
  const get = async (path) => {
    const response = await fetch(`${api}${path}`);
    const payload = await response.json();
    if (!response.ok || payload.code !== 200) throw new Error(payload.msg || 'request failed');
    return payload.data;
  };
  const createNavLink = (item) => {
    const link = document.createElement('a');
    link.href = item.link;
    link.textContent = item.title;
    if (item.open_mode === 'new') { link.target = '_blank'; link.rel = 'noopener'; }
    if (item.icon_url) {
      const icon = document.createElement('img');
      icon.src = item.icon_url; icon.alt = '';
      icon.style.cssText = 'width:16px;height:16px;object-fit:contain;vertical-align:-3px;margin-right:5px';
      link.prepend(icon);
    }
    const target = new URL(link.href, window.location.origin);
    if (target.pathname === window.location.pathname) link.classList.add('active');
    return link;
  };
  const hasValidSession = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return false;
    try {
      const response = await fetch('/api/v1/auth/userinfo', { headers: { Authorization: `Bearer ${token}` } });
      const payload = await response.json();
      if (!response.ok || payload.code !== 200) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return false;
      }
      return true;
    } catch {
      return false;
    }
  };
  const style = document.createElement('style');
  style.textContent = '[hidden]{display:none!important}';
  document.head.prepend(style);
  const isProfileItem = item => /个人中心/.test(item.title || '') || /\/profile\.html(?:$|[?#])/.test(item.link || '');
  (async () => {
    try {
      const [config, navigation, content, authenticated] = await Promise.all([get('/config'), get('/navigation'), get('/content'), hasValidSession()]);
      if (/\/(?:apehub-web\/)?(?:index\.html)?$/.test(window.location.pathname)) {
        document.title = config.seo_title || config.site_name || document.title;
      }
      document.querySelectorAll('link[rel="icon"]').forEach((icon) => { icon.href = config.site_icon || config.site_logo; });
      document.querySelectorAll('.brand img, .modal-logo img').forEach((image) => { image.src = config.site_logo || image.src; });
      document.querySelectorAll('.nav-links').forEach((container) => {
        const visibleNavigation = authenticated ? navigation : navigation.filter(item => !isProfileItem(item));
        container.replaceChildren(...visibleNavigation.map(createNavLink));
      });
      // Show/hide profile and login buttons consistently across all pages
      document.querySelectorAll('[data-profile-nav]').forEach(link => { link.hidden = !authenticated; link.style.display = authenticated ? '' : 'none'; });
      document.querySelectorAll('.account-link, #navProfileBtn').forEach(link => { link.hidden = !authenticated; link.style.display = authenticated ? '' : 'none'; });
      document.querySelectorAll('#navLoginBtn').forEach(link => { link.hidden = authenticated; link.style.display = authenticated ? 'none' : ''; });
      const hero = content.hero && content.hero[0];
      if (hero?.image) document.querySelectorAll('img[src*="screenshot.png"]').forEach((image) => { image.src = hero.image; });
    } catch (error) {
      console.warn('Apehub_web public configuration unavailable', error);
    }
  })();
})();
