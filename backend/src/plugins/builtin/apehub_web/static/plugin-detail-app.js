/* ApeHub plugin detail page — fully config-driven.
 *
 * Layout copy, section visibility, tab labels and float actions are read from
 * the admin-editable `plugin_detail_config` JSON (see Config.vue). Any value
 * missing from the config falls back to a sane default so the page always
 * renders.
 */
const detailEsc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
const detailToken = () => localStorage.getItem('access_token') || '';
const detailIsImage = value => /^(?:https?:\/\/|\/|data:image\/)/i.test(String(value || '').trim());
const detailPrice = value => Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

let currentPlugin = null;
let pageConfig = {};            // raw plugin_detail_config from /site/public/config
const setEnabled = (el, enabled) => { if (el) el.style.display = enabled ? '' : 'none'; };
const val = (obj, path, fallback) => {
  const parts = String(path).split('.');
  let cur = obj;
  for (const part of parts) {
    if (cur == null || typeof cur !== 'object') return fallback;
    cur = cur[part];
  }
  return cur == null ? fallback : cur;
};

async function detailApi(path, options = {}) {
  const headers = { 'Content-Type':'application/json', ...(options.headers || {}) };
  if (detailToken()) headers.Authorization = `Bearer ${detailToken()}`;
  const response = await fetch(`/api/v1${path}`, { ...options, headers });
  const payload = await response.json();
  if (!response.ok || payload.code !== 200) throw new Error(payload.msg || '请求失败');
  return payload.data;
}

function markdownView(markdown) {
  const text = detailEsc(markdown || '暂无技术文档');
  return text.split('\n').map(line => {
    if (line.startsWith('### ')) return `<h3>${line.slice(4)}</h3>`;
    if (line.startsWith('## ')) return `<h2>${line.slice(3)}</h2>`;
    if (line.startsWith('# ')) return `<h1>${line.slice(2)}</h1>`;
    if (line.startsWith('- ')) return `<li>${line.slice(2)}</li>`;
    if (!line.trim()) return '<br>';
    return `<p>${line}</p>`;
  }).join('');
}

/* ---------------- config-driven page assembly ---------------- */

function applyHeroConfig(plugin) {
  const hero = pageConfig.sections?.hero || {};
  setEnabled(document.querySelector('.hero'), hero.enabled !== false);
  setEnabled(document.querySelector('.breadcrumb'), hero.show_breadcrumb !== false);
  if (hero.show_star === false) setEnabled(document.getElementById('starTag'), false);
  else document.getElementById('starTag').textContent = hero.star_tag_text || '⭐ 精选插件';
  document.getElementById('starTag').style.display = hero.show_star === false ? 'none' : '';
  const meta = document.querySelector('.hero-left .meta');
  if (meta) setEnabled(meta, hero.show_meta !== false);
  if (hero.show_meta === false) {
    const spans = meta?.querySelectorAll('span');
    spans?.forEach(span => { span.style.display = 'none'; });
  }
  setEnabled(document.querySelector('.hero-right'), hero.show_icon !== false);
  setEnabled(document.querySelector('.hero-actions'), hero.show_actions !== false);
}

function applySectionConfig() {
  const sections = pageConfig.sections || {};
  const panelMap = { intro: 'tab-intro', docs: 'tab-docs', demo: 'tab-demo', changelog: 'tab-changelog' };
  for (const [key, panelId] of Object.entries(panelMap)) {
    const cfg = sections[key];
    const panel = document.getElementById(panelId);
    if (!panel) continue;
    const enabled = cfg ? cfg.enabled !== false : true;
    setEnabled(panel, enabled);
    // Section titles / descriptions are configurable.
    if (cfg?.title) {
      const title = panel.querySelector('.sec-title');
      const em = cfg.title_em != null ? `<span class="em">${detailEsc(cfg.title_em)}</span>` : (title?.querySelector('.em')?.outerHTML || '');
      if (title) title.innerHTML = `${detailEsc(cfg.title.replace(cfg.title_em || '', ''))}${em}`;
    }
    if (cfg?.description) {
      const desc = panel.querySelector('.sec-desc');
      if (desc) desc.textContent = cfg.description;
    }
  }
}

