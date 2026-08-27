"""Replace the only retired ApeUI default image path after the plugin rename."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def replace_legacy_asset_path(connection: AsyncConnection) -> None:
    """Move the known legacy bundled logo to its Apehub_web static location."""
    await connection.execute(
        text(
            "UPDATE apehub_web_site_config "
            "SET site_logo = '/apehub-web/assets/logo.png' "
            "WHERE site_logo = '/apeui/assets/logo.png'"
        )
    )
