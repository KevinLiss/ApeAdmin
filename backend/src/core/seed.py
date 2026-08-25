"""Seed initial data: super admin, default role, default menus.

Creates:
- 1 super admin user (admin / admin123)
- 1 default admin role with all menus
- Full menu tree matching the frontend routes (system:user, system:role, etc.)
"""

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.crypto import encrypt_api_key
from src.core.security import hash_password
from src.db import SessionLocal
from src.models import Dept, Menu, Role, User
from src.models.ai import AiProvider


async def seed_initial_data() -> None:
    """Seed the database with essential initial data if not already present."""
    async with SessionLocal() as db:
        await _seed_dept(db)
        await _seed_menus(db)
        await _seed_role(db)
        await _seed_super_admin(db)
        await _seed_ai_provider(db)
        await db.commit()
    logger.info("Initial data seeded")


async def _seed_dept(db: AsyncSession) -> None:
    """Create a default root department if none exists."""
    result = await db.execute(select(Dept).where(Dept.parent_id == 0))
    if result.scalars().first():
        return
    root = Dept(
        name="ApeAdmin",
        parent_id=0,
        sort=0,
        leader="admin",
        phone="",
        status=1,
    )
    db.add(root)
    await db.flush()
    logger.info("Created root department 'ApeAdmin'")