function applyTabConfig() {
  const tabs = pageConfig.tabs || {};
  const bar = document.querySelector('.tabs-inner');
  if (!bar) return;
  const buttons = Array.from(bar.querySelectorAll('.tab-btn'));
  // Sort tabs by configured order.
  buttons.sort((a, b) => {
    const ta = tabs[a.dataset.tab]?.sort ?? 999;
    const tb = tabs[b.dataset.tab]?.sort ?? 999;
    return ta - tb;
  });
  buttons.forEach(btn => bar.appendChild(btn));
  // Toggle enabled / custom labels.
  buttons.forEach(btn => {
    const cfg = tabs[btn.dataset.tab];
    if (cfg) {
      btn.style.display = cfg.enabled === false ? 'none' : '';
      if (cfg.label) btn.innerHTML = detailEsc(cfg.label);
    }
  });
  // First visible tab becomes active.
  const visible = buttons.filter(btn => btn.style.display !== 'none');
  if (visible.length) {
    buttons.forEach(btn => btn.classList.remove('active'));
    visible[0].classList.add('active');
    document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.toggle('active', panel.id === `tab-${visible[0].dataset.tab}`));
  }
}

function applyButtonConfig(plugin) {
  const buttons = pageConfig.buttons || {};
  const demoCfg = buttons.demo || {};
  const buyCfg = buttons.buy || {};
  const demoBtn = document.getElementById('demoBtn');
  const buyBtn = document.getElementById('buyBtn');
  if (demoBtn) {
    setEnabled(demoBtn.closest('div[style*="position"]') || demoBtn, demoCfg.enabled !== false);
    if (demoCfg.label) demoBtn.innerHTML = detailEsc(demoCfg.label) + (demoCfg.dropdown !== false ? ' ▾' : '');
    if (demoCfg.style) demoBtn.className = `btn btn-${demoCfg.style} btn-lg`;
  }
  if (buyBtn) {
    setEnabled(buyBtn, buyCfg.enabled !== false);
    const isFree = Number(plugin.price) <= 0;
    if (buyCfg.enabled !== false) {
      const label = isFree
        ? (buyCfg.label_free || '免费下载')
        : (buyCfg.label_paid || `🛒 立即购买`);
      buyBtn.textContent = label;
      if (buyCfg.style) buyBtn.className = `btn btn-${buyCfg.style} btn-lg`;
    }
  }
}

function applyFloatActions() {
  const actions = pageConfig.float_actions || {};
  const buttons = document.querySelectorAll('.float-actions .float-btn');
  buttons.forEach(btn => {
    const key = btn.title;
    const keyMap = { '客服咨询': 'contact', '帮助文档': 'docs', '返回顶部': 'top' };
    const cfgKey = keyMap[key] || key;
    const cfg = actions[cfgKey];
    if (cfg) {
      setEnabled(btn, cfg.enabled !== false);
      if (cfg.icon) btn.textContent = cfg.icon;
      if (cfg.title) btn.title = cfg.title;
    }
  });
}

/* ---------------- data rendering ---------------- */

async function loadDetail() {
  const id = Number(new URLSearchParams(location.search).get('id'));
  if (!id) { location.replace('/apehub-web/plugins.html'); return; }
  try {
    const [plugin, cfg] = await Promise.all([
      detailApi(`/apehub-web/site/public/plugins/${id}`),
      detailApi('/apehub-web/site/public/config'),
    ]);
    pageConfig = cfg.plugin_detail_config || {};
    currentPlugin = plugin;
    renderDetail(plugin);
  } catch (error) {
    document.querySelector('.hero-inner').innerHTML = `<div style="padding:60px 0"><h1>插件无法加载</h1><p>${detailEsc(error.message)}</p><a class="btn btn-primary" href="/apehub-web/plugins.html">返回插件市场</a></div>`;
  }
}

