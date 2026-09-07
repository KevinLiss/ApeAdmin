---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '0db5ed18-c40b-4857-a215-ceaaa51ebf87'
  PropagateID: '0db5ed18-c40b-4857-a215-ceaaa51ebf87'
  ReservedCode1: '21c3a073-d298-46b6-a431-c548fa5c68dc'
  ReservedCode2: '21c3a073-d298-46b6-a431-c548fa5c68dc'
---

<div align="center">
  <br/>
  <img src="assets/logo.png" width="130" alt="ApeAdmin Logo" />
  <h1>ApeAdmin</h1>
  <p> Built for modern AI application systems · 100% Open-Source Admin Framework</p>
</div>

<p align="center">
  <a href="https://apehub.finecv.cn/admin">Live Demo</a> ·
  <a href="http://apehub.finecv.cn/apehub-web">Website</a> ·
  <a href="http://apehub.finecv.cn/apehub-web/plugins.html">Plugin Market</a> ·
  <a href="http://apehub.finecv.cn/apehub-web/docs-portal">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#configuration">Configuration</a> ·
</p>

<p align="center">
  <a href="README.md">简体中文</a> | English
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.2.0-blue" alt="version">
  <img src="https://img.shields.io/badge/python-3.11%2B-orange" alt="python">
  <img src="https://img.shields.io/badge/vue-3.5-brightgreen" alt="vue">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="license">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey" alt="platform">
</p>

---

> **This project is AI-driven developed, with humans in charge of product and quality.** ApeAdmin iterates efficiently with AI assistance: human developers own product direction, architecture review, quality verification and final decisions, while AI accelerates implementation, testing and documentation.

---

ApeAdmin is an admin framework built for the AI era, powered by FastAPI + Vue3. It provides a platform-style management foundation that breaks away from traditional admin systems, natively adapted for AI Agent capability invocation.

The project supports plugin-based development with a thriving plugin community ecosystem; it ships with enterprise-grade capabilities including RBAC access control, a plugin market, and audit logs. The framework integrates an MCP-SSE gateway that wraps base-system and plugin features into standardized AI tools for Agents to call, seamlessly bridging traditional business systems and LLM-powered agents while retaining full admin capabilities — helping developers quickly build applications with both business management and AI tool output.

You can think of it as a "batteries-included + pluggable" admin framework — the base provides infrastructure such as permissions, menus and logs; business features are developed and deployed as independent plugins; and management capabilities are exposed to AI Agents through the MCP gateway. The project is released under the MIT license.

## Features

### Installation Wizard

WordPress-style out-of-the-box experience, no manual config editing required:

- **Auto detection** — first visit automatically redirects to the `/setup` wizard; installed systems go straight to the admin panel
- **Three-step install** — configure database → configure site & admin account → finish
- **Auto database creation** — MySQL connections are auto-detected; the database is created automatically if missing (utf8mb4)
- **Auto secret generation** — JWT_SECRET is randomly generated and written to `.env`, no manual handling needed
- **Install-lock protection** — `setup.lock` is written after installation, preventing the wizard from running again

### RBAC Permission System

- **Five-table model** — user / role / menu / dept tables plus association tables, standard RBAC infrastructure
- **Four permission layers** — public → auth-exempt → rule-based → data scope (own dept / dept & children / all)
- **Three menu types** — directory (M) / menu (C) / button (F), unlimited-depth tree structure
- **Superadmin wildcard** — super admins automatically own every permission; regular users follow role-menu assignments
- **Frontend permission directive** — the `v-permission` directive controls button-level visibility; route guards verify page-level permissions

### Microservice Plugin Architecture

- **Auto discovery** — plugins are developed as Python packages, auto-scanned via `importlib`
- **Independent deployment** — business plugins can be deployed as standalone Docker services, fully decoupled from the base
- **Full lifecycle** — `load → install → register → uninstall`, with hot enable/disable
- **Event bus** — EventBus supports 7 built-in events (APP_STARTUP / DB_READY / USER_LOGIN, etc.) for loosely-coupled plugin communication
- **ZIP install** — upload ZIP packages to import plugins, no manual file placement
- **Plugin market** — browse, search and download community plugins online; developers publish plugins and installation packages
- **Capability registration** — plugins can register their own routes, MCP tools, and event listeners

### MCP-SSE Gateway

Exposes base-system and plugin management capabilities as tools callable by AI Agents:

