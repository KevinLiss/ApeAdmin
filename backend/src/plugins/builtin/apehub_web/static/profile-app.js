const API = '/api/v1';
const state = { token: localStorage.getItem('access_token') || '', profile: null, config: null, plugins: [], selectedPlugin: null, selectedVersion: null, analysisTimer: null };
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
const money = (value) => Number(value || 0).toFixed(2).replace(/\.00$/, '');
const isImage = (value) => /^(?:https?:\/\/|\/|data:image\/)/i.test(String(value || '').trim());
const date = (value) => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-';
const statusText = (value) => ({ draft:'草稿', analyzing:'AI 分析中', analysis_failed:'分析失败', submitted:'待审核', reviewing:'审核中', approved:'已通过', published:'已发布', rejected:'已驳回', deprecated:'历史版本', pending:'待处理', paid:'已支付', refunded:'已退款', available:'可提现', done:'已完成', offline:'已下架' }[value] || value || '-');

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  const response = await fetch(API + path, { ...options, headers });
  let payload = null;
  try { payload = await response.json(); } catch { payload = null; }
  if (!response.ok || (payload && payload.code && payload.code !== 200)) {
    if (response.status === 401) logout(false);
    throw new Error(payload?.msg || `请求失败 (${response.status})`);
  }
  return payload?.data ?? payload;
}

function toast(message, error = false) {
  const el = $('#toast');
  el.textContent = message;
  el.className = `toast show${error ? ' error' : ''}`;
  clearTimeout(el.timer);
  el.timer = setTimeout(() => el.className = 'toast', 3200);
}

function logout(reload = true) {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  state.token = '';
  if (reload) location.reload();
}

async function init() {
  try { state.config = await api('/apehub-web/site/public/config'); } catch { state.config = {}; }
  if (!state.token) {
    $('#authGate').hidden = false;
    $('#logoutBtn').hidden = true;
    return;
  }
  $('#logoutBtn').hidden = false;
  $('#app').hidden = false;
  await refreshAll();
}

async function refreshAll() {
  try {
    const [profile, purchased, plugins, incomes, withdrawals, wallet] = await Promise.all([
      api('/apehub-web/profile'), api('/apehub-web/orders/my/paid'), api('/apehub-web/developer/plugins'),
      api('/apehub-web/incomes'), api('/apehub-web/withdrawals'), api('/apehub-web/wallet'),
    ]);
    state.profile = profile;
    state.plugins = plugins || [];
    renderProfile();
    renderPurchased(purchased || []);
    renderPlugins();
    renderIncomes(incomes || []);
    renderWallet(wallet, withdrawals || []);
  } catch (error) { toast(error.message, true); }
}

function renderProfile() {
  const p = state.profile;
  $('#userName').textContent = p.nickname || p.username;
  $('#profileName').textContent = p.nickname || p.username;
  $('#profileMeta').textContent = p.is_developer ? '开发者账户' : '注册用户';
  $('#statBalance').textContent = `${money(p.balance)} USDT`;
  $('#statFrozen').textContent = `${money(p.frozen_balance)} USDT`;
  $('#statIncome').textContent = `${money(p.total_income)} USDT`;
  $('#statPlugins').textContent = String(state.plugins.length);
}

function renderPurchased(items) {
  $('#purchasedBody').innerHTML = items.length ? items.map(item => {
    const files = (item.files || []).map(file => `<button class="btn btn-small" data-download="${file.id}" data-name="${esc(file.filename)}">${esc(file.version || item.version)} 下载</button>`).join(' ');
    return `<tr><td><strong>${esc(item.display_name)}</strong><br><span class="muted">${esc(item.name)}</span></td><td>${esc(item.version)}</td><td>${money(item.price)} USDT</td><td><span class="status paid">永久授权</span></td><td>${files || '-'}</td></tr>`;
  }).join('') : '<tr><td colspan="5" class="empty">暂无已购插件</td></tr>';
  document.querySelectorAll('[data-download]').forEach(button => button.addEventListener('click', () => downloadFile(button.dataset.download, button.dataset.name)));
}