function renderDetail(plugin) {
  const versions = plugin.versions || [];
  const latest = versions[0] || {};
  const ai = latest.analysis_report?.ai || {};
  document.title = `ApeHub · ${plugin.display_name}`;
  const labels = pageConfig.labels || {};
  document.getElementById('pluginName').textContent = plugin.display_name;
  document.getElementById('pluginSub').textContent = `${plugin.category || '插件'} · ${String(plugin.tags || '').replaceAll(',', ' · ')}`;
  document.getElementById('pluginDesc').textContent = plugin.description || '暂无介绍';
  document.getElementById('pluginVer').textContent = `v${plugin.version}`;
  document.getElementById('pluginAuthor').textContent = `${labels.author ? labels.author + ' ' : ''}#${plugin.developer_id}`;
  document.getElementById('pluginDl').textContent = Number(plugin.download_count || 0).toLocaleString();
  document.getElementById('pluginRate').textContent = Number(plugin.rating_avg || 5).toFixed(1);
  document.getElementById('crumbName').textContent = plugin.display_name;
  document.getElementById('heroIcon').innerHTML = detailIsImage(plugin.icon)
    ? `<img src="${detailEsc(plugin.icon)}" alt="${detailEsc(plugin.display_name)}" style="width:100%;height:100%;object-fit:cover;border-radius:24px">`
    : detailEsc(plugin.icon || '插');

  const features = Array.isArray(ai.features) ? ai.features : [];
  document.getElementById('featGrid').innerHTML = features.length ? features.map((feature, index) => `<div class="feat-card"><h4>${index + 1}. ${detailEsc(typeof feature === 'string' ? feature : feature.name || feature.title)}</h4><p>${detailEsc(typeof feature === 'string' ? '' : feature.description || '')}</p></div>`).join('') : `<div class="feat-card"><h4>插件能力</h4><p>${detailEsc(plugin.description)}</p></div>`;

  const shots = (plugin.media || []).filter(item => item.media_type === 'carousel');
  const shotRoot = document.querySelector('.shots');
  shotRoot.innerHTML = shots.length ? shots.map(item => `<figure class="shot"><img src="${detailEsc(item.url)}" alt="${detailEsc(item.alt_text)}" style="width:100%;display:block"><figcaption class="cap">${detailEsc(item.alt_text || plugin.display_name)}</figcaption></figure>`).join('') : '<div class="empty" style="color:var(--text-3)">暂无产品截图</div>';

  const isFree = Number(plugin.price) <= 0;
  const riskMap = { none: '无风险', low: '低', medium: '中', high: '高', critical: '严重' };
  document.querySelector('.tbl-wrap tbody').innerHTML = `<tr><td>当前版本</td><td>v${detailEsc(plugin.version)}</td></tr><tr><td>兼容性</td><td>${detailEsc(latest.compatibility || 'ApeAdmin / FastAPI')}</td></tr><tr><td>文件数</td><td>${latest.analysis_report?.file_count || '-'}</td></tr><tr><td>静态风险级别</td><td>${detailEsc(riskMap[latest.analysis_report?.risk_level] || '未标记')}</td></tr><tr><td>授权</td><td>${isFree ? '免费开源，可自由下载使用' : '购买一次，永久获得该插件全部已发布版本'}</td></tr>`;
  document.getElementById('tab-docs').innerHTML = `<h2 class="sec-title">技术<span class="em">文档</span></h2><div style="max-width:920px;white-space:normal" class="doc-markdown">${markdownView(latest.documentation)}</div>`;
  document.querySelector('.changelog').innerHTML = versions.length ? versions.map(version => `<div class="log-item"><div><div class="ver">v${detailEsc(version.version)}</div><div class="date">${version.published_at ? new Date(version.published_at).toLocaleDateString('zh-CN') : '-'}</div></div><div><p>${detailEsc(version.changelog || '无更新说明')}</p></div></div>`).join('') : '<p>暂无版本记录</p>';

  renderDemos(plugin.demos || []);
  renderBuy(plugin, latest);
  applyHeroConfig(plugin);
  applySectionConfig();
  applyTabConfig();
  applyButtonConfig(plugin);
  applyFloatActions();
  applyLabelConfig();
}

function renderDemos(demos) {
  const dropdown = document.getElementById('demoDropdown');
  dropdown.innerHTML = demos.length ? demos.map(item => `<a href="${detailEsc(item.url || '#')}" target="${item.url ? '_blank' : '_self'}" rel="noopener">${detailEsc(item.title || item.demo_type)}</a>`).join('') : '<a href="#">暂无在线 Demo</a>';
  document.getElementById('demoBtn').disabled = !demos.length;
  document.getElementById('demoBody').innerHTML = demos.length ? `<div class="big-icon">演</div><p>可用 Demo：${demos.map(item => detailEsc(item.title || item.demo_type)).join(' · ')}</p>` : '<div class="big-icon">—</div><p>当前版本未提供在线 Demo</p>';
}