- **Three primitives** — Tools (tool invocation) / Resources (resource reading) / Prompts (template rendering)
- **Auto schema** — JSON Schema is automatically inferred from function signatures upon tool registration, no handwriting needed
- **RBAC filtering** — AI Agents only see tools the current user is permitted to call
- **Secure transport** — one-time ticket authentication over SSE (replacing bare JWT in URLs), 30s timeout protection on tool calls
- **Persistent recovery** — plugin registration info is persisted; MCP tool registrations auto-recover after service restart
- **Audit log** — every tool call records request, response, duration and caller
- **Plugin extension** — plugins can register tools into the MCP gateway, exposing capabilities externally

Built-in MCP tools:

| Tool | Description |
|------|-------------|
| `system_health_check` | System health check |
| `system_list_plugins` | List installed plugins |
| `role_list / create / update / delete` | Role management (requires permission) |
| `dept_list / create / update / delete` | Dept management (requires permission) |
| `menu_list / create / update / delete` | Menu management (requires permission) |

### AI Chat

- **Multi-model support** — DeepSeek / Qwen / Zhipu GLM / OpenAI / custom endpoints, all OpenAI-compatible
- **Streaming SSE** — streaming output + real-time Markdown rendering + code highlighting
- **Function Calling** — AI can invoke MCP tools to perform admin operations, up to 5 rounds of tool-call loops
- **Key management** — manage AI provider keys in the admin panel, encrypted at rest with Fernet (key derived from JWT_SECRET)

### Audit Logs

- **Request tracing** — RequestContextMiddleware assigns a globally unique request ID
- **Operation logs** — record user actions, filterable by module, time and user
- **Request timing** — automatically record the duration of every API request

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 (async) + Alembic |
| Frontend | Vue 3.5 + Vite 6 + TypeScript 5.7 + Element Plus 2.9 |
| State | Pinia 2.3 |
| Charts | ECharts 5.6 + vue-echarts |
| Database | MySQL (aiomysql) / SQLite (aiosqlite), dual-driver auto-switching |
| Cache | Redis (optional, auto-degrades to in-memory when missing) |
| Auth | JWT (access token) + bcrypt password hashing |
| AI Protocol | MCP (Model Context Protocol) — SSE transport |
| AI Models | DeepSeek / Qwen / Zhipu GLM / OpenAI (OpenAI-compatible APIs) |

## Quick Start

### Live Demo

No setup required — visit the online demo directly:

- **Demo URL**: <https://apehub.finecv.cn/admin>
- **Username**: `ceshi110`
- **Password**: `ceshi110`

> The demo account is a read-only viewer role: it can browse module data but has no create / update / delete permissions.

### Option 1: Installation Wizard (Recommended)

No manual configuration — finish installing with a few clicks in your browser:

```bash
# 1. Start the backend
cd backend
python -m venv .venv && .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 2. Start the frontend (dev mode)
cd frontend
npm install --legacy-peer-deps
npm run dev
```

Open `http://localhost:5173`; the system detects the missing installation and enters the setup wizard automatically:

1. **Configure database** — choose SQLite (zero config) or MySQL (fill in connection info, auto database creation supported)
2. **Configure site** — site name, admin account & password, access URL
3. **Finish installation** — config is written and tables created; restart the backend as prompted, and the admin account with base data is initialized automatically on restart

> SQLite suits local development and lightweight deployments; MySQL suits production and multi-service scenarios.

### Option 2: Production Deployment

One-click deployment for servers (BT Panel / Docker / bare-metal Nginx), deployment package building, and SQLite→MySQL data migration — see **[deploy/DEPLOY.md](deploy/DEPLOY.md)**.

Deployment packages contain only the admin base (RBAC / menus / plugin framework / MCP gateway), no business plugins; the setup wizard starts on first launch. Business plugins are installed on demand through the plugin import mechanism (ZIP upload / plugin market online install), decoupled from the deployment package:

### Default Exploration Path

1. Log into the admin panel (the admin account set in the setup wizard)
2. System Management → Users / Roles / Menus / Depts / Plugins
3. MCP Management → Tools / Resources / Prompts / Call Logs
4. AI Assistant → configure a model key and start chatting

> Alternatively, log into the online demo with the demo account above — no local deployment needed.

## Architecture

ApeAdmin is a front-end/back-end separated monolith with a pluggable backend and a built-in installation wizard:

```
apeadmin/
  backend/                       # FastAPI backend
    src/
      api/                       # Route layer
        auth.py                  # Auth (login/logout/user info)
        user.py                  # User management
        role.py                  # Role management
        menu.py                  # Menu management (tree)
        dept.py                  # Dept management (tree)
        plugin.py                # Plugin management
        ai_provider.py           # AI model key management
        chat.py                  # AI chat (streaming SSE)
        dashboard.py             # Dashboard statistics
        log.py                   # System logs
      core/                      # Infrastructure
        config.py                # Config (pydantic-settings)
        security.py              # Password hashing + JWT
        deps.py                  # Dependency injection
        middleware.py            # Middleware (CORS / request tracing)
        seed.py                  # Seed data initialization
        crypto.py                # API key encryption
      crud/                      # Generic CRUD base + RBAC CRUD
      db/                        # Database engine & session management
      models/                    # ORM models
        rbac.py                  # RBAC five tables
        ai.py                    # AI providers
        plugin.py                # Plugin records
        mcp.py                   # MCP audit logs
        log.py                   # System logs
      mcp/                       # MCP protocol system
        manager.py               # Tool/resource/prompt management + RBAC filtering
        routes.py                # MCP HTTP routes + audit logging
        builtin_resources.py     # Built-in tools/resources/prompts
      plugins/                   # Plugin system
        base.py                  # PluginInterface + EventBus
        manager.py               # Plugin discovery/loading/install/uninstall
        builtin/                 # Built-in plugins (drop in, directory auto-scanned)
          dev_example/           # Plugin development example
      setup_wizard/              # Installation wizard (mounted when not installed)
        state.py                 # Install state (setup.lock / .env read & write)
        api.py                   # Wizard API (status/test connection/execute install)
        setup.html               # Wizard page
      ai/                        # AI agent
        agent.py                 # Multi-model chat + tool-call loop
        tools.py                 # MCP tool list building
      schemas/                   # Pydantic request/response models
      main.py                    # App entry (lifespan + setup mode switching)
      cli.py                     # CLI tools
    alembic/                     # Database migrations
    pyproject.toml

  frontend/                      # Vue3 frontend
    src/
      api/                       # Axios wrapper + all API definitions
      components/                # ApeHeader / ApeSidebar
      composables/               # useTheme (dark/light switching)
      directives/                # v-permission permission directive
      layout/                    # Main layout
      router/                    # Routing + guards + dynamic route generation
      stores/                    # Pinia (user state/permissions/menus)
      styles/                    # Global styles
      views/                     # Pages
        login/                   # Login
        system/                  # System management (users/roles/menus/depts/files/plugins/logs/settings/profile)
        mcp/                     # MCP management (tools/resources/prompts/audit logs)
        ai/                      # AI assistant (chat/model key management)
        error/                   # Error pages (404 etc.)

  deploy/                        # Deployment assets
    DEPLOY.md                    # Production deployment doc (BT Panel/Docker/Nginx)
    build_deploy_package.sh      # Deployment package build script (base/full)
    nginx/                       # Nginx site config templates
    scripts/                     # Server-side deployment/management scripts
```

### Design Principles

1. **Install-and-go** — uninstalled systems automatically enter the `/setup` wizard; config is written to `.env` and tables are created automatically, with an install lock preventing reruns; the install phase only creates tables without running seed data — seeds run after restart with the new key, avoiding encryption key mismatch
2. **Base-plugin decoupling** — the base provides infrastructure such as RBAC, logs and the MCP gateway; all business features are developed as plugins, independent of each other
3. **Dual database drivers** — SQLite for zero-config local startup, MySQL for production, switched via the `DB_TYPE` environment variable
4. **Optional Redis** — the cache layer auto-degrades to an in-memory dictionary when missing, with no functional impact
5. **Permissions throughout AI** — MCP tool calls and AI Function Calling are both governed by RBAC; AI Agents can only operate resources they are permitted to
6. **Dynamic routing** — frontend routes are generated from the backend menu tree; adding or removing menus requires no frontend code changes

## Plugin Development

### Creating a Plugin

Create a Python package under `backend/src/plugins/builtin/`:

```
my_plugin/
  __init__.py
  plugin.py          # Plugin entry (implements PluginInterface)
  models.py          # ORM models (optional)
  api.py             # Routes (optional)
  services.py        # Business logic (optional)
```

### Plugin Interface

```python
from src.plugins.base import PluginInterface, PluginInfo, EventBus, Event

class MyPlugin(PluginInterface):
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="my-plugin",
            version="1.0.0",
            description="My first plugin",
            author="Your Name",
        )

    def on_load(self):
        """Called when the plugin loads"""
        pass

    def on_install(self):
        """Called when the plugin installs (can create database tables)"""
        pass

    def register_routes(self, app):
        """Register FastAPI routes"""
        @app.get("/api/v1/my-plugin/hello")
        def hello():
            return {"msg": "Hello from MyPlugin!"}

    def register_mcp_tools(self, mcp_manager):
        """Register MCP tools, exposed to AI Agents"""
        @mcp_manager.tool("my_plugin_greet", "Greeting tool")
        def greet(name: str) -> dict:
        """Greet the given user"""
        return {"message": f"Hello, {name}!"}

    def on_event(self, event: Event, *args, **kwargs):
        """Listen to event-bus events"""
        if event == Event.USER_LOGIN:
            print(f"User logged in: {kwargs.get('username')}")
```