async function downloadFile(id, filename) {
  try {
    const response = await fetch(`${API}/apehub-web/files/${id}/download`, { headers: { Authorization: `Bearer ${state.token}` } });
    if (!response.ok) throw new Error('下载失败');
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement('a'); link.href = url; link.download = filename || 'plugin.zip'; link.click();
    URL.revokeObjectURL(url);
  } catch (error) { toast(error.message, true); }
}

function renderPlugins() {
  $('#pluginList').innerHTML = state.plugins.length ? state.plugins.map(plugin => `<button class="plugin-row${state.selectedPlugin?.id === plugin.id ? ' active' : ''}" data-plugin="${plugin.id}"><strong>${esc(plugin.display_name)}</strong><span>${esc(plugin.version)} · ${statusText(plugin.status)} · ${money(plugin.price)} USDT</span></button>`).join('') : '<div class="empty">还没有插件草稿</div>';
  document.querySelectorAll('[data-plugin]').forEach(button => button.addEventListener('click', () => selectPlugin(Number(button.dataset.plugin))));
}

async function selectPlugin(id) {
  try {
    state.selectedPlugin = await api(`/apehub-web/developer/plugins/${id}`);
    state.selectedVersion = state.selectedPlugin.versions?.[0] || null;
    renderPlugins();
    renderWorkbench();
  } catch (error) { toast(error.message, true); }
}

function renderWorkbench() {
  const root = $('#workbench');
  const plugin = state.selectedPlugin;
  if (!plugin) { root.innerHTML = '<div class="workbench-empty">选择左侧插件进入版本工作台</div>'; return; }
  root.innerHTML = `
    <div class="plugin-meta"><img src="${esc(isImage(plugin.icon) ? plugin.icon : '/apehub-web/assets/logo.png')}" alt="${esc(plugin.display_name)}"><div><h2>${esc(plugin.display_name)}</h2><p>${esc(plugin.name)} · ${money(plugin.price)} USDT · ${statusText(plugin.status)}</p></div></div>
    <div class="block"><h3>市场图片</h3><div class="media-grid"><div class="upload-box"><span>插件 Logo</span><label class="btn btn-small">选择图片<input id="logoFile" type="file" accept="image/png,image/jpeg,image/gif,image/webp" hidden></label></div><div class="upload-box"><span>轮播图（可多次上传）</span><label class="btn btn-small">选择图片<input id="carouselFile" type="file" accept="image/png,image/jpeg,image/gif,image/webp" hidden></label></div></div></div>
    <div class="block"><div class="section-head"><h3>版本树</h3><button class="btn btn-small" id="newVersionBtn">新建版本</button></div><div class="version-layout"><div class="version-tree">${(plugin.versions || []).map(version => `<button data-version="${version.id}" class="${state.selectedVersion?.id === version.id ? 'active' : ''}"><strong>${esc(version.version)}</strong><br><span class="status ${esc(version.status)}">${statusText(version.status)}</span></button>`).join('') || '<div class="empty">暂无版本</div>'}</div><div class="version-detail" id="versionDetail"></div></div></div>`;
  $('#logoFile').addEventListener('change', event => uploadMedia(event.target.files[0], 'logo'));
  $('#carouselFile').addEventListener('change', event => uploadMedia(event.target.files[0], 'carousel'));
  $('#newVersionBtn').addEventListener('click', () => $('#versionDialog').showModal());
  document.querySelectorAll('[data-version]').forEach(button => button.addEventListener('click', () => {
    state.selectedVersion = plugin.versions.find(item => item.id === Number(button.dataset.version)); renderWorkbench();
  }));
  renderVersionDetail();
}

