"""Point existing sites at the VitePress portal and normalize the AI model."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def activate_docs_portal(connection: AsyncConnection) -> None:
    await connection.execute(
        text(
            "UPDATE apehub_web_navigation_item "
            "SET link = '/apehub-web/docs-portal/' "
            "WHERE link = '/apehub-web/docs.html'"
        )
    )
    await connection.execute(
        text(
            "UPDATE apehub_web_site_config SET deepseek_model = 'deepseek-chat' "
            "WHERE deepseek_model IS NULL OR deepseek_model = '' OR deepseek_model = 'deepseek-v4-pro'"
        )
    )