async def _seed_menus(db: AsyncSession) -> None:
    """Create the default system management menu tree."""
    # Check if any menus exist
    result = await db.execute(select(Menu).limit(1))
    if result.scalars().first():
        # Incremental seeding: add any missing MCP/AI sub-menus on existing installs
        await _seed_missing_menus(db)
        return

    menus_data = [
        # (name, parent_key, type, path, component, permission, icon, sort)
        # Dashboard (top-level)
        ("系统仪表盘", None, "C", "/dashboard-monitor", "apeui/dashboard/Monitor", None, "Monitor", 1),
        # UI Components (top-level directory, children are static frontend pages)
        # path="" so resolvePath skips parent prefix; children paths are already full (e.g. dashboard-1, apeui/app/projects)
        ("Apeadmin 样式库", None, "M", "", None, None, "Grid", 99),
        ("仪表盘样式1", "Apeadmin 样式库", "C", "dashboard-1", "apeui/dashboard/Default", None, "Odometer", 1),
        ("仪表盘样式2", "Apeadmin 样式库", "C", "dashboard-2", "apeui/dashboard/Ecommerce", None, "DataAnalysis", 2),
        ("项目列表", "Apeadmin 样式库", "C", "apeui/app/projects", "apeui/applications/Projects", None, "Folder", 3),
        ("新建项目", "Apeadmin 样式库", "C", "apeui/app/project-create", "apeui/applications/ProjectCreate", None, "FolderAdd", 4),
        ("文件管理", "Apeadmin 样式库", "C", "apeui/app/file-manager", "apeui/applications/FileManager", None, "Document", 5),
        ("看板视图", "Apeadmin 样式库", "C", "apeui/app/kanban", "apeui/applications/Kanban", None, "Grid", 6),
        ("书签管理", "Apeadmin 样式库", "C", "apeui/app/bookmark", "apeui/applications/Bookmark", None, "Collection", 7),
        ("通讯录", "Apeadmin 样式库", "C", "apeui/app/contacts", "apeui/applications/Contacts", None, "Phone", 8),
        ("任务列表", "Apeadmin 样式库", "C", "apeui/app/tasks", "apeui/applications/Tasks", None, "List", 9),
        ("日历", "Apeadmin 样式库", "C", "apeui/app/calendar", "apeui/applications/CalendarBasic", None, "Calendar", 10),
        ("社交应用", "Apeadmin 样式库", "C", "apeui/app/social", "apeui/applications/SocialApp", None, "ChatDotSquare", 11),
        ("待办事项", "Apeadmin 样式库", "C", "apeui/app/todo", "apeui/applications/Todo", None, "Checked", 12),
        ("搜索结果", "Apeadmin 样式库", "C", "apeui/app/search", "apeui/applications/SearchResult", None, "Search", 13),
        ("聊天应用", "Apeadmin 样式库", "C", "apeui/app/chat", "apeui/applications/ChatApp", None, "ChatLineSquare", 14),
        ("视频聊天", "Apeadmin 样式库", "C", "apeui/app/chat-video", "apeui/applications/ChatVideo", None, "VideoCamera", 15),
        ("商品管理", "Apeadmin 样式库", "C", "apeui/ecommerce/product", "apeui/ecommerce/Product", None, "Goods", 16),
        ("商品详情页", "Apeadmin 样式库", "C", "apeui/ecommerce/product-page", "apeui/ecommerce/ProductPage", None, "GoodsFilled", 17),
        ("添加商品", "Apeadmin 样式库", "C", "apeui/ecommerce/add-product", "apeui/ecommerce/AddProduct", None, "CirclePlus", 18),
        ("商品列表", "Apeadmin 样式库", "C", "apeui/ecommerce/product-list", "apeui/ecommerce/ProductList", None, "List", 19),
        ("支付详情", "Apeadmin 样式库", "C", "apeui/ecommerce/payment", "apeui/ecommerce/PaymentDetails", None, "CreditCard", 20),
        ("订单历史", "Apeadmin 样式库", "C", "apeui/ecommerce/order-history", "apeui/ecommerce/OrderHistory", None, "Timer", 21),
        ("发票模板", "Apeadmin 样式库", "C", "apeui/ecommerce/invoice", "apeui/ecommerce/InvoiceTemplate", None, "Tickets", 22),
        ("购物车", "Apeadmin 样式库", "C", "apeui/ecommerce/cart", "apeui/ecommerce/Cart", None, "ShoppingCart", 23),
        ("心愿单", "Apeadmin 样式库", "C", "apeui/ecommerce/wishlist", "apeui/ecommerce/Wishlist", None, "StarFilled", 24),
        ("结算页面", "Apeadmin 样式库", "C", "apeui/ecommerce/checkout", "apeui/ecommerce/Checkout", None, "ShoppingCartFull", 25),
        ("定价方案", "Apeadmin 样式库", "C", "apeui/ecommerce/pricing", "apeui/ecommerce/Pricing", None, "Ticket", 26),
        ("用户资料", "Apeadmin 样式库", "C", "apeui/users/profile", "apeui/users/UserProfile", None, "User", 27),
        ("编辑资料", "Apeadmin 样式库", "C", "apeui/users/edit-profile", "apeui/users/EditProfile", None, "Edit", 28),
        ("用户卡片", "Apeadmin 样式库", "C", "apeui/users/cards", "apeui/users/UserCards", None, "Postcard", 29),
        ("状态颜色", "Apeadmin 样式库", "C", "apeui/components/state-color", "apeui/components/pages/StateColor", None, "Brush", 30),
        ("排版样式", "Apeadmin 样式库", "C", "apeui/components/typography", "apeui/components/pages/Typography", None, "Document", 31),
        ("头像", "Apeadmin 样式库", "C", "apeui/components/avatars", "apeui/components/pages/Avatars", None, "Avatar", 32),
        ("栅格布局", "Apeadmin 样式库", "C", "apeui/components/grid", "apeui/components/pages/Grid", None, "Grid", 33),
        ("阴影效果", "Apeadmin 样式库", "C", "apeui/components/box-shadow", "apeui/components/pages/BoxShadow", None, "Box", 34),
        ("按钮", "Apeadmin 样式库", "C", "apeui/components/buttons", "apeui/components/pages/Buttons", None, "Pointer", 35),
        ("按钮组", "Apeadmin 样式库", "C", "apeui/components/button-group", "apeui/components/pages/ButtonGroup", None, "Pointer", 36),
        ("标签与胶囊", "Apeadmin 样式库", "C", "apeui/components/tag-pills", "apeui/components/pages/TagPills", None, "CollectionTag", 37),
        ("进度条", "Apeadmin 样式库", "C", "apeui/components/progress-bar", "apeui/components/pages/ProgressBar", None, "Histogram", 38),
        ("模态框", "Apeadmin 样式库", "C", "apeui/components/modal", "apeui/components/pages/Modal", None, "Box", 39),
        ("警告提示", "Apeadmin 样式库", "C", "apeui/components/alert", "apeui/components/pages/Alert", None, "Warning", 40),
        ("气泡卡片", "Apeadmin 样式库", "C", "apeui/components/popover", "apeui/components/pages/Popover", None, "ChatLineSquare", 41),
        ("文字提示", "Apeadmin 样式库", "C", "apeui/components/tooltip", "apeui/components/pages/Tooltip", None, "InfoFilled", 42),
        ("下拉菜单", "Apeadmin 样式库", "C", "apeui/components/dropdown", "apeui/components/pages/Dropdown", None, "ArrowDown", 43),
        ("折叠面板", "Apeadmin 样式库", "C", "apeui/components/accordion", "apeui/components/pages/Accordion", None, "Fold", 44),
        ("ApeAdmin 标签页", "Apeadmin 样式库", "C", "apeui/components/tabs-bootstrap", "apeui/components/pages/TabsBootstrap", None, "Document", 45),
        ("线型标签页", "Apeadmin 样式库", "C", "apeui/components/tabs-line", "apeui/components/pages/TabsLine", None, "Document", 46),
        ("列表", "Apeadmin 样式库", "C", "apeui/components/list", "apeui/components/pages/List", None, "List", 47),
        ("滚动区域", "Apeadmin 样式库", "C", "apeui/components/scrollable", "apeui/components/pages/Scrollable", None, "Scroll", 48),
        ("树形视图", "Apeadmin 样式库", "C", "apeui/components/tree", "apeui/components/pages/Tree", None, "Connection", 49),
        ("评分", "Apeadmin 样式库", "C", "apeui/components/rating", "apeui/components/pages/Rating", None, "StarFilled", 50),
        ("弹窗提示", "Apeadmin 样式库", "C", "apeui/components/sweet-alert2", "apeui/components/pages/SweetAlert2", None, "Warning", 51),
        ("分页", "Apeadmin 样式库", "C", "apeui/components/pagination", "apeui/components/pages/Pagination", None, "Document", 52),
        ("面包屑", "Apeadmin 样式库", "C", "apeui/components/breadcrumb", "apeui/components/pages/Breadcrumb", None, "Rank", 53),
        ("范围滑块", "Apeadmin 样式库", "C", "apeui/components/range-slider", "apeui/components/pages/RangeSlider", None, "Slider", 54),
        ("基础卡片", "Apeadmin 样式库", "C", "apeui/components/basic-card", "apeui/components/pages/BasicCard", None, "Postcard", 55),
        ("创意卡片", "Apeadmin 样式库", "C", "apeui/components/creative-card", "apeui/components/pages/CreativeCard", None, "Postcard", 56),
        ("标签页卡片", "Apeadmin 样式库", "C", "apeui/components/tabbed-card", "apeui/components/pages/TabbedCard", None, "Postcard", 57),
        ("可拖拽卡片", "Apeadmin 样式库", "C", "apeui/components/dragable-card", "apeui/components/pages/DragableCard", None, "Postcard", 58),
        ("时间轴一", "Apeadmin 样式库", "C", "apeui/components/timeline-1", "apeui/components/pages/Timeline1", None, "Timer", 59),
        ("时间轴二", "Apeadmin 样式库", "C", "apeui/components/timeline-2", "apeui/components/pages/Timeline2", None, "Timer", 60),
        ("Apex 图表", "Apeadmin 样式库", "C", "apeui/components/chart-apex", "apeui/components/pages/ChartApex", None, "TrendCharts", 61),
        ("Google 图表", "Apeadmin 样式库", "C", "apeui/components/chart-google", "apeui/components/pages/ChartGoogle", None, "TrendCharts", 62),
        ("迷你走势图", "Apeadmin 样式库", "C", "apeui/components/chart-sparkline", "apeui/components/pages/ChartSparkline", None, "TrendCharts", 63),
        ("Flot 图表", "Apeadmin 样式库", "C", "apeui/components/chart-flot", "apeui/components/pages/ChartFlot", None, "TrendCharts", 64),
        ("旋钮图表", "Apeadmin 样式库", "C", "apeui/components/chart-knob", "apeui/components/pages/ChartKnob", None, "TrendCharts", 65),
        ("Morris 图表", "Apeadmin 样式库", "C", "apeui/components/chart-morris", "apeui/components/pages/ChartMorris", None, "TrendCharts", 66),
        ("Chart.js 图表", "Apeadmin 样式库", "C", "apeui/components/chartjs", "apeui/components/pages/Chartjs", None, "TrendCharts", 67),
        ("Chartist 图表", "Apeadmin 样式库", "C", "apeui/components/chartist", "apeui/components/pages/Chartist", None, "TrendCharts", 68),
        ("Peity 图表", "Apeadmin 样式库", "C", "apeui/components/chart-peity", "apeui/components/pages/ChartPeity", None, "TrendCharts", 69),
        ("国旗图标", "Apeadmin 样式库", "C", "apeui/components/flag-icon", "apeui/components/pages/FlagIcon", None, "Flag", 70),
        ("Font Awesome 图标", "Apeadmin 样式库", "C", "apeui/components/font-awesome", "apeui/components/pages/FontAwesome", None, "StarFilled", 71),
        ("Ico 图标", "Apeadmin 样式库", "C", "apeui/components/ico-icon", "apeui/components/pages/IcoIcon", None, "StarFilled", 72),
        ("Themify 图标", "Apeadmin 样式库", "C", "apeui/components/themify-icon", "apeui/components/pages/ThemifyIcon", None, "StarFilled", 73),
        ("Feather 图标", "Apeadmin 样式库", "C", "apeui/components/feather-icon", "apeui/components/pages/FeatherIcon", None, "Sunny", 74),
        # System management
        ("系统管理", None, "M", "/system", None, None, "Setting", 10),
        ("用户管理", "系统管理", "C", "user", "system/user/index", "system:user:list", "User", 1),
        ("新增用户", "用户管理", "F", None, None, "system:user:add", None, 1),
        ("编辑用户", "用户管理", "F", None, None, "system:user:edit", None, 2),
        ("删除用户", "用户管理", "F", None, None, "system:user:delete", None, 3),
        ("重置密码", "用户管理", "F", None, None, "system:user:reset-password", None, 4),
        ("角色管理", "系统管理", "C", "role", "system/role/index", "system:role:list", "UserFilled", 2),
        ("新增角色", "角色管理", "F", None, None, "system:role:add", None, 1),
        ("编辑角色", "角色管理", "F", None, None, "system:role:edit", None, 2),
        ("删除角色", "角色管理", "F", None, None, "system:role:delete", None, 3),
        ("菜单管理", "系统管理", "C", "menu", "system/menu/index", "system:menu:list", "Menu", 3),
        ("新增菜单", "菜单管理", "F", None, None, "system:menu:add", None, 1),
        ("编辑菜单", "菜单管理", "F", None, None, "system:menu:edit", None, 2),
        ("删除菜单", "菜单管理", "F", None, None, "system:menu:delete", None, 3),
        ("部门管理", "系统管理", "C", "dept", "system/dept/index", "system:dept:list", "OfficeBuilding", 4),
        ("新增部门", "部门管理", "F", None, None, "system:dept:add", None, 1),
        ("编辑部门", "部门管理", "F", None, None, "system:dept:edit", None, 2),
        ("删除部门", "部门管理", "F", None, None, "system:dept:delete", None, 3),
        ("插件管理", "系统管理", "C", "plugin", "system/plugin/index", "system:plugin:list", "Box", 5),
        ("启用/禁用插件", "插件管理", "F", None, None, "system:plugin:toggle", None, 1),
        ("插件配置", "插件管理", "F", None, None, "system:plugin:config", None, 2),
        # System log
        ("系统日志", "系统管理", "C", "log", "system/log/index", "system:log:list", "Document", 6),
        ("删除日志", "系统日志", "F", None, None, "system:log:delete", None, 1),
        # MCP menu
        ("MCP 管理", None, "M", "/mcp", None, None, "Connection", 20),
        ("工具列表", "MCP 管理", "C", "tools", "mcp/tools", "mcp:tools:list", "Tools", 1),
        ("资源列表", "MCP 管理", "C", "resources", "mcp/resources", "mcp:resources:list", "FolderOpened", 2),
        # AI module menu
        ("AI 助手", None, "M", "/ai", None, None, "ChatDotRound", 30),
        ("AI 全能助手", "AI 助手", "C", "chat", "ai/chat/index", "ai:chat", "ChatLineRound", 1),
        ("模型密钥管理", "AI 助手", "C", "providers", "ai/providers/index", "ai:provider:list", "Key", 2),
        ("新增模型密钥", "模型密钥管理", "F", None, None, "ai:provider:add", None, 1),
        ("编辑模型密钥", "模型密钥管理", "F", None, None, "ai:provider:edit", None, 2),
        ("删除模型密钥", "模型密钥管理", "F", None, None, "ai:provider:delete", None, 3),
    ]

    # Track created menus by name for parent linking
    name_to_menu: dict[str, Menu] = {}

    for name, parent_name, mtype, path, component, permission, icon, sort in menus_data:
        parent_id = name_to_menu[parent_name].id if parent_name and parent_name in name_to_menu else 0
        menu = Menu(
            name=name,
            parent_id=parent_id,
            type=mtype,
            path=path,
            component=component,
            permission=permission,
            icon=icon,
            sort=sort,
            visible=1,
            status=1,
        )
        db.add(menu)
        await db.flush()  # Get the ID
        name_to_menu[name] = menu

    logger.info(f"Created {len(menus_data)} menu items")


