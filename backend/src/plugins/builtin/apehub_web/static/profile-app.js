/* ========== Profile App — ApeHub Developer Center ========== */
const API = '/api/v1';
const state = {
  token: localStorage.getItem('access_token') || '',
  profile: null,
  config: {},
  plugins: [],
  selectedPlugin: null,
  selectedVersion: null,
  analysisTimer: null,
  wallets: [],
  pager: { income: { page: 1, total: 0 }, withdraw: { page: 1, total: 0 }, ledger: { page: 1, total: 0, type: '' } },
  // wizard state
  wizard: { step: 1, plugin: null, version: null, packageFile: null, logoFile: null, carouselFiles: [] },
};
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => document.querySelectorAll(selector);
const esc = (value) => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
const money = (value) => Number(value || 0).toFixed(2).replace(/\.00$/, '');
const isImage = (value) => /^(?:https?:\/\/|\/|data:image\/)/i.test(String(value || '').trim());
const date = (value) => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-';
const statusText = (value) => ({
  draft: '草稿', analyzing: 'AI 分析中', analysis_failed: '分析失败', submitted: '待审核',
  reviewing: '审核中', approved: '已通过', published: '已发布', rejected: '已驳回',
  deprecated: '历史版本', pending: '待处理', paid: '已支付', refunded: '已退款',
  available: '可提现', done: '已完成', offline: '已下架', approved_pay: '已通过'
}[value] || value || '-');

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
    const [profile, purchased, plugins] = await Promise.all([
      api('/apehub-web/profile'),
      api('/apehub-web/orders/my/paid'),
      api('/apehub-web/developer/plugins'),
    ]);
    state.profile = profile;
    state.plugins = plugins || [];
    renderProfile();
    renderPurchased(purchased || []);
    renderPlugins();
    await Promise.all([loadWallets(), loadIncomes(), loadWithdrawals(), loadLedger()]);
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
  $('#statPlugins').textContent = `${state.plugins.length} 个`;
}

