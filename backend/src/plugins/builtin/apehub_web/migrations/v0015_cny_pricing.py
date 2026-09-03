"""Add CNY pricing support: exchange rate config + order income in USDT + pay channel.

Schema changes (idempotent):
1. ``apehub_web_site_config.usdt_cny_rate``  - CNY/USDT exchange rate (Numeric 20,8, default 7.2)
2. ``apehub_web_order.developer_income_usdt`` - developer income recorded in USDT (Numeric 20,8, default 0)
3. ``apehub_web_order.pay_type``             - actual payment channel used (alipay/wxpay/usdt)
"""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection

DEFAULT_USDT_CNY_RATE = "7.2"


async def upgrade_cny_pricing(connection: AsyncConnection) -> None:
    # 1. site_config.usdt_cny_rate
    config_columns = await connection.run_sync(
        lambda sync_connection: {c["name"] for c in inspect(sync_connection).get_columns("apehub_web_site_config")}
    )
    if "usdt_cny_rate" not in config_columns:
        await connection.execute(
            text(
                f"ALTER TABLE apehub_web_site_config "
                f"ADD COLUMN usdt_cny_rate NUMERIC(20, 8) NOT NULL DEFAULT {DEFAULT_USDT_CNY_RATE}"
            )
        )
    # Backfill for rows where it stayed NULL (safety, some DBs ignore NOT NULL on ALTER).
    await connection.execute(
        text(
            "UPDATE apehub_web_site_config SET usdt_cny_rate = :rate "
            "WHERE usdt_cny_rate IS NULL OR usdt_cny_rate = 0"
        ),
        {"rate": DEFAULT_USDT_CNY_RATE},
    )

    # 2. order.developer_income_usdt + pay_type
    order_columns = await connection.run_sync(
        lambda sync_connection: {c["name"] for c in inspect(sync_connection).get_columns("apehub_web_order")}
    )
    if "developer_income_usdt" not in order_columns:
        await connection.execute(
            text(
                "ALTER TABLE apehub_web_order "
                "ADD COLUMN developer_income_usdt NUMERIC(20, 8) NOT NULL DEFAULT 0"
            )
        )
    if "pay_type" not in order_columns:
        await connection.execute(
            text(
                "ALTER TABLE apehub_web_order "
                "ADD COLUMN pay_type VARCHAR(16) NOT NULL DEFAULT ''"
            )
        )