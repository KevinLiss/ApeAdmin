"""One-time migration from the retired ApeUI schema to Apehub_web."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


TABLE_PAIRS = [
    ("apeui_site_config", "apehub_web_site_config"),
    ("apeui_site_content", "apehub_web_site_content"),
    ("apeui_doc_category", "apehub_web_doc_category"),
    ("apeui_doc", "apehub_web_doc"),
    ("apeui_profile", "apehub_web_profile"),
    ("apeui_plugin", "apehub_web_plugin"),
    ("apeui_plugin_file", "apehub_web_plugin_file"),
    ("apeui_plugin_demo", "apehub_web_plugin_demo"),
    ("apeui_order", "apehub_web_order"),
    ("apeui_income", "apehub_web_income"),
    ("apeui_withdrawal", "apehub_web_withdrawal"),
]


async def _has_rows(connection: AsyncConnection, table: str) -> bool:
    return bool((await connection.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))).scalar_one_or_none())


async def migrate_legacy_apeui_data(connection: AsyncConnection) -> None:
    """Copy the legacy schema once, preserving identifiers and relationships."""
    occupied = [target for _source, target in TABLE_PAIRS if await _has_rows(connection, target)]
    if occupied:
        raise RuntimeError(
            "检测到 apeui_* 历史数据且新的 apehub_web_* 表已有数据，"
            f"无法自动合并：{', '.join(occupied)}"
        )

    statements = [
        """INSERT INTO apehub_web_site_config
        (id, site_name, site_logo, site_domain, site_prefix, seo_title, seo_description, seo_keywords,
         mail_user, mail_code, mail_host, mail_port, lempay_pid, lempay_key, lempay_api_url,
         lempay_submit_url, lempay_notify_url, lempay_return_url, service_fee_rate, updated_at)
        SELECT id, site_name, site_logo, '', '/apehub-web', seo_title, seo_description, seo_keywords,
               smtp_user, smtp_pass, smtp_host, smtp_port, lempay_pid, lempay_key, lempay_api,
               '', '', '', service_fee_rate, CURRENT_TIMESTAMP
        FROM apeui_site_config""",
        """INSERT INTO apehub_web_site_content
        (id, block_key, title, subtitle, body, image, sort, enabled, extra, updated_at)
        SELECT id, block_key, title, subtitle, body, image, sort, enabled, extra, CURRENT_TIMESTAMP
        FROM apeui_site_content""",
        """INSERT INTO apehub_web_doc_category (id, name, description, sort, created_at)
        SELECT id, name, description, sort, CURRENT_TIMESTAMP FROM apeui_doc_category""",
        """INSERT INTO apehub_web_doc
        (id, category_id, title, slug, summary, body, version, author, published, sort, view_count, created_at, updated_at)
        SELECT id, category_id, title, slug, summary, body, version, '', published, sort, view_count, created_at, updated_at
        FROM apeui_doc""",
        """INSERT INTO apehub_web_profile
        (id, user_id, nickname, avatar, bio, is_developer, balance, frozen_balance, total_income, total_withdrawn, created_at)
        SELECT id, user_id, '', '', '', is_developer, balance, frozen_balance, total_income, total_withdrawn, created_at
        FROM apeui_profile""",
        """INSERT INTO apehub_web_plugin
        (id, developer_id, name, display_name, slug, description, category, version, tags, icon, price,
         service_fee_rate, status, download_count, rating_avg, rating_count, reject_reason, created_at, updated_at)
        SELECT id, developer_id, name, display_name, slug, description, category, version, tags, icon, price,
               service_fee_rate, status, download_count, rating_avg, 0, reject_reason, created_at, updated_at
        FROM apeui_plugin""",
        """INSERT INTO apehub_web_plugin_file
        (id, plugin_id, file_type, filename, stored_path, size, md5, created_at)
        SELECT id, plugin_id, file_type, filename, stored_path, size, md5, created_at FROM apeui_plugin_file""",
        """INSERT INTO apehub_web_plugin_demo
        (id, plugin_id, demo_type, title, url, qr_image, created_at)
        SELECT id, plugin_id, demo_type, title, url, qr_image, created_at FROM apeui_plugin_demo""",
        """INSERT INTO apehub_web_order
        (id, order_no, user_id, plugin_id, amount, service_fee, developer_income, status, lepay_trade_no, created_at, paid_at)
        SELECT id, order_no, user_id, plugin_id, amount, service_fee, developer_income, status, lepay_trade_no, created_at, paid_at
        FROM apeui_order""",
        """INSERT INTO apehub_web_income (id, order_id, user_id, plugin_id, amount, rate, created_at)
        SELECT id, order_id, user_id, plugin_id, amount, rate, created_at FROM apeui_income""",
        """INSERT INTO apehub_web_withdrawal
        (id, user_id, amount, method, account, status, remark, created_at, updated_at)
        SELECT id, user_id, amount, method, account, status, remark, created_at, created_at FROM apeui_withdrawal""",
    ]
    for statement in statements:
        await connection.execute(text(statement))