function renderPurchased(items) {
  $('#purchasedBody').innerHTML = items.length ? items.map(item => {
    const files = (item.files || []).map(file => `<button class="btn btn-small" data-download="${file.id}" data-name="${esc(file.filename)}">${esc(file.version || item.version)} 下载</button>`).join(' ');
    return `<tr><td><strong>${esc(item.display_name)}</strong><br><span class="muted">${esc(item.name)}</span></td><td>${esc(item.version)}</td><td>${money(item.price)} USDT</td><td><span class="status paid">永久授权</span></td><td>${files || '-'}</td></tr>`;
  }).join('') : '<tr><td colspan="5" class="empty">暂无已购插件</td></tr>';
  $$('[data-download]').forEach(button => button.addEventListener('click', () => downloadFile(button.dataset.download, button.dataset.name)));
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

/* ========== Developer Plugin List ========== */
function renderPlugins() {
  $('#pluginList').innerHTML = state.plugins.length ? state.plugins.map(plugin => `<button class="plugin-row${state.selectedPlugin?.id === plugin.id ? ' active' : ''}" data-plugin="${plugin.id}"><strong>${esc(plugin.display_name)}</strong><span>${esc(plugin.version)} · ${statusText(plugin.status)} · ${money(plugin.price)} USDT</span></button>`).join('') : '<div class="empty">还没有插件草稿<br><span class="muted" style="font-size:12px">点击右上角发布新插件</span></div>';
  $$('[data-plugin]').forEach(button => button.addEventListener('click', () => selectPlugin(Number(button.dataset.plugin))));
}

async function selectPlugin(id) {
  try {
    state.selectedPlugin = await api(`/apehub-web/developer/plugins/${id}`);
    state.selectedVersion = state.selectedPlugin.versions?.[0] || null;
    renderPlugins();
    renderWorkbench();
  } catch (error) { toast(error.message, true); }
}

/* ========== Developer Workbench ========== */
function renderWorkbench() {
  const root = $('#workbench');
  const plugin = state.selectedPlugin;
  if (!plugin) { root.innerHTML = '<div class="workbench-empty">选择左侧插件进入管理</div>'; return; }
  const logoMedia = (plugin.media || []).find(m => m.media_type === 'logo');
  const carouselMedia = (plugin.media || []).filter(m => m.media_type === 'carousel');
  const logoUrl = logoMedia ? logoMedia.url : (isImage(plugin.icon) ? plugin.icon : '/apehub-web/assets/logo.png');
  root.innerHTML = `
    <div class="plugin-meta">
      <img src="${esc(logoUrl)}" alt="${esc(plugin.display_name)}">
      <div><h2>${esc(plugin.display_name)}</h2><p>${esc(plugin.name)} · ${money(plugin.price)} USDT · ${statusText(plugin.status)}</p></div>
    </div>
    <div class="block">
      <h3>基本信息</h3>
      <div class="info-grid">
        <div class="field"><label>插件标题</label><input id="editDisplayName" value="${esc(plugin.display_name)}"></div>
        <div class="field"><label>插件标识</label><input id="editName" value="${esc(plugin.name)}"><div class="field-hint">小写字母+下划线</div></div>
        <div class="field"><label>售价 (USDT)</label><input id="editPrice" type="number" min="0" step="0.01" value="${money(plugin.price)}"><div class="field-hint">填 0 表示免费</div></div>
        <div class="field"><label>分类</label><select id="editCategory"><option ${plugin.category === '工具' ? 'selected' : ''}>工具</option><option ${plugin.category === 'AI' ? 'selected' : ''}>AI</option><option ${plugin.category === '电商' ? 'selected' : ''}>电商</option><option ${plugin.category === '仪表盘' ? 'selected' : ''}>仪表盘</option><option ${plugin.category === '系统增强' ? 'selected' : ''}>系统增强</option></select></div>
        <div class="field"><label>标签</label><input id="editTags" value="${esc(plugin.tags)}"><div class="field-hint">逗号分隔</div></div>
        <div class="field full"><label>插件介绍</label><textarea id="editDescription" style="min-height:100px">${esc(plugin.description || '')}</textarea></div>
      </div>
      <div class="info-actions"><button class="btn btn-primary btn-small" id="savePluginInfo">保存基本信息</button></div>
    </div>
    <div class="block">
      <h3>市场图片</h3>
      <div class="media-section">
        <div class="upload-box">
          <div class="upload-preview">${logoMedia ? `<img src="${esc(logoMedia.url)}" alt="logo">` : '<span class="placeholder">Logo</span>'}</div>
          <div class="upload-info"><span>插件 Logo</span><label class="btn btn-small">选择图片<input id="logoFile" type="file" accept="image/png,image/jpeg,image/gif,image/webp" hidden></label></div>
        </div>
        <div class="upload-box">
          <div class="upload-preview">${carouselMedia.length ? `<img src="${esc(carouselMedia[0].url)}" alt="carousel">` : '<span class="placeholder">轮播</span>'}</div>
          <div class="upload-info"><span>轮播图（${carouselMedia.length} 张）</span><label class="btn btn-small">选择图片<input id="carouselFile" type="file" accept="image/png,image/jpeg,image/gif,image/webp" multiple hidden></label></div>
        </div>
      </div>
      ${carouselMedia.length ? `<div class="carousel-thumbs">${carouselMedia.map(m => `<div class="thumb"><img src="${esc(m.url)}" alt="${esc(m.alt_text)}"><button class="thumb-del" data-media="${m.id}" title="删除">×</button></div>`).join('')}</div>` : ''}
    </div>
    <div class="block">
      <div class="section-head"><h3>版本管理</h3><button class="btn btn-small" id="newVersionBtn">新建版本</button></div>
      <div class="version-layout">
        <div class="version-tree">${(plugin.versions || []).map(version => `<button data-version="${version.id}" class="${state.selectedVersion?.id === version.id ? 'active' : ''}"><strong>${esc(version.version)}</strong><br><span class="status ${esc(version.status)}">${statusText(version.status)}</span></button>`).join('') || '<div class="empty">暂无版本</div>'}</div>
        <div class="version-detail" id="versionDetail"></div>
      </div>
    </div>`;
  $('#savePluginInfo').addEventListener('click', savePluginInfo);
  $('#logoFile').addEventListener('change', event => uploadMedia(event.target.files[0], 'logo'));
  $('#carouselFile').addEventListener('change', event => uploadCarousel(event.target.files));
  $('#newVersionBtn').addEventListener('click', () => $('#versionDialog').showModal());
  $$('[data-version]').forEach(button => button.addEventListener('click', () => {
    state.selectedVersion = plugin.versions.find(item => item.id === Number(button.dataset.version));
    renderWorkbench();
  }));
  $$('[data-media]').forEach(button => button.addEventListener('click', async () => {
    if (!confirm('确定删除此图片吗？')) return;
    try { await api(`/apehub-web/developer/plugins/${plugin.id}/media/${button.dataset.media}`, { method: 'DELETE' }); toast('图片已删除'); await selectPlugin(plugin.id); } catch (error) { toast(error.message, true); }
  }));
  renderVersionDetail();
}

async function savePluginInfo() {
  const plugin = state.selectedPlugin;
  if (!plugin) return;
  const payload = {
    name: $('#editName').value.trim(),
    display_name: $('#editDisplayName').value.trim(),
    description: $('#editDescription').value.trim(),
    category: $('#editCategory').value,
    tags: $('#editTags').value.trim(),
    price: Number($('#editPrice').value),
    version: plugin.version,
  };
  if (!payload.display_name) { toast('插件标题不能为空', true); return; }
  if (!payload.name) { toast('插件标识不能为空', true); return; }
  try {
    await api(`/apehub-web/developer/plugins/${plugin.id}`, { method: 'PUT', body: JSON.stringify(payload) });
    toast('基本信息已保存'); await selectPlugin(plugin.id); await refreshPlugins();
  } catch (error) { toast(error.message, true); }
}

function renderVersionDetail() {
  const root = $('#versionDetail');
  const version = state.selectedVersion;
  if (!root) return;
  if (!version) { root.innerHTML = '<div class="empty">请选择版本</div>'; return; }
  const editable = ['draft', 'rejected', 'analysis_failed'].includes(version.status);
  const isPublished = version.status === 'published';
  const isAnalyzing = version.status === 'analyzing';
  const canEdit = editable || isPublished;
  const hasPackage = (version.files || []).length > 0;
  const hasDocs = !!(version.documentation && version.documentation.trim());
  const report = version.analysis_report;
  const aiResult = report?.ai || null;
  const files = (version.files || []).map(file => `<div class="file-chip"><span>${esc(file.filename)}</span><span class="muted">${Math.ceil(file.size / 1024)} KB</span>${canEdit ? `<button class="file-chip-del" data-file="${file.id}" title="删除文件">×</button>` : ''}</div>`).join('') || '<span class="muted">未上传安装包</span>';
  const warnings = report?.warnings || [];
  const riskColors = { critical: 'red', high: 'red', medium: 'amber', low: 'green', none: 'green' };
  const riskColor = riskColors[report?.risk_level] || 'text-3';
  // Step guide for draft/rejected/analysis_failed versions
  const showSteps = editable;
  // Re-review banner for published versions being edited
  const reReviewBanner = isPublished ? `<div class="re-review-banner">⚠️ 此版本已发布。修改内容或替换安装包后，版本将重新进入审核队列。</div>` : '';
  const steps = [
    { label: '上传 ZIP', done: hasPackage, icon: '📦' },
    { label: '填写文档', done: hasDocs, icon: '📝' },
    { label: '提交审核', done: !editable, icon: '🚀' },
  ];
  const stepsHtml = showSteps ? `<div class="step-guide">${steps.map((s, i) => `<div class="step ${s.done ? 'done' : ''} ${s.failed ? 'failed' : ''}"><span class="step-icon">${s.failed ? '⚠️' : s.done ? '✓' : s.icon}</span><span class="step-label">${esc(s.label)}</span>${i < steps.length - 1 ? '<span class="step-arrow">→</span>' : ''}</div>`).join('')}</div>` : '';
  const emptyTip = (canEdit && !hasPackage) ? `<div class="empty-tip">💡 请先上传 ZIP 安装包，可使用「AI 补全」生成文档，或手动填写文档</div>` : '';
  root.innerHTML = `
    <div class="version-head"><h4>${esc(version.version)}</h4><span class="status ${esc(version.status)}">${statusText(version.status)}</span></div>
    ${stepsHtml}
    ${reReviewBanner}
    ${emptyTip}
    ${version.compatibility ? `<div class="field" style="margin-bottom:14px"><label>兼容性</label><input id="versionCompat" value="${esc(version.compatibility)}" ${canEdit ? '' : 'disabled'}></div>` : ''}
    <div class="field"><label>更新说明${canEdit ? `<span class="label-actions"><button class="btn btn-small btn-ai-optimize" id="optimizeChangelogBtn" title="使用 AI 润色更新说明">AI 优化</button><button class="btn btn-small btn-ai-optimize" id="generateChangelogBtn" title="分析已上传的代码包，用 AI 生成更新说明">AI 补全</button></span>` : ''}</label><textarea id="versionChangelog" ${canEdit ? '' : 'disabled'}>${esc(version.changelog || '')}</textarea></div>
    <div class="field" style="margin-top:14px"><label>技术文档（Markdown）${canEdit ? `<span class="label-actions"><button class="btn btn-small btn-ai-optimize" id="optimizeDocsBtn" title="使用 AI 润色技术文档">AI 优化</button><button class="btn btn-small btn-ai-optimize" id="generateDocsBtn" title="分析已上传的代码包，用 AI 生成技术文档">AI 补全</button><label class="btn btn-small btn-ai-optimize" title="上传本地 .md 文档">上传 md<input id="docsFile" type="file" accept=".md,.markdown,text/markdown" hidden></label></span>` : ''}</label><textarea id="versionDocs" style="min-height:260px" ${canEdit ? '' : 'disabled'}>${esc(version.documentation || '')}</textarea></div>
    <div class="analysis-panel">
      <div class="analysis-header"><strong>安装包</strong>${files}</div>
      <div class="analysis-row"><span>静态风险</span><span class="status ${riskColor}">${esc(report?.risk_level || '尚未分析')}</span></div>
      <div class="analysis-row"><span>文件数</span><span>${report?.file_count || 0}</span></div>
      <div class="analysis-row"><span>解压大小</span><span>${report?.uncompressed_size ? Math.ceil(report.uncompressed_size / 1024) + ' KB' : '-'}</span></div>
      ${warnings.length ? `<div class="analysis-warnings">${warnings.map(w => `<div class="warning-item warning-${w.severity}"><span class="severity">${esc(w.severity)}</span>${esc(w.message)} <span class="muted">${esc(w.file)}</span></div>`).join('')}</div>` : ''}
      ${aiResult ? `<div class="ai-result"><div class="ai-summary">${esc(aiResult.summary || '')}</div>${aiResult.features ? `<div class="ai-features">${(Array.isArray(aiResult.features) ? aiResult.features : []).map((f, i) => `<div class="ai-feat"><strong>${i + 1}. ${esc(typeof f === 'string' ? f : f.name || f.title || '')}</strong><p>${esc(typeof f === 'string' ? '' : f.description || '')}</p></div>`).join('')}</div>` : ''}</div>` : ''}
      ${version.status === 'analysis_failed' ? `<div class="analysis-error"><strong>⚠️ 分析失败</strong><p>AI 分析过程中出错。您可以手动填写文档后直接提交审核，或使用「AI 补全」重新生成。</p><div class="analysis-error-detail" style="display:none"></div></div>` : ''}
      ${version.reject_reason ? `<div class="reject-reason"><strong>驳回原因：</strong>${esc(version.reject_reason)}</div>` : ''}
      <div id="analysisProgress"></div>
    </div>
    <div class="actions">${canEdit ? `<button class="btn btn-small" id="uploadPackageBtn" type="button">上传 ZIP</button><input id="packageFile" type="file" accept=".zip,application/zip" hidden><button class="btn btn-small" id="saveVersion">保存文档</button><button class="btn btn-primary btn-small" id="submitVersion" ${hasPackage ? '' : 'disabled title="请先上传 ZIP 安装包"'}${!hasDocs ? ' disabled title="请先填写技术文档"' : ''}>${isPublished ? '重新提交审核' : '提交审核'}</button>` : ''}</div>`;
  // Bind file delete
  if (canEdit) $$('[data-file]').forEach(btn => btn.addEventListener('click', async () => {
    if (!confirm('确定删除此安装包吗？')) return;
    try { await api(`/apehub-web/developer/plugins/${state.selectedPlugin.id}/files/${btn.dataset.file}`, { method: 'DELETE' }); toast('文件已删除'); await selectPlugin(state.selectedPlugin.id); } catch (error) { toast(error.message, true); }
  }));
  // Resume progress polling if a job is still running for this version
  if (isAnalyzing) pollAnalysis(state.selectedPlugin.id, version.id);
  if (!canEdit) return;
  $('#uploadPackageBtn').addEventListener('click', () => $('#packageFile').click());
  $('#packageFile').addEventListener('change', event => uploadPackage(event.target.files[0]));
  $('#saveVersion').addEventListener('click', saveVersion);
  $('#submitVersion').addEventListener('click', submitVersion);
  const optimizeBtn = $('#optimizeChangelogBtn');
  if (optimizeBtn) optimizeBtn.addEventListener('click', optimizeChangelog);
  const generateChangelogBtn = $('#generateChangelogBtn');
  if (generateChangelogBtn) generateChangelogBtn.addEventListener('click', generateChangelog);
  const optimizeDocsBtn = $('#optimizeDocsBtn');
  if (optimizeDocsBtn) optimizeDocsBtn.addEventListener('click', optimizeDocumentation);
  const generateDocsBtn = $('#generateDocsBtn');
  if (generateDocsBtn) generateDocsBtn.addEventListener('click', generateDocumentation);
  const docsFileInput = $('#docsFile');
  if (docsFileInput) docsFileInput.addEventListener('change', event => loadDocsFile(event.target.files[0]));
  // If analysis failed, try to fetch the error info
  if (version.status === 'analysis_failed') fetchAnalysisError(state.selectedPlugin.id, version.id);
}

async function fetchAnalysisError(pluginId, versionId) {
  try {
    const data = await api(`/apehub-web/developer/plugins/${pluginId}/versions/${versionId}/analysis`);
    const job = data.job;
    const errBox = $('.analysis-error-detail');
    if (errBox && job?.error) {
      errBox.textContent = job.error;
      errBox.style.display = 'block';
    }
  } catch (_) { /* silently ignore — UI already has a generic fallback message */ }
}

async function uploadMedia(file, mediaType) {
  if (!file || !state.selectedPlugin) return;
  const form = new FormData(); form.append('file', file);
  try {
    await api(`/apehub-web/developer/plugins/${state.selectedPlugin.id}/media/upload?media_type=${mediaType}`, { method: 'POST', body: form });
    toast('图片上传成功'); await selectPlugin(state.selectedPlugin.id);
  } catch (error) { toast(error.message, true); }
}

async function uploadCarousel(files) {
  if (!files?.length || !state.selectedPlugin) return;
  for (const file of files) {
    const form = new FormData(); form.append('file', file);
    try {
      await api(`/apehub-web/developer/plugins/${state.selectedPlugin.id}/media/upload?media_type=carousel`, { method: 'POST', body: form });
    } catch (error) { toast(error.message, true); return; }
  }
  toast(`已上传 ${files.length} 张轮播图`); await selectPlugin(state.selectedPlugin.id);
}

async function uploadPackage(file) {
  if (!file || !state.selectedPlugin || !state.selectedVersion) return;
  const wasPublished = state.selectedVersion.status === 'published';
  const form = new FormData(); form.append('file', file);
  try {
    await api(`/apehub-web/developer/plugins/${state.selectedPlugin.id}/files?file_type=package&version_id=${state.selectedVersion.id}`, { method: 'POST', body: form });
    toast(wasPublished ? '安装包已替换，版本重新提交审核' : '安装包校验并上传成功'); await selectPlugin(state.selectedPlugin.id);
  } catch (error) { toast(error.message, true); }
}

async function optimizeChangelog() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  const textarea = $('#versionChangelog');
  const raw = (textarea?.value || '').trim();
  if (!raw) { toast('请先输入更新说明草稿', true); return; }
  const btn = $('#optimizeChangelogBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'AI 优化中...'; }
  try {
    const data = await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/optimize-changelog`, { method: 'POST', body: JSON.stringify({ changelog: raw }) });
    if (textarea && data.changelog) { textarea.value = data.changelog; toast('AI 优化完成，请确认后保存'); }
    else { toast('AI 返回为空', true); }
  }   catch (error) { toast(error.message, true); }
  finally { if (btn) { btn.disabled = false; btn.textContent = 'AI 优化'; } }
}

/* ========== AI Generate (from uploaded package) & Docs upload ========== */
async function generateChangelog() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  if (!(version.files || []).length) { toast('请先上传 ZIP 安装包，AI 补全需要代码包内容', true); return; }
  const btn = $('#generateChangelogBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'AI 补全中...'; }
  try {
    const data = await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/generate-changelog`, { method: 'POST' });
    const textarea = $('#versionChangelog');
    if (textarea && data.changelog) { textarea.value = data.changelog; toast('AI 补全完成，请确认后保存'); }
    else { toast('AI 返回为空', true); }
  } catch (error) { toast(error.message, true); }
  finally { if (btn) { btn.disabled = false; btn.textContent = 'AI 补全'; } }
}