async def _seed_missing_menus(db: AsyncSession) -> None:
    """Idempotently add menus that were introduced after the initial seed.

    Handles upgrades of existing installs: checks by name + parent, only inserts missing rows.
    """
    existing = await db.execute(select(Menu))
    existing_menus = list(existing.scalars().all())

    def find(name: str, parent_name: str | None = None) -> Menu | None:
        """Find a menu by name (optionally scoped to a parent's name).

        Parent lookup is name-based across any tree level (not restricted to
        top-level menus), so sub-menus like '工具列表' or 'AI 全能助手' can be
        used as parents for button-level (F) permission entries.
        """
        if parent_name is None:
            return next((m for m in existing_menus if m.name == name and m.parent_id == 0), None)
        parent = next((m for m in existing_menus if m.name == parent_name), None)
        if not parent:
            return None
        return next((m for m in existing_menus if m.name == name and m.parent_id == parent.id), None)

    # (name, parent_name, type, path, component, permission, icon, sort)
    missing_menus = [
        # Dashboard and UI Components (top-level)
        ("系统仪表盘", None, "C", "/dashboard-monitor", "apeui/dashboard/Monitor", None, "Monitor", 1),
        ("Apeadmin 样式库", None, "M", "", None, None, "Grid", 99),
        ("仪表盘样式1", "Apeadmin 样式库", "C", "dashboard-1", "apeui/dashboard/Default", None, "Odometer", 1),
        ("仪表盘样式2", "Apeadmin 样式库", "C", "dashboard-2", "apeui/dashboard/Ecommerce", None, "DataAnalysis", 2),
        ("项目列表", "Apeadmin 样式库", "C", "apeui/app/projects", "apeui/applications/Projects", None, "Folder", 3),
        ("新建项目", "Apeadmin 样式库", "C", "apeui/app/project-create", "apeui/applications/ProjectCreate", None, "FolderAdd", 4),
        ("文件管理", "Apeadmin 样式库", "C", "apeui/app/file-manager", "apeui/applications/FileManager", None, "Document", 5),
        ("看板视图", "Apeadmin 样式库", "C", "apeui/app/kanban", "apeui/applications/Kanban", None, "Grid", 6),
        ("书签管理", "Apeadmin 样式库", "C", "apeui/app/bookmark", "apeui/applications/Bookmark", None, "Collection", 7),
        ("通讯录", "Apeadmin 样式库", "C", "apeui/app/contacts", "apeui/applications/Contacts", None, "Phone", 8),
        ("任务列表", "Apeadmin 样式库", "C", "apeui/app/tasks", "apeui/applications/Tasks", None, "List", 9),
        ("日历", "Apeadmin 样式库", "C", "apeui/app/calendar", "apeui/applications/CalendarBasic", None, "Calendar", 10),
        ("社交应用", "Apeadmin 样式库", "C", "apeui/app/social", "apeui/applications/SocialApp", None, "ChatDotSquare", 11),
        ("待办事项", "Apeadmin 样式库", "C", "apeui/app/todo", "apeui/applications/Todo", None, "Checked", 12),
        ("搜索结果", "Apeadmin 样式库", "C", "apeui/app/search", "apeui/applications/SearchResult", None, "Search", 13),
        ("聊天应用", "Apeadmin 样式库", "C", "apeui/app/chat", "apeui/applications/ChatApp", None, "ChatLineSquare", 14),
        ("视频聊天", "Apeadmin 样式库", "C", "apeui/app/chat-video", "apeui/applications/ChatVideo", None, "VideoCamera", 15),
        ("商品管理", "Apeadmin 样式库", "C", "apeui/ecommerce/product", "apeui/ecommerce/Product", None, "Goods", 16),
        ("商品详情页", "Apeadmin 样式库", "C", "apeui/ecommerce/product-page", "apeui/ecommerce/ProductPage", None, "GoodsFilled", 17),
        ("添加商品", "Apeadmin 样式库", "C", "apeui/ecommerce/add-product", "apeui/ecommerce/AddProduct", None, "CirclePlus", 18),
        ("商品列表", "Apeadmin 样式库", "C", "apeui/ecommerce/product-list", "apeui/ecommerce/ProductList", None, "List", 19),
        ("支付详情", "Apeadmin 样式库", "C", "apeui/ecommerce/payment", "apeui/ecommerce/PaymentDetails", None, "CreditCard", 20),
        ("订单历史", "Apeadmin 样式库", "C", "apeui/ecommerce/order-history", "apeui/ecommerce/OrderHistory", None, "Timer", 21),
        ("发票模板", "Apeadmin 样式库", "C", "apeui/ecommerce/invoice", "apeui/ecommerce/InvoiceTemplate", None, "Tickets", 22),
        ("购物车", "Apeadmin 样式库", "C", "apeui/ecommerce/cart", "apeui/ecommerce/Cart", None, "ShoppingCart", 23),
        ("心愿单", "Apeadmin 样式库", "C", "apeui/ecommerce/wishlist", "apeui/ecommerce/Wishlist", None, "StarFilled", 24),
        ("结算页面", "Apeadmin 样式库", "C", "apeui/ecommerce/checkout", "apeui/ecommerce/Checkout", None, "ShoppingCartFull", 25),
        ("定价方案", "Apeadmin 样式库", "C", "apeui/ecommerce/pricing", "apeui/ecommerce/Pricing", None, "Ticket", 26),
        ("用户资料", "Apeadmin 样式库", "C", "apeui/users/profile", "apeui/users/UserProfile", None, "User", 27),
        ("编辑资料", "Apeadmin 样式库", "C", "apeui/users/edit-profile", "apeui/users/EditProfile", None, "Edit", 28),
        ("用户卡片", "Apeadmin 样式库", "C", "apeui/users/cards", "apeui/users/UserCards", None, "Postcard", 29),
        ("状态颜色", "Apeadmin 样式库", "C", "apeui/components/state-color", "apeui/components/pages/StateColor", None, "Brush", 30),
        ("排版样式", "Apeadmin 样式库", "C", "apeui/components/typography", "apeui/components/pages/Typography", None, "Document", 31),
        ("头像", "Apeadmin 样式库", "C", "apeui/components/avatars", "apeui/components/pages/Avatars", None, "Avatar", 32),
        ("栅格布局", "Apeadmin 样式库", "C", "apeui/components/grid", "apeui/components/pages/Grid", None, "Grid", 33),
        ("阴影效果", "Apeadmin 样式库", "C", "apeui/components/box-shadow", "apeui/components/pages/BoxShadow", None, "Box", 34),
        ("按钮", "Apeadmin 样式库", "C", "apeui/components/buttons", "apeui/components/pages/Buttons", None, "Pointer", 35),
        ("按钮组", "Apeadmin 样式库", "C", "apeui/components/button-group", "apeui/components/pages/ButtonGroup", None, "Pointer", 36),
        ("标签与胶囊", "Apeadmin 样式库", "C", "apeui/components/tag-pills", "apeui/components/pages/TagPills", None, "CollectionTag", 37),
        ("进度条", "Apeadmin 样式库", "C", "apeui/components/progress-bar", "apeui/components/pages/ProgressBar", None, "Histogram", 38),
        ("模态框", "Apeadmin 样式库", "C", "apeui/components/modal", "apeui/components/pages/Modal", None, "Box", 39),
        ("警告提示", "Apeadmin 样式库", "C", "apeui/components/alert", "apeui/components/pages/Alert", None, "Warning", 40),
        ("气泡卡片", "Apeadmin 样式库", "C", "apeui/components/popover", "apeui/components/pages/Popover", None, "ChatLineSquare", 41),
        ("文字提示", "Apeadmin 样式库", "C", "apeui/components/tooltip", "apeui/components/pages/Tooltip", None, "InfoFilled", 42),
        ("下拉菜单", "Apeadmin 样式库", "C", "apeui/components/dropdown", "apeui/components/pages/Dropdown", None, "ArrowDown", 43),
        ("折叠面板", "Apeadmin 样式库", "C", "apeui/components/accordion", "apeui/components/pages/Accordion", None, "Fold", 44),
        ("ApeAdmin 标签页", "Apeadmin 样式库", "C", "apeui/components/tabs-bootstrap", "apeui/components/pages/TabsBootstrap", None, "Document", 45),
        ("线型标签页", "Apeadmin 样式库", "C", "apeui/components/tabs-line", "apeui/components/pages/TabsLine", None, "Document", 46),
        ("列表", "Apeadmin 样式库", "C", "apeui/components/list", "apeui/components/pages/List", None, "List", 47),
        ("滚动区域", "Apeadmin 样式库", "C", "apeui/components/scrollable", "apeui/components/pages/Scrollable", None, "Scroll", 48),
        ("树形视图", "Apeadmin 样式库", "C", "apeui/components/tree", "apeui/components/pages/Tree", None, "Connection", 49),
        ("评分", "Apeadmin 样式库", "C", "apeui/components/rating", "apeui/components/pages/Rating", None, "StarFilled", 50),
        ("弹窗提示", "Apeadmin 样式库", "C", "apeui/components/sweet-alert2", "apeui/components/pages/SweetAlert2", None, "Warning", 51),
        ("分页", "Apeadmin 样式库", "C", "apeui/components/pagination", "apeui/components/pages/Pagination", None, "Document", 52),
        ("面包屑", "Apeadmin 样式库", "C", "apeui/components/breadcrumb", "apeui/components/pages/Breadcrumb", None, "Rank", 53),
        ("范围滑块", "Apeadmin 样式库", "C", "apeui/components/range-slider", "apeui/components/pages/RangeSlider", None, "Slider", 54),
        ("基础卡片", "Apeadmin 样式库", "C", "apeui/components/basic-card", "apeui/components/pages/BasicCard", None, "Postcard", 55),
        ("创意卡片", "Apeadmin 样式库", "C", "apeui/components/creative-card", "apeui/components/pages/CreativeCard", None, "Postcard", 56),
        ("标签页卡片", "Apeadmin 样式库", "C", "apeui/components/tabbed-card", "apeui/components/pages/TabbedCard", None, "Postcard", 57),
        ("可拖拽卡片", "Apeadmin 样式库", "C", "apeui/components/dragable-card", "apeui/components/pages/DragableCard", None, "Postcard", 58),
        ("时间轴一", "Apeadmin 样式库", "C", "apeui/components/timeline-1", "apeui/components/pages/Timeline1", None, "Timer", 59),
        ("时间轴二", "Apeadmin 样式库", "C", "apeui/components/timeline-2", "apeui/components/pages/Timeline2", None, "Timer", 60),
        ("Apex 图表", "Apeadmin 样式库", "C", "apeui/components/chart-apex", "apeui/components/pages/ChartApex", None, "TrendCharts", 61),
        ("Google 图表", "Apeadmin 样式库", "C", "apeui/components/chart-google", "apeui/components/pages/ChartGoogle", None, "TrendCharts", 62),
        ("迷你走势图", "Apeadmin 样式库", "C", "apeui/components/chart-sparkline", "apeui/components/pages/ChartSparkline", None, "TrendCharts", 63),
        ("Flot 图表", "Apeadmin 样式库", "C", "apeui/components/chart-flot", "apeui/components/pages/ChartFlot", None, "TrendCharts", 64),
        ("旋钮图表", "Apeadmin 样式库", "C", "apeui/components/chart-knob", "apeui/components/pages/ChartKnob", None, "TrendCharts", 65),
        ("Morris 图表", "Apeadmin 样式库", "C", "apeui/components/chart-morris", "apeui/components/pages/ChartMorris", None, "TrendCharts", 66),
        ("Chart.js 图表", "Apeadmin 样式库", "C", "apeui/components/chartjs", "apeui/components/pages/Chartjs", None, "TrendCharts", 67),
        ("Chartist 图表", "Apeadmin 样式库", "C", "apeui/components/chartist", "apeui/components/pages/Chartist", None, "TrendCharts", 68),
        ("Peity 图表", "Apeadmin 样式库", "C", "apeui/components/chart-peity", "apeui/components/pages/ChartPeity", None, "TrendCharts", 69),
        ("国旗图标", "Apeadmin 样式库", "C", "apeui/components/flag-icon", "apeui/components/pages/FlagIcon", None, "Flag", 70),
        ("Font Awesome 图标", "Apeadmin 样式库", "C", "apeui/components/font-awesome", "apeui/components/pages/FontAwesome", None, "StarFilled", 71),
        ("Ico 图标", "Apeadmin 样式库", "C", "apeui/components/ico-icon", "apeui/components/pages/IcoIcon", None, "StarFilled", 72),
        ("Themify 图标", "Apeadmin 样式库", "C", "apeui/components/themify-icon", "apeui/components/pages/ThemifyIcon", None, "StarFilled", 73),
        ("Feather 图标", "Apeadmin 样式库", "C", "apeui/components/feather-icon", "apeui/components/pages/FeatherIcon", None, "Sunny", 74),
        # MCP management additions
        ("提示词列表", "MCP 管理", "C", "prompts", "mcp/prompts", "mcp:prompts:list", "ChatLineSquare", 3),
        ("调用工具", "工具列表", "F", None, None, "mcp:tools:call", None, 1),
        ("调用日志", "MCP 管理", "C", "audit-logs", "mcp/audit-logs", "mcp:audit:list", "List", 4),
        # AI module button-level permissions
        ("调用AI对话", "AI 全能助手", "F", None, None, "ai:chat:call", None, 1),
        # System log menu (incremental)
        ("系统日志", "系统管理", "C", "log", "system/log/index", "system:log:list", "Document", 6),
        ("删除日志", "系统日志", "F", None, None, "system:log:delete", None, 1),
    ]

    added = 0
    for name, parent_name, mtype, path, component, permission, icon, sort in missing_menus:
        # Determine parent (any level, not just top-level menus)
        parent_menu: Menu | None = None
        if parent_name:
            parent_menu = next((m for m in existing_menus if m.name == parent_name), None)
            if parent_menu is None:
                logger.warning(f"Skip menu '{name}': parent '{parent_name}' not found")
                continue

        pid = parent_menu.id if parent_menu else 0

        # Skip if already exists (by parent id)
        dup = any(m.name == name and m.parent_id == pid for m in existing_menus)
        if dup:
            continue

        menu = Menu(
            name=name,
            parent_id=pid,
            type=mtype,
            path=path,
            component=component,
            permission=permission,
            icon=icon,
            sort=sort,
            visible=1,
            status=1,
        )
        db.add(menu)
        await db.flush()
        existing_menus.append(menu)
        added += 1

    if added:
        logger.info(f"Added {added} missing menu items")
        # Bind new menus to the admin role so they are accessible
        from sqlalchemy import select as sa_select
        admin_role = await db.execute(sa_select(Role).where(Role.code == "admin"))
        role = admin_role.scalars().first()
        if role:
            # Get all menu IDs currently bound to the role
            bound_ids = {m.id for m in role.menus}
            # Add any new menus that aren't bound yet
            new_menus = [m for m in existing_menus if m.id not in bound_ids]
            if new_menus:
                role.menus = list(role.menus) + new_menus
                await db.flush()
                logger.info(f"Bound {len(new_menus)} new menus to admin role")


