const detailEsc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
const detailToken = () => localStorage.getItem('access_token') || '';
const detailIsImage = value => /^(?:https?:\/\/|\/|data:image\/)/i.test(String(value || '').trim());
const detailPrice = value => Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
let currentPlugin = null;

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

async function loadDetail() {
  const id = Number(new URLSearchParams(location.search).get('id'));
  if (!id) { location.replace('/apehub-web/plugins.html'); return; }
  try {
    currentPlugin = await detailApi(`/apehub-web/site/public/plugins/${id}`);
    renderDetail(currentPlugin);
  } catch (error) {
    document.querySelector('.hero-inner').innerHTML = `<div style="padding:60px 0"><h1>插件无法加载</h1><p>${detailEsc(error.message)}</p><a class="btn btn-primary" href="/apehub-web/plugins.html">返回插件市场</a></div>`;
  }
}

function renderDetail(plugin) {
  const versions = plugin.versions || [];
  const latest = versions[0] || {};
  const ai = latest.analysis_report?.ai || {};
  document.title = `ApeHub · ${plugin.display_name}`;
  document.getElementById('pluginName').textContent = plugin.display_name;
  document.getElementById('pluginSub').textContent = `${plugin.category || '插件'} · ${String(plugin.tags || '').replaceAll(',', ' · ')}`;
  document.getElementById('pluginDesc').textContent = plugin.description || '暂无介绍';
  document.getElementById('pluginVer').textContent = `v${plugin.version}`;
  document.getElementById('pluginAuthor').textContent = `开发者 #${plugin.developer_id}`;
  document.getElementById('pluginDl').textContent = Number(plugin.download_count || 0).toLocaleString();
  document.getElementById('pluginRate').textContent = Number(plugin.rating_avg || 5).toFixed(1);
  document.getElementById('crumbName').textContent = plugin.display_name;
  document.getElementById('starTag').style.display = 'none';
  document.getElementById('heroIcon').innerHTML = detailIsImage(plugin.icon)
    ? `<img src="${detailEsc(plugin.icon)}" alt="${detailEsc(plugin.display_name)}" style="width:100%;height:100%;object-fit:cover;border-radius:24px">`
    : detailEsc(plugin.icon || '插');

  const features = Array.isArray(ai.features) ? ai.features : [];
  document.getElementById('featGrid').innerHTML = features.length ? features.map((feature, index) => `<div class="feat-card"><h4>${index + 1}. ${detailEsc(typeof feature === 'string' ? feature : feature.name || feature.title)}</h4><p>${detailEsc(typeof feature === 'string' ? '' : feature.description || '')}</p></div>`).join('') : `<div class="feat-card"><h4>插件能力</h4><p>${detailEsc(plugin.description)}</p></div>`;

  const shots = (plugin.media || []).filter(item => item.media_type === 'carousel');
  const shotRoot = document.querySelector('.shots');
  shotRoot.innerHTML = shots.length ? shots.map(item => `<figure class="shot"><img src="${detailEsc(item.url)}" alt="${detailEsc(item.alt_text)}" style="width:100%;display:block"><figcaption class="cap">${detailEsc(item.alt_text || plugin.display_name)}</figcaption></figure>`).join('') : '<div class="empty" style="color:var(--text-3)">暂无产品截图</div>';

  document.querySelector('.tbl-wrap tbody').innerHTML = `<tr><td>当前版本</td><td>v${detailEsc(plugin.version)}</td></tr><tr><td>兼容性</td><td>${detailEsc(latest.compatibility || 'ApeAdmin / FastAPI')}</td></tr><tr><td>文件数</td><td>${latest.analysis_report?.file_count || '-'}</td></tr><tr><td>静态风险级别</td><td>${detailEsc(latest.analysis_report?.risk_level || '未标记')}</td></tr><tr><td>授权</td><td>购买一次，可下载所有已发布版本</td></tr>`;
  document.getElementById('tab-docs').innerHTML = `<h2 class="sec-title">技术<span class="em">文档</span></h2><div style="max-width:920px;white-space:normal" class="doc-markdown">${markdownView(latest.documentation)}</div>`;
  document.querySelector('.changelog').innerHTML = versions.length ? versions.map(version => `<div class="log-item"><div><div class="ver">v${detailEsc(version.version)}</div><div class="date">${version.published_at ? new Date(version.published_at).toLocaleDateString('zh-CN') : '-'}</div></div><div><p>${detailEsc(version.changelog || '无更新说明')}</p></div></div>`).join('') : '<p>暂无版本记录</p>';
  renderDemos(plugin.demos || []);
  renderBuy(plugin, latest);
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

document.querySelectorAll('.tab-btn').forEach(button => button.addEventListener('click', () => { document.querySelectorAll('.tab-btn').forEach(item => item.classList.toggle('active', item === button)); document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.toggle('active', panel.id === `tab-${button.dataset.tab}`)); }));
const buyModal = document.getElementById('buyModal');
document.getElementById('buyBtn').addEventListener('click', () => buyModal.classList.add('show'));
buyModal.addEventListener('click', event => { if (event.target === buyModal) buyModal.classList.remove('show'); });
const demoButton = document.getElementById('demoBtn'), demoDropdown = document.getElementById('demoDropdown');
demoButton.addEventListener('click', event => { event.stopPropagation(); demoDropdown.classList.toggle('show'); });
document.addEventListener('click', () => demoDropdown.classList.remove('show'));
document.addEventListener('keydown', event => { if (event.key === 'Escape') buyModal.classList.remove('show'); });
loadDetail();