async function optimizeDocumentation() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  const textarea = $('#versionDocs');
  const raw = (textarea?.value || '').trim();
  if (!raw) { toast('请先输入技术文档草稿', true); return; }
  const btn = $('#optimizeDocsBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'AI 优化中...'; }
  try {
    const data = await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/optimize-documentation`, { method: 'POST', body: JSON.stringify({ documentation: raw }) });
    if (textarea && data.documentation) { textarea.value = data.documentation; toast('AI 优化完成，请确认后保存'); }
    else { toast('AI 返回为空', true); }
  } catch (error) { toast(error.message, true); }
  finally { if (btn) { btn.disabled = false; btn.textContent = 'AI 优化'; } }
}

async function generateDocumentation() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  if (!(version.files || []).length) { toast('请先上传 ZIP 安装包，AI 补全需要代码包内容', true); return; }
  const btn = $('#generateDocsBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'AI 补全中...'; }
  try {
    const data = await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/generate-documentation`, { method: 'POST' });
    const textarea = $('#versionDocs');
    if (textarea && data.documentation) { textarea.value = data.documentation; toast('AI 补全完成，请确认后保存'); }
    else { toast('AI 返回为空', true); }
  } catch (error) { toast(error.message, true); }
  finally { if (btn) { btn.disabled = false; btn.textContent = 'AI 补全'; } }
}

