/* Public-site configuration renderer. Keeps static pages aligned with admin data. */
(async () => {
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
      // Keep a locally known session when the optional validation request is unavailable.
      return true;
    }
  };
  const isProfileItem = item => /个人中心/.test(item.title || '') || /\/profile\.html(?:$|[?#])/.test(item.link || '');
  try {
    const [config, navigation, content, authenticated] = await Promise.all([get('/config'), get('/navigation'), get('/content'), hasValidSession()]);
    // The site-level SEO title belongs to the landing page; marketplace, detail,
    // documentation, and account pages maintain their own descriptive titles.
    if (/\/(?:apehub-web\/)?(?:index\.html)?$/.test(window.location.pathname)) {
      document.title = config.seo_title || config.site_name || document.title;
    }
    document.querySelectorAll('link[rel="icon"]').forEach((icon) => { icon.href = config.site_icon || config.site_logo; });
    document.querySelectorAll('.brand img, .modal-logo img').forEach((image) => { image.src = config.site_logo || image.src; });
    document.querySelectorAll('.nav-links').forEach((container) => {
      const visibleNavigation = authenticated ? navigation : navigation.filter(item => !isProfileItem(item));
      container.replaceChildren(...visibleNavigation.map(createNavLink));
    });
    document.querySelectorAll('[data-profile-nav]').forEach(link => { link.hidden = !authenticated; link.style.display = authenticated ? '' : 'none'; });
    document.querySelectorAll('.account-link, #navProfileBtn').forEach(link => { link.hidden = !authenticated; });
    document.querySelectorAll('#navLoginBtn').forEach(link => { link.hidden = authenticated; });
    const hero = content.hero && content.hero[0];
    if (hero?.image) document.querySelectorAll('img[src*="screenshot.png"]').forEach((image) => { image.src = hero.image; });
  } catch (error) {
    console.warn('Apehub_web public configuration unavailable', error);
  }
})();