async def _seed_role(db: AsyncSession) -> None:
    """Create a default admin role with all menus."""
    result = await db.execute(select(Role).where(Role.code == "admin"))
    if result.scalars().first():
        return

    all_menus = await db.execute(select(Menu))
    menus = list(all_menus.scalars().all())

    role = Role(
        name="超级管理员",
        code="admin",
        data_scope=4,  # All data
        sort=1,
        status=1,
        remark="系统内置超级管理员角色",
    )
    role.menus = menus
    db.add(role)
    await db.flush()
    logger.info("Created role '超级管理员'")


async def _seed_super_admin(db: AsyncSession) -> None:
    """Create the super admin user."""
    result = await db.execute(select(User).where(User.username == settings.SUPER_ADMIN_USERNAME))
    if result.scalars().first():
        return

    # Get dept
    dept_result = await db.execute(select(Dept).where(Dept.name == "ApeAdmin"))
    dept = dept_result.scalars().first()

    # Get admin role
    role_result = await db.execute(select(Role).where(Role.code == "admin"))
    role = role_result.scalars().first()

    user = User(
        username=settings.SUPER_ADMIN_USERNAME,
        nickname="超级管理员",
        password=hash_password(settings.SUPER_ADMIN_PASSWORD),
        email="admin@apeadmin.local",
        phone="",
        dept_id=dept.id if dept else None,
        status=1,
    )
    if role:
        user.roles = [role]

    db.add(user)
    await db.flush()
    logger.info(f"Created super admin user '{settings.SUPER_ADMIN_USERNAME}'")


async def _seed_ai_provider(db: AsyncSession) -> None:
    """Seed a default DeepSeek provider so the user just needs to fill in the API Key."""
    result = await db.execute(select(AiProvider).where(AiProvider.name == "DeepSeek-V4Pro"))
    if result.scalars().first():
        return

    import json

    provider = AiProvider(
        name="DeepSeek-V4Pro",
        provider_type="deepseek",
        api_key_enc=encrypt_api_key("sk-placeholder"),
        base_url="https://api.deepseek.com",
        models=json.dumps(["deepseek-chat", "deepseek-reasoner"], ensure_ascii=False),
        enabled=1,
        sort=1,
        remark="默认供应商，请编辑后填入真实 API Key",
    )
    db.add(provider)
    await db.flush()
    logger.info("Created default AI provider 'DeepSeek-V4Pro'")
