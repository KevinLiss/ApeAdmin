# 本地运行

## 环境

- Python 3.11 或更高版本
- Node.js 18 或更高版本
- Git
- 开发环境可直接使用 SQLite；生产环境建议使用 MySQL

## 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows 使用 .venv\\Scripts\\activate
pip install -e .
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

后端 API 文档地址为 `http://127.0.0.1:8000/docs`。启动时会初始化核心表、种子菜单并加载启用的内置插件。

## 启动管理台

```bash
cd frontend
npm install
npm run dev
```

开发服务器通常运行在 `http://localhost:5173`。前端通过 Vite 代理访问后端 API。

## 访问官网

- 首页：`/apehub-web/index.html`
- 插件市场：`/apehub-web/plugins.html`
- 技术文档：`/apehub-web/docs-portal/`
- 个人中心：`/apehub-web/profile.html`

个人中心页面需要官网登录态；未登录时只显示登录提示，不读取开发者数据。

## 首次检查

1. 使用管理员账号登录管理台。
2. 确认“插件管理”中的 `Apehub_web` 为启用状态。
3. 打开官网首页和本技术文档入口，确认静态资源没有 404。
4. 在管理台刷新动态菜单，确认 `apehub_web/admin/*` 页面均能访问。

生产部署时不要使用默认密码，不要把 SMTP 授权码、AI Key 或支付密钥提交到代码仓库。
