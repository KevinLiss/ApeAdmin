"""Production marketplace foundation: encrypted secrets, USDT money, versions and ledger."""

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.core.crypto import decrypt_api_key, encrypt_api_key


async def _column_names(connection: AsyncConnection, table: str) -> set[str]:
    return await connection.run_sync(
        lambda sync_connection: {
            column["name"] for column in inspect(sync_connection).get_columns(table)
        }
    )


async def _add_columns(
    connection: AsyncConnection,
    table: str,
    definitions: dict[str, str],
) -> None:
    existing = await _column_names(connection, table)
    for name, definition in definitions.items():
        if name not in existing:
            await connection.execute(
                text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
            )


def _encrypt_legacy_secret(value: str | None) -> str:
    if not value:
        return ""
    try:
        decrypt_api_key(value)
        return value
    except Exception:
        return encrypt_api_key(value)


async def add_marketplace_foundation(connection: AsyncConnection) -> None:
    """Upgrade existing plugin data without deleting marketplace or financial history."""
    text_secret = "VARCHAR(1024) NOT NULL DEFAULT ''"
    await _add_columns(
        connection,
        "apehub_web_site_config",
        {
            "lempay_payment_type": "VARCHAR(16) NOT NULL DEFAULT 'usdt'",
            "deepseek_api_key": text_secret,
            "deepseek_base_url": "VARCHAR(255) NOT NULL DEFAULT 'https://api.deepseek.com'",
            "deepseek_model": "VARCHAR(64) NOT NULL DEFAULT 'deepseek-chat'",
            "currency": "VARCHAR(8) NOT NULL DEFAULT 'USDT'",
            "settlement_days": "INTEGER NOT NULL DEFAULT 7",
            "refund_days": "INTEGER NOT NULL DEFAULT 7",
            "min_withdrawal": "DECIMAL(20,8) NOT NULL DEFAULT 100",
            "withdrawal_fee_type": "VARCHAR(16) NOT NULL DEFAULT 'fixed'",
            "withdrawal_fee_value": "DECIMAL(20,8) NOT NULL DEFAULT 0",
        },
    )
    await _add_columns(
        connection,
        "apehub_web_plugin_file",
        {"version_id": "INTEGER NULL"},
    )
    await _add_columns(
        connection,
        "apehub_web_order",
        {
            "currency": "VARCHAR(8) NOT NULL DEFAULT 'USDT'",
            "refunded_at": "DATETIME NULL",
            "refund_reason": "VARCHAR(500) NOT NULL DEFAULT ''",
        },
    )
    await _add_columns(
        connection,
        "apehub_web_income",
        {
            "available_at": "DATETIME NULL",
            "status": "VARCHAR(16) NOT NULL DEFAULT 'pending'",
        },
    )
    await _add_columns(
        connection,
        "apehub_web_withdrawal",
        {
            "fee": "DECIMAL(20,8) NOT NULL DEFAULT 0",
            "net_amount": "DECIMAL(20,8) NOT NULL DEFAULT 0",
            "network": "VARCHAR(16) NOT NULL DEFAULT 'TRC20'",
            "tx_hash": "VARCHAR(128) NOT NULL DEFAULT ''",
            "reviewer_id": "INTEGER NULL",
            "reviewed_at": "DATETIME NULL",
            "paid_at": "DATETIME NULL",
        },
    )

    # Existing installations become a first version without changing public visibility.
    plugins = (
        await connection.execute(
            text("SELECT id, version, status FROM apehub_web_plugin ORDER BY id")
        )
    ).mappings().all()
    for plugin in plugins:
        existing = (
            await connection.execute(
                text(
                    "SELECT id FROM apehub_web_plugin_version "
                    "WHERE plugin_id = :plugin_id AND version = :version"
                ),
                {"plugin_id": plugin["id"], "version": plugin["version"]},
            )
        ).scalar_one_or_none()
        if existing is None:
            legacy_status = str(plugin["status"]).lower()
            if "approved" in legacy_status:
                version_status = "PUBLISHED"
            elif "rejected" in legacy_status:
                version_status = "REJECTED"
            elif "offline" in legacy_status:
                version_status = "DEPRECATED"
            else:
                version_status = "SUBMITTED"
            await connection.execute(
                text(
                    "INSERT INTO apehub_web_plugin_version "
                    "(plugin_id, version, status, compatibility, changelog, documentation, "
                    "reject_reason, created_at, updated_at) "
                    "VALUES (:plugin_id, :version, :status, '', '', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {
                    "plugin_id": plugin["id"],
                    "version": plugin["version"],
                    "status": version_status,
                },
            )
        version_id = (
            await connection.execute(
                text(
                    "SELECT id FROM apehub_web_plugin_version "
                    "WHERE plugin_id = :plugin_id AND version = :version"
                ),
                {"plugin_id": plugin["id"], "version": plugin["version"]},
            )
        ).scalar_one()
        await connection.execute(
            text(
                "UPDATE apehub_web_plugin_file SET version_id = :version_id "
                "WHERE plugin_id = :plugin_id AND version_id IS NULL"
            ),
            {"version_id": version_id, "plugin_id": plugin["id"]},
        )

    # Existing paid orders grant permanent access to future published versions.
    paid_orders = (
        await connection.execute(
            text(
                "SELECT id, user_id, plugin_id FROM apehub_web_order "
                "WHERE LOWER(status) IN ('paid', 'orderstatus.paid') OR status = 'PAID'"
            )
        )
    ).mappings().all()
    for order in paid_orders:
        exists = (
            await connection.execute(
                text(
                    "SELECT id FROM apehub_web_purchase_entitlement "
                    "WHERE user_id = :user_id AND plugin_id = :plugin_id"
                ),
                {"user_id": order["user_id"], "plugin_id": order["plugin_id"]},
            )
        ).scalar_one_or_none()
        if exists is None:
            await connection.execute(
                text(
                    "INSERT INTO apehub_web_purchase_entitlement "
                    "(user_id, plugin_id, order_id, active, granted_at) "
                    "VALUES (:user_id, :plugin_id, :order_id, 1, CURRENT_TIMESTAMP)"
                ),
                {
                    "user_id": order["user_id"],
                    "plugin_id": order["plugin_id"],
                    "order_id": order["id"],
                },
            )

    # Secrets were plaintext in schema <= 6. Re-encrypt them in place.
    configs = (
        await connection.execute(
            text("SELECT id, mail_code, lempay_key FROM apehub_web_site_config")
        )
    ).mappings().all()
    for config in configs:
        await connection.execute(
            text(
                "UPDATE apehub_web_site_config "
                "SET mail_code = :mail_code, lempay_key = :lempay_key WHERE id = :id"
            ),
            {
                "id": config["id"],
                "mail_code": _encrypt_legacy_secret(config["mail_code"]),
                "lempay_key": _encrypt_legacy_secret(config["lempay_key"]),
            },
        )

    # MySQL must alter existing floating money columns; SQLite's Numeric mapper
    # still quantizes values even when the historical storage affinity is REAL.
    if connection.dialect.name == "mysql":
        for table, columns in {
            "apehub_web_profile": ["balance", "frozen_balance", "total_income", "total_withdrawn"],
            "apehub_web_plugin": ["price"],
            "apehub_web_order": ["amount", "service_fee", "developer_income"],
            "apehub_web_income": ["amount"],
            "apehub_web_withdrawal": ["amount"],
        }.items():
            for column in columns:
                await connection.execute(
                    text(
                        f"ALTER TABLE {table} MODIFY COLUMN {column} "
                        "DECIMAL(20,8) NOT NULL DEFAULT 0"
                    )
                )
        for table, column in [
            ("apehub_web_site_config", "service_fee_rate"),
            ("apehub_web_plugin", "service_fee_rate"),
            ("apehub_web_income", "rate"),
        ]:
            await connection.execute(
                text(
                    f"ALTER TABLE {table} MODIFY COLUMN {column} "
                    "DECIMAL(8,4) NOT NULL DEFAULT 0"
                )
            )

    # Keep old withdrawals and incomes internally consistent.
    await connection.execute(
        text(
            "UPDATE apehub_web_withdrawal SET net_amount = amount - fee "
            "WHERE net_amount = 0 AND amount > 0"
        )
    )
    await connection.execute(
        text(
            "UPDATE apehub_web_income SET status = 'available', available_at = created_at "
            "WHERE status = 'pending'"
        )
    )
