const marketState = { category: 'all', keyword: '', page: 1, pageSize: 18, total: 0, items: [] };
const marketEsc = value => String(value ?? '').replace(/[&<>'"]/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
const marketIsImage = value => /^(?:https?:\/\/|\/|data:image\/)/i.test(String(value || '').trim());
const marketPrice = value => Number(value || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function categoryKey(value) {
  const text = String(value || '').toLowerCase();
  if (text.includes('ai')) return 'ai';
  if (text.includes('数据')) return 'data';
  if (text.includes('界面') || text.includes('ui') || text.includes('仪表')) return 'ui';
  if (text.includes('运维') || text.includes('系统')) return 'sys';
  if (text.includes('业务') || text.includes('电商')) return 'biz';
  return 'dev';
}

async function loadMarket(reset = true) {
  if (reset) marketState.page = 1;
  const params = new URLSearchParams({ page: String(marketState.page), page_size: String(marketState.pageSize) });
  if (marketState.keyword) params.set('keyword', marketState.keyword);
  const response = await fetch(`/api/v1/apehub-web/site/public/plugins?${params}`);
  const payload = await response.json();
  if (!response.ok || payload.code !== 200) throw new Error(payload.msg || '插件市场加载失败');
  marketState.items = reset ? payload.data.items : marketState.items.concat(payload.data.items || []);
  marketState.total = payload.data.total || 0;
  renderMarket();
}

function renderMarket() {
  const grid = document.getElementById('pluginsGrid');
  const filtered = marketState.items.filter(item => marketState.category === 'all' || categoryKey(item.category) === marketState.category);
  if (!filtered.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;padding:60px 20px;text-align:center;color:var(--text-3)">暂无已上架插件</div>';
  } else {
    grid.innerHTML = filtered.map(item => {
      const tags = String(item.tags || '').split(',').map(tag => tag.trim()).filter(Boolean).slice(0, 4);
      const icon = marketIsImage(item.icon)
        ? `<img src="${marketEsc(item.icon)}" alt="${marketEsc(item.display_name)}" style="width:100%;height:100%;object-fit:cover;border-radius:12px">`
        : marketEsc(item.icon || '插');
      return `<article class="plugin-card" data-id="${item.id}">
        <div class="p-head"><div class="p-icon" style="background:rgba(52,211,153,.12)">${icon}</div><div><div class="p-name">${marketEsc(item.display_name)}</div><div class="p-ver">v${marketEsc(item.version)}</div></div></div>
        <div class="p-desc">${marketEsc(item.description || '暂无介绍')}</div>
        <div class="p-tags">${tags.map(tag => `<span class="p-tag">${marketEsc(tag)}</span>`).join('')}</div>
        <div class="p-meta"><div class="p-stats"><span>安装 ${Number(item.install_count || 0).toLocaleString()}</span><span>下载 ${Number(item.download_count || 0).toLocaleString()}</span></div><div class="p-actions"><button class="install-btn">${Number(item.price) > 0 ? `${marketPrice(item.price)} USDT` : '免费'}</button></div></div>
      </article>`;
    }).join('');
    grid.querySelectorAll('[data-id]').forEach(card => card.addEventListener('click', () => location.href = `/apehub-web/plugin-detail.html?id=${card.dataset.id}`));
  }
  document.getElementById('loadMore').style.display = marketState.items.length < marketState.total ? 'inline-flex' : 'none';
}

document.querySelectorAll('.cat-pill').forEach(pill => pill.addEventListener('click', () => {
  document.querySelectorAll('.cat-pill').forEach(item => item.classList.toggle('active', item === pill));
  marketState.category = pill.dataset.cat;
  renderMarket();
}));
document.getElementById('searchInput').addEventListener('input', event => marketState.keyword = event.target.value.trim());
document.getElementById('searchInput').addEventListener('keydown', event => { if (event.key === 'Enter') loadMarket().catch(showMarketError); });
document.getElementById('searchBtn').addEventListener('click', () => loadMarket().catch(showMarketError));
document.getElementById('loadMore').addEventListener('click', () => { marketState.page += 1; loadMarket(false).catch(showMarketError); });
function showMarketError(error) { document.getElementById('pluginsGrid').innerHTML = `<div style="grid-column:1/-1;padding:60px 20px;text-align:center;color:var(--red)">${marketEsc(error.message)}</div>`; }

const themeToggle = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('ape-theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);
themeToggle.textContent = savedTheme === 'dark' ? '☾' : '☀';
themeToggle.addEventListener('click', () => { const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; document.documentElement.setAttribute('data-theme', next); localStorage.setItem('ape-theme', next); themeToggle.textContent = next === 'dark' ? '☾' : '☀'; });
document.getElementById('menuToggle')?.addEventListener('click', () => document.querySelector('.nav-links')?.classList.toggle('open'));
loadMarket().catch(showMarketError);
