import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.menu import update_menu
from src.core.deps import _build_menu_tree
from src.core.exceptions import ValidationException
from src.db import Base
from src.models import Menu
from src.schemas import MenuUpdate


@pytest.fixture
async def menu_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as db:
        yield db

    await engine.dispose()


@pytest.mark.asyncio
async def test_clearing_parent_moves_menu_to_root_and_clears_nullable_fields(menu_db):
    parent = Menu(name="系统管理", parent_id=0, type="M", path="/system")
    child = Menu(
        name="插件管理",
        parent_id=0,
        type="C",
        path="plugin",
        component="system/plugin/index",
        permission="system:plugin:list",
    )
    menu_db.add_all([parent, child])
    await menu_db.flush()
    child.parent_id = parent.id
    await menu_db.commit()

    await update_menu(
        child.id,
        MenuUpdate(parent_id=None, permission=None),
        menu_db,
        None,
    )

    await menu_db.refresh(child)
    assert child.parent_id == 0
    assert child.permission is None


@pytest.mark.asyncio
async def test_menu_cannot_be_moved_below_its_descendant(menu_db):
    root = Menu(name="系统管理", parent_id=0, type="M", path="/system")
    child = Menu(name="插件管理", parent_id=0, type="C", path="plugin")
    menu_db.add_all([root, child])
    await menu_db.flush()
    child.parent_id = root.id
    await menu_db.commit()

    with pytest.raises(ValidationException, match="当前菜单或其下级"):
        await update_menu(
            root.id,
            MenuUpdate(parent_id=child.id),
            menu_db,
            None,
        )


def test_menu_tree_includes_status_for_management_page():
    menu = Menu(name="插件管理", parent_id=0, type="C", status=1)
    menu.id = 1

    tree = _build_menu_tree([menu])

    assert tree[0]["status"] == 1
