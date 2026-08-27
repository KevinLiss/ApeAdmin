"""Assign built-in legacy static assets only where a site has no custom image."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def set_default_assets(connection: AsyncConnection) -> None:
    """Fill blank defaults without overwriting configured logos or hero images."""
    await connection.execute(
        text(
            "UPDATE apehub_web_site_config "
            "SET site_logo = '/apehub-web/assets/logo.png' "
            "WHERE site_logo IS NULL OR TRIM(site_logo) = ''"
        )
    )
    await connection.execute(
        text(
            "UPDATE apehub_web_site_content "
            "SET image = '/apehub-web/assets/screenshot.png' "
            "WHERE block_key = 'hero' AND (image IS NULL OR TRIM(image) = '')"
        )
    )
