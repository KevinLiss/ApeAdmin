/* ApeAdmin 安装下载页：版本列表渲染 + 下载 */
(() => {
  const esc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  const formatSize = size => {
    const n = Number(size || 0);
    return n >= 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(2)} MB` : n > 0 ? `${Math.ceil(n / 1024)} KB` : '';
  };
  const formatDate = d => d ? d.replace('T', ' ').slice(0, 10) : '';

  async function loadReleases() {
    const listEl = document.getElementById('releasesList');
    const latestCard = document.getElementById('latestCard');
    try {
      const response = await fetch('/api/v1/apehub-web/site/public/releases');
      const payload = await response.json();
      if (!response.ok || payload.code !== 200) throw new Error(payload.msg || '版本列表加载失败');
      const items = payload.data.items || [];
      if (!items.length) {
        listEl.innerHTML = '<div class="loading-tip">暂无可用安装包，敬请期待</div>';
        return;
      }

      // 最新版本卡片：is_latest 优先，否则取第一个
      const latest = items.find(item => item.is_latest) || items[0];
      if (latestCard) {
        document.getElementById('latestVersion').textContent = `v${latest.version}`;
        document.getElementById('latestTitle').textContent = latest.title || `ApeAdmin ${latest.version}`;
        document.getElementById('latestDesc').textContent = latest.description || latest.changelog || '';
        const dlBtn = document.getElementById('latestDownloadBtn');
        if (latest.file_name) {
          dlBtn.href = `/api/v1/apehub-web/site/public/releases/${latest.id}/download`;
          dlBtn.setAttribute('download', latest.file_name);
        } else {
          dlBtn.style.display = 'none';
        }
        latestCard.hidden = false;
      }

      // 版本列表
      listEl.innerHTML = items.map(item => {
        const isLatest = !!item.is_latest;
        const changelog = item.changelog
          ? item.changelog.split('\n').filter(line => line.trim()).map(line => `• ${line.trim()}`).join('\n')
          : (item.description || '暂无更新日志');
        const hasFile = !!item.file_name;
        return `<div class="release-item">
          <div class="r-ver"><span class="ver-badge ${isLatest ? '' : 'old'}">v${esc(item.version)}</span></div>
          <div class="r-body">
            <div class="r-title">${esc(item.title || `ApeAdmin ${item.version}`)}${isLatest ? '<span class="r-latest-tag">最新</span>' : ''}</div>
            <div class="r-changelog">${esc(changelog)}</div>
            <div class="r-meta">
              <span>${formatSize(item.file_size) || '未上传安装包'}</span>
              <span>下载 ${Number(item.download_count || 0).toLocaleString()}</span>
              <span>${formatDate(item.updated_at) || formatDate(item.created_at)}</span>
            </div>
          </div>
          <div class="r-actions">
            ${hasFile
              ? `<a class="dl-btn" href="/api/v1/apehub-web/site/public/releases/${item.id}/download" download="${esc(item.file_name)}">下载</a>`
              : '<button class="dl-btn ghost" disabled>未上传</button>'}
          </div>
        </div>`;
      }).join('');
    } catch (error) {
      listEl.innerHTML = `<div class="error-tip">${esc(error.message)}</div>`;
    }
  }

  loadReleases();
})();