function renderBuy(plugin, latest) {
  const button = document.getElementById('buyBtn');
  button.textContent = Number(plugin.price) > 0 ? `购买 ${detailPrice(plugin.price)} USDT` : '免费下载';
  const modal = document.querySelector('#buyModal .modal');
  modal.innerHTML = `<button class="close-btn" id="buyClose">×</button><h3>${detailEsc(plugin.display_name)}</h3><p class="m-sub">购买一次，永久获得该插件全部已发布版本。</p><div class="price-grid" style="grid-template-columns:1fr"><div class="price-card popular"><div class="p-name">完整插件授权</div><div class="p-price">${Number(plugin.price) > 0 ? detailPrice(plugin.price) : '0.00'}<span class="unit"> USDT / 永久</span></div><ul class="p-features"><li>当前已发布版本 v${detailEsc(plugin.version)}</li><li>后续发布版本</li><li>完整技术文档</li></ul><button class="p-btn pro" id="confirmBuy">${Number(plugin.price) > 0 ? '前往 USDT 支付' : '下载当前版本'}</button></div></div>`;
  document.getElementById('buyClose').addEventListener('click', () => document.getElementById('buyModal').classList.remove('show'));
  document.getElementById('confirmBuy').addEventListener('click', () => purchase(plugin, latest));
}

function applyLabelConfig() {
  const labels = pageConfig.labels || {};
  const meta = document.querySelector('.hero-left .meta');
  if (!meta) return;
  const spans = meta.querySelectorAll('span');
  if (spans[2]) {
    spans[2].innerHTML = `⬇ <span id="pluginDl">${Number(currentPlugin?.download_count || 0).toLocaleString()}</span> ${detailEsc(labels.content || '下载')}`;
  }
  if (labels.rating && spans[3]) {
    spans[3].innerHTML = `★ <span id="pluginRate">${Number(currentPlugin?.rating_avg || 5).toFixed(1)}</span>`;
  }
  if (labels.author && document.getElementById('pluginAuthor')) {
    document.getElementById('pluginAuthor').textContent = `${labels.author} #${currentPlugin?.developer_id}`;
  }
  if (labels.version && document.getElementById('pluginVer')) {
    document.getElementById('pluginVer').textContent = `v${currentPlugin?.version}`;
  }
}

async function purchase(plugin, latest) {
  if (!detailToken()) { alert('请先登录或注册'); location.href = '/apehub-web/index.html'; return; }
  try {
    if (Number(plugin.price) <= 0) {
      const file = (latest.files || []).find(item => item.file_type === 'package');
      if (!file) throw new Error('当前版本暂无可下载文件');
      const response = await fetch(`/api/v1/apehub-web/files/${file.id}/download`, { headers: { Authorization:`Bearer ${detailToken()}` } });
      if (!response.ok) throw new Error('下载失败');
      const url = URL.createObjectURL(await response.blob()); const link = document.createElement('a'); link.href = url; link.download = file.filename; link.click(); URL.revokeObjectURL(url);
    } else {
      const order = await detailApi('/apehub-web/orders/create', { method:'POST', body:JSON.stringify({ plugin_id:plugin.id }) });
      location.assign(order.pay_url);
    }
  } catch (error) { alert(error.message); }
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.tab-btn').forEach(item => item.classList.toggle('active', item === button));
  document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.toggle('active', panel.id === `tab-${button.dataset.tab}`));
}));
const buyModal = document.getElementById('buyModal');
document.getElementById('buyBtn').addEventListener('click', () => buyModal.classList.add('show'));
buyModal.addEventListener('click', event => { if (event.target === buyModal) buyModal.classList.remove('show'); });
const demoButton = document.getElementById('demoBtn'), demoDropdown = document.getElementById('demoDropdown');
demoButton.addEventListener('click', event => { event.stopPropagation(); demoDropdown.classList.toggle('show'); });
document.addEventListener('click', () => demoDropdown.classList.remove('show'));
document.addEventListener('keydown', event => { if (event.key === 'Escape') buyModal.classList.remove('show'); });
loadDetail();