function renderVersionDetail() {
  const root = $('#versionDetail');
  const version = state.selectedVersion;
  if (!root) return;
  if (!version) { root.innerHTML = '<div class="empty">请选择版本</div>'; return; }
  const editable = ['draft', 'rejected', 'analysis_failed'].includes(version.status);
  const files = (version.files || []).map(file => `${esc(file.filename)} (${Math.ceil(file.size / 1024)} KB)`).join(', ') || '未上传安装包';
  const report = version.analysis_report;
  root.innerHTML = `
    <div class="version-head"><h4>${esc(version.version)}</h4><span class="status ${esc(version.status)}">${statusText(version.status)}</span></div>
    <div class="field"><label>更新说明</label><textarea id="versionChangelog" ${editable ? '' : 'disabled'}>${esc(version.changelog || '')}</textarea></div>
    <div class="field"><label>技术文档（Markdown）</label><textarea id="versionDocs" style="min-height:260px" ${editable ? '' : 'disabled'}>${esc(version.documentation || '')}</textarea></div>
    <div class="analysis"><strong>安装包：</strong>${files}<br><strong>静态风险：</strong>${esc(report?.risk_level || '尚未分析')} · ${report?.file_count || 0} 个文件${version.reject_reason ? `<br><strong>驳回原因：</strong>${esc(version.reject_reason)}` : ''}<div id="analysisProgress"></div></div>
    <div class="actions">${editable ? `<label class="btn btn-small">上传 ZIP<input id="packageFile" type="file" accept=".zip,application/zip" hidden></label><button class="btn btn-small" id="saveVersion">保存文档</button><button class="btn btn-small" id="analyzeVersion">AI 自动分析</button><button class="btn btn-primary btn-small" id="submitVersion">提交审核</button>` : ''}</div>`;
  if (!editable) return;
  $('#packageFile').addEventListener('change', event => uploadPackage(event.target.files[0]));
  $('#saveVersion').addEventListener('click', saveVersion);
  $('#analyzeVersion').addEventListener('click', analyzeVersion);
  $('#submitVersion').addEventListener('click', submitVersion);
}

async function uploadMedia(file, mediaType) {
  if (!file || !state.selectedPlugin) return;
  const form = new FormData(); form.append('file', file);
  try {
    await api(`/apehub-web/developer/plugins/${state.selectedPlugin.id}/media/upload?media_type=${mediaType}`, { method:'POST', body:form });
    toast('图片上传成功'); await selectPlugin(state.selectedPlugin.id);
  } catch (error) { toast(error.message, true); }
}

async function uploadPackage(file) {
  if (!file || !state.selectedPlugin || !state.selectedVersion) return;
  const form = new FormData(); form.append('file', file);
  try {
    await api(`/apehub-web/developer/plugins/${state.selectedPlugin.id}/files?file_type=package&version_id=${state.selectedVersion.id}`, { method:'POST', body:form });
    toast('安装包校验并上传成功'); await selectPlugin(state.selectedPlugin.id);
  } catch (error) { toast(error.message, true); }
}

async function saveVersion() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  try {
    await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}`, { method:'PUT', body:JSON.stringify({ changelog:$('#versionChangelog').value, documentation:$('#versionDocs').value }) });
    toast('版本资料已保存'); await selectPlugin(plugin.id);
  } catch (error) { toast(error.message, true); }
}

async function analyzeVersion() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  try {
    await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/analyze`, { method:'POST' });
    toast('AI 分析已开始'); pollAnalysis(plugin.id, version.id);
  } catch (error) { toast(error.message, true); }
}

async function pollAnalysis(pluginId, versionId) {
  clearTimeout(state.analysisTimer);
  try {
    const data = await api(`/apehub-web/developer/plugins/${pluginId}/versions/${versionId}/analysis`);
    const progress = $('#analysisProgress');
    if (progress && data.job) progress.innerHTML = `<p>${esc(data.job.stage)} · ${data.job.progress}%</p><progress max="100" value="${data.job.progress}"></progress>${data.job.error ? `<p>${esc(data.job.error)}</p>` : ''}`;
    if (['queued','running'].includes(data.job?.status)) state.analysisTimer = setTimeout(() => pollAnalysis(pluginId, versionId), 1800);
    else { await selectPlugin(pluginId); toast(data.job?.status === 'succeeded' ? 'AI 文档已生成' : (data.job?.error || 'AI 分析失败'), data.job?.status !== 'succeeded'); }
  } catch (error) { toast(error.message, true); }
}