function loadDocsFile(file) {
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) { toast('文档文件不能超过 5 MB', true); return; }
  const reader = new FileReader();
  reader.onload = () => {
    const content = String(reader.result || '');
    if (!content.trim()) { toast('文档内容为空', true); return; }
    const textarea = $('#versionDocs');
    if (textarea) {
      textarea.value = content;
      toast('文档已载入，请确认后点击「保存文档」');
    }
  };
  reader.onerror = () => toast('读取文件失败', true);
  reader.readAsText(file, 'utf-8');
}

async function saveVersion() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  try {
    const wasPublished = version.status === 'published';
    await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}`, { method: 'PUT', body: JSON.stringify({ changelog: $('#versionChangelog').value, documentation: $('#versionDocs').value }) });
    toast(wasPublished ? '版本已保存并重新提交审核' : '版本资料已保存'); await selectPlugin(plugin.id);
  } catch (error) { toast(error.message, true); }
}

/* ========== AI Analysis with progress visualization ========== */
async function pollAnalysis(pluginId, versionId) {
  clearTimeout(state.analysisTimer);
  try {
    const data = await api(`/apehub-web/developer/plugins/${pluginId}/versions/${versionId}/analysis`);
    const progress = $('#analysisProgress');
    if (progress) {
      const job = data.job;
      if (!job) { progress.innerHTML = ''; return; }
      const stageText = { queued: '排队中...', running: '正在分析...', succeeded: '分析完成', failed: '分析失败' }[job.status] || job.stage;
      const barColor = job.status === 'failed' ? 'var(--red)' : 'var(--primary)';
      progress.innerHTML = `
        <div class="analysis-job">
          <div class="job-stage">${esc(stageText)}</div>
          <progress max="100" value="${job.progress || 0}" style="width:100%;height:8px;--progress-color:${barColor}"></progress>
          <div class="job-meta">${job.model ? `模型: ${esc(job.model)}` : ''} · ${job.progress || 0}%</div>
          ${job.error ? `<div class="job-error">${esc(job.error)}</div>` : ''}
        </div>`;
    }
    if (['queued', 'running'].includes(data.job?.status)) {
      // Safety net: stop polling if the job has been running too long (AI upstream hang)
      const started = data.job.created_at ? new Date(data.job.created_at).getTime() : Date.now();
      const elapsedMs = Date.now() - started;
      if (elapsedMs > 5 * 60 * 1000) {
        const box = $('#analysisProgress');
        if (box) box.innerHTML = '<div class="analysis-job"><div class="job-stage">AI 分析超时</div><div class="job-error">分析耗时过长，可能是 AI 服务暂时不可用。请稍后重试，或手动填写文档后提交审核。</div></div>';
        await selectPlugin(pluginId);
        toast('AI 分析超时，请稍后重试', true);
        return;
      }
      state.analysisTimer = setTimeout(() => pollAnalysis(pluginId, versionId), 1500);
    } else {
      await selectPlugin(pluginId);
      const succeeded = data.job?.status === 'succeeded';
      toast(succeeded ? 'AI 文档已生成，请查看并编辑后提交审核' : (data.job?.error || 'AI 分析失败'), !succeeded);
    }
  } catch (error) { toast(error.message, true); }
}

async function submitVersion() {
  const plugin = state.selectedPlugin, version = state.selectedVersion;
  try {
    await saveVersion();
    await api(`/apehub-web/developer/plugins/${plugin.id}/versions/${version.id}/submit`, { method: 'POST' });
    toast('版本已提交审核，请等待管理员审核'); await selectPlugin(plugin.id); await refreshPlugins();
  } catch (error) { toast(error.message, true); }
}

async function refreshPlugins() {
  state.plugins = await api('/apehub-web/developer/plugins'); renderPlugins();
}

/* ========== Incomes (paginated) ========== */
async function loadIncomes(page = state.pager.income.page) {
  state.pager.income.page = page;
  try {
    const data = await api(`/apehub-web/incomes?page=${page}&page_size=10`);
    renderIncomes(data.items || []);
    renderPager('#incomePager', data, loadIncomes);
    const total = Number(data.total || 0);
    $('#incomeSummary').textContent = total ? `共 ${total} 条` : '';
  } catch (error) { toast(error.message, true); }
}

function renderIncomes(items) {
  $('#incomeBody').innerHTML = items.length ? items.map(item => `<tr><td>${esc(item.plugin_name)}</td><td>${money(item.amount)} USDT</td><td>${money(item.rate)}%</td><td><span class="status ${esc(item.status)}">${statusText(item.status)}</span></td><td>${date(item.available_at)}</td></tr>`).join('') : '<tr><td colspan="5" class="empty">暂无销售收益</td></tr>';
}

/* ========== Wallets (multi-wallet CRUD) ========== */
const TRC20_RE = /^T[1-9A-HJ-NP-Za-km-z]{33}$/;

function isTrc20Address(value) { return TRC20_RE.test(String(value || '').trim()); }

function validateAddress(address, fieldName) {
  const value = String(address || '').trim();
  if (!value) return `${fieldName}不能为空`;
  if (value.length !== 34) return `${fieldName}需为 34 位（当前 ${value.length} 位）`;
  if (!value.startsWith('T')) return `${fieldName}需以 T 开头`;
  if (!TRC20_RE.test(value)) return `${fieldName}包含无效字符，请检查后重试`;
  return '';
}

function feeFor(amount) {
  const cfg = state.config || {}, value = Number(cfg.withdrawal_fee_value || 0);
  return cfg.withdrawal_fee_type === 'percent' ? amount * value / 100 : value;
}

function feeRateText() {
  const cfg = state.config || {};
  if (cfg.withdrawal_fee_type === 'percent') return `手续费率 ${money(cfg.withdrawal_fee_value)}%`;
  const value = Number(cfg.withdrawal_fee_value || 0);
  return value > 0 ? `固定手续费 ${money(value)} USDT` : '免手续费';
}

function withdrawHintText() {
  return `最低提现 ${money(state.config?.min_withdrawal || 100)} USDT · ${feeRateText()}`;
}

async function loadWallets() {
  try {
    state.wallets = await api('/apehub-web/wallets');
    renderWalletCards();
  } catch (error) { toast(error.message, true); }
}

function renderWalletCards() {
  const grid = $('#walletCardGrid');
  if (!grid) return;
  const wallets = state.wallets || [];
  grid.innerHTML = wallets.length ? wallets.map(w => `
    <div class="wallet-card${w.is_default ? ' default' : ''}" data-wallet="${w.id}">
      <div class="wallet-card-head">
        <span class="wallet-label">${esc(w.label || '未命名钱包')}</span>
        ${w.is_default ? '<span class="wallet-badge">默认</span>' : ''}
      </div>
      <div class="wallet-address" title="${esc(w.address)}">${esc(w.address.slice(0, 12))}...${esc(w.address.slice(-8))}</div>
      <div class="wallet-meta"><span class="muted">TRC20</span><span class="muted">${w.updated_at ? date(w.updated_at) : ''}</span></div>
      <div class="wallet-card-actions">
        ${w.is_default ? '' : `<button class="btn btn-small" data-wallet-default="${w.id}">设为默认</button>`}
        <button class="btn btn-primary btn-small" data-wallet-withdraw="${w.id}">提现</button>
        <button class="btn btn-small btn-danger" data-wallet-delete="${w.id}">删除</button>
      </div>
    </div>
  `).join('') : '<div class="wallet-empty">还没有钱包，点击右上角"新增钱包"添加</div>';

  // Bind card actions
  $$('[data-wallet-default]').forEach(btn => btn.addEventListener('click', async () => {
    try { await api(`/apehub-web/wallets/${btn.dataset.walletDefault}`, { method: 'PUT', body: JSON.stringify({ is_default: true }) }); toast('已设为默认钱包'); await loadWallets(); } catch (error) { toast(error.message, true); }
  }));
  $$('[data-wallet-withdraw]').forEach(btn => btn.addEventListener('click', () => openWithdrawDialog(Number(btn.dataset.walletWithdraw))));
  $$('[data-wallet-delete]').forEach(btn => btn.addEventListener('click', async () => {
    if (!confirm('确定删除此钱包吗？')) return;
    try { await api(`/apehub-web/wallets/${btn.dataset.walletDelete}`, { method: 'DELETE' }); toast('钱包已删除'); await loadWallets(); } catch (error) { toast(error.message, true); }
  }));
}

function openWalletDialog() {
  const form = $('#walletForm');
  form.reset();
  form.dataset.walletId = '';
  $('#walletDialog').showModal();
}

function openWithdrawDialog(walletId) {
  const form = $('#withdrawForm');
  const select = $('#withdrawWalletSelect');
  if (!select) return;
  select.innerHTML = (state.wallets || []).map(w => `<option value="${w.id}" ${w.id === walletId ? 'selected' : ''}>${esc(w.label || '未命名钱包')} — ${esc(w.address.slice(0, 10))}...${esc(w.address.slice(-6))}</option>`).join('');
  if (!state.wallets.length) { toast('请先添加钱包', true); return; }
  $('#withdrawRule').textContent = withdrawHintText();
  $('#withdrawDialogSub').textContent = `当前余额 ${money(state.profile?.balance || 0)} USDT`;
  form.reset();
  if (walletId) select.value = walletId;
  form.amount = '';
  updateWithdrawFeePreview();
  $('#withdrawDialog').showModal();
}

/* ========== Withdrawals (paginated) ========== */
async function loadWithdrawals(page = state.pager.withdraw.page) {
  state.pager.withdraw.page = page;
  try {
    const data = await api(`/apehub-web/withdrawals?page=${page}&page_size=10`);
    $('#withdrawBody').innerHTML = (data.items || []).length ? (data.items || []).map(item => `<tr><td>${money(item.amount)} USDT</td><td>${money(item.fee)} USDT</td><td>${money(item.net_amount)} USDT</td><td title="${esc(item.account)}">${esc(item.account.slice(0, 8))}...${esc(item.account.slice(-6))}</td><td><span class="status ${esc(item.status)}">${statusText(item.status)}</span></td><td>${esc(item.tx_hash || '-')}</td></tr>`).join('') : '<tr><td colspan="6" class="empty">暂无提现记录</td></tr>';
    renderPager('#withdrawPager', data, loadWithdrawals);
  } catch (error) { toast(error.message, true); }
}

function updateWithdrawFeePreview() {
  const el = $('#feePreview');
  if (!el) return;
  const amountEl = $('#withdrawForm [name="amount"]');
  const amount = Number(amountEl?.value || 0);
  if (amount <= 0) { el.textContent = '输入提现金额后将实时显示手续费与到账金额'; el.classList.add('fee-preview-muted'); return; }
  el.classList.remove('fee-preview-muted');
  const fee = Math.min(amount, feeFor(amount));
  el.textContent = `手续费 ${money(fee)} USDT，预计到账 ${money(Math.max(0, amount - fee))} USDT`;
}

/* ========== Ledger (paginated) ========== */
async function loadLedger(page = state.pager.ledger.page) {
  state.pager.ledger.page = page;
  const entryType = state.pager.ledger.type || '';
  try {
    const data = await api(`/apehub-web/ledger?page=${page}&page_size=10${entryType ? `&entry_type=${entryType}` : ''}`);
    $('#ledgerBody').innerHTML = (data.items || []).length ? (data.items || []).map(item => `<tr><td>${esc(item.type_label)}</td><td class="${item.is_income ? 'ledger-income' : 'ledger-expense'}">${item.is_income ? '+' : ''}${money(item.amount)} USDT</td><td><span class="status ${esc(item.status)}">${statusText(item.status)}</span></td><td class="muted">${esc(item.note || '-')}</td><td>${date(item.created_at)}</td></tr>`).join('') : '<tr><td colspan="5" class="empty">暂无流水记录</td></tr>';
    renderPager('#ledgerPager', data, loadLedger);
  } catch (error) { toast(error.message, true); }
}

/* ========== Pagination helper ========== */
function renderPager(container, data, loadFn) {
  const el = $(container);
  if (!el) return;
  const { total, page, page_size } = data;
  const pages = Math.ceil(total / page_size) || 1;
  if (pages <= 1) { el.innerHTML = total ? `<span class="muted pager-info">共 ${total} 条</span>` : ''; return; }
  const btns = [];
  if (page > 1) btns.push(`<button class="btn btn-small pager-btn" data-page="${page - 1}">上一页</button>`);
  // page number buttons
  const start = Math.max(1, page - 2), end = Math.min(pages, page + 2);
  if (start > 1) { btns.push(`<button class="btn btn-small pager-btn" data-page="1">1</button>`); if (start > 2) btns.push('<span class="muted">…</span>'); }
  for (let i = start; i <= end; i++) btns.push(`<button class="btn btn-small pager-btn${i === page ? ' active' : ''}" data-page="${i}">${i}</button>`);
  if (end < pages) { if (end < pages - 1) btns.push('<span class="muted">…</span>'); btns.push(`<button class="btn btn-small pager-btn" data-page="${pages}">${pages}</button>`); }
  if (page < pages) btns.push(`<button class="btn btn-small pager-btn" data-page="${page + 1}">下一页</button>`);
  el.innerHTML = `<div class="pager"><span class="muted pager-info">共 ${total} 条 / ${pages} 页</span><div class="pager-btns">${btns.join('')}</div></div>`;
  el.querySelectorAll('[data-page]').forEach(btn => btn.addEventListener('click', () => loadFn(Number(btn.dataset.page))));
}

/* ========== Event Bindings ========== */
$('#logoutBtn').addEventListener('click', () => { if (confirm('确定退出登录吗？')) logout(); });
$$('.tab').forEach(button => button.addEventListener('click', () => {
  $$('.tab').forEach(item => item.classList.toggle('active', item === button));
  $$('.panel').forEach(panel => panel.classList.toggle('active', panel.id === `panel-${button.dataset.tab}`));
}));
$$('.stat[data-tab-target]').forEach(stat => stat.addEventListener('click', () => {
  const tab = $(`.tab[data-tab="${stat.dataset.tabTarget}"]`);
  if (tab) tab.click();
}));
$('#openPluginDialog').addEventListener('click', () => $('#pluginDialog').showModal());
$$('[data-close]').forEach(button => button.addEventListener('click', () => button.closest('dialog').close()));
$('#pluginForm').addEventListener('submit', async event => {
  event.preventDefault(); const form = new FormData(event.target);
  try {
    const result = await api('/apehub-web/developer/plugins', { method: 'POST', body: JSON.stringify(Object.fromEntries(form.entries())) });
    event.target.reset(); $('#pluginDialog').close(); toast('插件草稿已创建，请在工作台上传安装包和图片'); await refreshPlugins(); await selectPlugin(result.id);
  } catch (error) { toast(error.message, true); }
});
$('#versionForm').addEventListener('submit', async event => {
  event.preventDefault(); const plugin = state.selectedPlugin; const form = new FormData(event.target);
  try {
    const created = await api(`/apehub-web/developer/plugins/${plugin.id}/versions`, { method: 'POST', body: JSON.stringify(Object.fromEntries(form.entries())) });
    event.target.reset(); $('#versionDialog').close(); toast('新版本草稿已创建'); await selectPlugin(plugin.id); state.selectedVersion = state.selectedPlugin.versions.find(item => item.id === created.id) || state.selectedPlugin.versions[0]; renderWorkbench();
  } catch (error) { toast(error.message, true); }
});

// Wallet dialog
$('#openWalletDialog').addEventListener('click', openWalletDialog);
$('#walletForm').addEventListener('submit', async event => {
  event.preventDefault();
  const fd = new FormData(event.target);
  const address = fd.get('address')?.trim() || '';
  const error = validateAddress(address, '钱包地址');
  if (error) { toast(error, true); return; }
  try {
    await api('/apehub-web/wallets', { method: 'POST', body: JSON.stringify({ address, label: fd.get('label') || '', is_default: fd.get('is_default') === 'on' }) });
    event.target.reset(); $('#walletDialog').close(); toast('钱包已添加'); await loadWallets();
  } catch (error) { toast(error.message, true); }
});

// Wallet dialog address validation
$('#walletForm [name="address"]')?.addEventListener('input', function () {
  if (!this.value.trim()) { $('#walletDialogHint').textContent = '仅支持 TRC20 网络，地址以 T 开头共 34 位'; $('#walletDialogHint').classList.remove('error-text'); return; }
  const error = validateAddress(this.value, '钱包地址');
  if (error) { $('#walletDialogHint').textContent = error; $('#walletDialogHint').classList.add('error-text'); }
  else { $('#walletDialogHint').textContent = '地址格式正确'; $('#walletDialogHint').classList.remove('error-text'); }
});

// Withdraw dialog
$('#withdrawForm [name="amount"]')?.addEventListener('input', updateWithdrawFeePreview);
$('#withdrawForm').addEventListener('submit', async event => {
  event.preventDefault();
  const fd = new FormData(event.target);
  const walletId = Number(fd.get('wallet_id'));
  const amount = fd.get('amount')?.trim();
  if (!walletId) { toast('请选择收款钱包', true); return; }
  if (!amount || Number(amount) <= 0) { toast('请输入有效的提现金额', true); return; }
  try {
    await api('/apehub-web/withdrawals', { method: 'POST', body: JSON.stringify({ amount, wallet_id: walletId }) });
    $('#withdrawDialog').close(); toast('提现申请已提交'); await refreshAll();
  } catch (error) { toast(error.message, true); }
});

// Ledger filter buttons
$$('.ledger-filter-btn').forEach(btn => btn.addEventListener('click', () => {
  $$('.ledger-filter-btn').forEach(b => b.classList.toggle('active', b === btn));
  state.pager.ledger.type = btn.dataset.ledgerFilter || '';
  state.pager.ledger.page = 1;
  loadLedger();
}));

init();