### Event Types

| Event | Trigger |
|------|---------|
| `APP_STARTUP` | App starts |
| `APP_SHUTDOWN` | App shuts down |
| `DB_READY` | Database initialization completes |
| `USER_LOGIN` | User logs in |
| `USER_LOGOUT` | User logs out |
| `BEFORE_REQUEST` | Before a request is handled |
| `AFTER_REQUEST` | After a request is handled |

## Configuration

The installation wizard can generate `.env` automatically; for manual configuration refer to the table below (backend directory `.env` file or environment variables):

| Option | Default | Description |
|--------|---------|-------------|
| `DB_TYPE` | sqlite | Database type (sqlite / mysql) |
| `DB_HOST` | localhost | MySQL host |
| `DB_PORT` | 3306 | MySQL port |
| `DB_USER` | root | MySQL user |
| `DB_PASSWORD` | — | MySQL password |
| `DB_NAME` | apeadmin | Database name |
| `REDIS_URL` | redis://localhost:6379/1 | Redis connection (optional) |
| `JWT_SECRET` | change-me-in-production... | JWT signing secret (auto-generated by the wizard) |
| `JWT_EXPIRE_MINUTES` | 1440 | Token validity (minutes) |
| `CORS_ORIGINS` | localhost:5173,localhost:8000 | CORS whitelist |
| `ADMIN_PATH` | /admin | Admin panel access path |
| `SITE_URL` | — | Public site URL |
| `MCP_ENABLED` | true | Enable the MCP gateway |
| `PLUGINS_ENABLED` | true | Enable the plugin system |
| `SUPER_ADMIN_USERNAME` | admin | Super admin username |
| `SUPER_ADMIN_PASSWORD` | admin123 | Super admin password |

### AI Model Configuration

Add providers in Admin Panel → AI Assistant → Model Key Management:

| Provider | Default Model | Base URL |
|----------|---------------|----------|
| DeepSeek | deepseek-chat | `https://api.deepseek.com` |
| Qwen | qwen-plus | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Zhipu GLM | glm-4-flash | `https://open.bigmodel.cn/api/paas/v4` |
| OpenAI | gpt-4o-mini | `https://api.openai.com/v1` |
| Custom | — | Any OpenAI-compatible endpoint |

## Screenshots

<table>
  <tr>
    <td width="50%" align="center">
      <img src="assets/screenshots/login.png" alt="Login" /><br/>
      <sub><b>Dashboard</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="assets/screenshots/dashboard.png" alt="Dashboard" /><br/>
      <sub><b>Plugins</b></sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center">
      <img src="assets/screenshots/plugins.png" alt="Plugin Market" /><br/>
      <sub><b>Permissions</b></sub>
    </td>
    <td width="50%" align="center">
      <img src="assets/screenshots/system.png" alt="System" /><br/>
      <sub><b>MCP Management</b></sub>
    </td>
  </tr>
</table>

## Contributing

Contributions are welcome!

### How to Contribute

1. **Fork** the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/ApeAdmin.git
   cd ApeAdmin
   ```
3. Create a branch:
   ```bash
   git checkout -b feat/your-feature
   ```
4. Make changes and make sure it runs:
   ```bash
   # Backend
   cd backend && pip install -e . && uvicorn src.main:app --reload

   # Frontend
   cd frontend && npm install --legacy-peer-deps && npm run dev
   ```
5. Write clear commits:
   ```bash
   git commit -m "feat: add xxx support"
   ```
6. **Push** and submit a **Pull Request** to the `master` branch

### Branch Naming

| Prefix | Purpose |
|--------|---------|
| `feat/` | New features |
| `fix/` | Bug fixes |
| `refactor/` | Refactoring (no behavior change) |
| `docs/` | Documentation only |
| `chore/` | Build, CI, toolchain |

### Conventions

- Keep plugins independent; no direct dependencies on other plugins
- Destructive operations must require user confirmation
- APIs follow RESTful style with the `/api/v1` prefix
- Make sure the backend starts and the frontend compiles before committing

## Community

---

Scan the QR code below with WeChat to join the ApeAdmin user group — report issues, share tips, and chat with other users and maintainers:

<p align="center">
  <img src="assets/wechat-group-qr.png" alt="WeChat User Group QR Code" width="220">
</p>