async function submitVersion() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  try {
    await saveVersion();
    await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/submit`, { method:'POST' });
    toast('版本已提交审核'); await selectPlugin(plugin.id); await refreshPlugins();
  } catch (error) { toast(error.message, true); }
}

async function refreshPlugins() {
  state.plugins = await api('/apehub-web/developer/plugins'); renderPlugins();
}

function renderIncomes(items) {
  $('#incomeBody').innerHTML = items.length ? items.map(item => `<tr><td>${esc(item.plugin_name)}</td><td>${money(item.amount)} USDT</td><td>${money(item.rate)}%</td><td><span class="status ${esc(item.status)}">${statusText(item.status)}</span></td><td>${date(item.available_at)}</td></tr>`).join('') : '<tr><td colspan="5" class="empty">暂无销售收益</td></tr>';
}

function feeFor(amount) {
  const cfg = state.config || {}, value = Number(cfg.withdrawal_fee_value || 0);
  return cfg.withdrawal_fee_type === 'percent' ? amount * value / 100 : value;
}

function renderWallet(wallet, withdrawals) {
  $('#walletAddress').value = wallet?.address || '';
  $('#withdrawAddress').value = wallet?.address || '';
  $('#withdrawRule').textContent = `最低提现 ${money(state.config?.min_withdrawal || 100)} USDT · 手续费 ${state.config?.withdrawal_fee_type === 'percent' ? `${money(state.config?.withdrawal_fee_value)}%` : `${money(state.config?.withdrawal_fee_value)} USDT`}`;
  $('#withdrawBody').innerHTML = withdrawals.length ? withdrawals.map(item => `<tr><td>${money(item.amount)} USDT</td><td>${money(item.fee)} USDT</td><td>${money(item.net_amount)} USDT</td><td title="${esc(item.account)}">${esc(item.account.slice(0,8))}...${esc(item.account.slice(-6))}</td><td><span class="status ${esc(item.status)}">${statusText(item.status)}</span></td><td>${esc(item.tx_hash || '-')}</td></tr>`).join('') : '<tr><td colspan="6" class="empty">暂无提现记录</td></tr>';
  updateFeePreview();
}

function updateFeePreview() {
  const amount = Number($('#withdrawAmount')?.value || 0), fee = Math.min(amount, feeFor(amount));
  if ($('#feePreview')) $('#feePreview').textContent = `手续费 ${money(fee)} USDT，预计到账 ${money(Math.max(0, amount - fee))} USDT`;
}

$('#logoutBtn').addEventListener('click', () => logout());
document.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(item => item.classList.toggle('active', item === button));
  document.querySelectorAll('.panel').forEach(panel => panel.classList.toggle('active', panel.id === `panel-${button.dataset.tab}`));
}));
$('#openPluginDialog').addEventListener('click', () => $('#pluginDialog').showModal());
document.querySelectorAll('[data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
$('#pluginForm').addEventListener('submit', async event => {
  event.preventDefault(); const form = new FormData(event.target);
  try {
    const result = await api('/apehub-web/developer/plugins', { method:'POST', body:JSON.stringify(Object.fromEntries(form.entries())) });
    event.target.reset(); $('#pluginDialog').close(); toast('插件草稿已创建'); await refreshPlugins(); await selectPlugin(result.id);
  } catch (error) { toast(error.message, true); }
});
$('#versionForm').addEventListener('submit', async event => {
  event.preventDefault(); const plugin = state.selectedPlugin; const form = new FormData(event.target);
  try {
    const created = await api(`/apehub-web/developer/plugins/${plugin.id}/versions`, { method:'POST', body:JSON.stringify(Object.fromEntries(form.entries())) });
    event.target.reset(); $('#versionDialog').close(); toast('新版本草稿已创建'); await selectPlugin(plugin.id); state.selectedVersion = state.selectedPlugin.versions.find(item => item.id === created.id) || state.selectedPlugin.versions[0]; renderWorkbench();
  } catch (error) { toast(error.message, true); }
});
$('#saveWallet').addEventListener('click', async () => {
  try { const address = $('#walletAddress').value.trim(); await api('/apehub-web/wallet', { method:'PUT', body:JSON.stringify({ address }) }); $('#withdrawAddress').value = address; toast('TRC20 钱包已保存'); } catch (error) { toast(error.message, true); }
});
$('#withdrawAmount').addEventListener('input', updateFeePreview);
$('#withdrawForm').addEventListener('submit', async event => {
  event.preventDefault();
  try {
    await api('/apehub-web/withdrawals', { method:'POST', body:JSON.stringify({ amount:$('#withdrawAmount').value, account:$('#withdrawAddress').value.trim() }) });
    toast('提现申请已提交'); event.target.reset(); await refreshAll();
  } catch (error) { toast(error.message, true); }
});

init();
