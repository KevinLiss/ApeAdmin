#!/usr/bin/env python
"""SQLite → MySQL 数据迁移脚本。

用法（在 backend/ 目录下）:
    # 先确保 .env 已切到 MySQL 配置（DB_TYPE=mysql 及 DB_* 五项）
    # 如需密钥轮换（服务器 JWT_SECRET 与本地不同），加 --old-jwt-secret
    python -m scripts.migrate_sqlite_to_mysql [--source apeadmin.db] \
        [--old-jwt-secret <本地旧的JWT_SECRET>]

流程:
    1. 读源 SQLite（ORM 模型声明的全部表 + apehub_web_schema_version 版本表）
    2. 目标 MySQL 先由 create_all 建空表（幂等）
    3. 按依赖顺序逐表搬数据（清空目标表后重灌，保证可重跑）
    4. 迁移 apehub_web_schema_version，避免服务器上插件 migration 重跑
    5. （可选）对加密字段做密钥轮换：旧 JWT_SECRET 解密 → 新 JWT_SECRET 重加密
    6. 迁移完输出各表行数对照 + 自增起点校正

特性:
    - 幂等：可反复执行，每次先清空目标表再灌
    - JSON/DateTime 字段由 SQLAlchemy 类型自动转换
    - 跳过源库中不存在的表（比如没启用过的插件表）
    - 加密字段轮换：Fernet 密钥由 JWT_SECRET 派生，换环境必换密钥

加密字段清单（Fernet 密文，均以 gAAAAAB 开头）:
    - ai_provider.api_key_enc
    - apehub_web_site_config: mail_code / lempay_key / deepseek_api_key / qwen_api_key
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import sys
from pathlib import Path

# 确保 backend/ 在 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import delete, insert, text  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from src.db import Base  # noqa: E402

# 导入所有模型，确保元数据完整
import src.models  # noqa: F401, E402
import src.plugins.builtin.apehub_web.models  # noqa: F401, E402

# 插件 schema 版本表（不在 ORM 元数据里，由 migration 系统自建）
VERSION_TABLE = "apehub_web_schema_version"

# 加密字段清单: 表名 -> [列名]
ENCRYPTED_COLUMNS: dict[str, list[str]] = {
    "ai_provider": ["api_key_enc"],
    "apehub_web_site_config": ["mail_code", "lempay_key", "deepseek_api_key", "qwen_api_key"],
}


def _make_fernet(secret: str):
    """按 crypto.py 的算法从 JWT_SECRET 派生 Fernet（不 import 应用代码，避免读 .env）。"""
    from cryptography.fernet import Fernet

    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def rotate_secrets(rows: list[dict], columns: list[str], old_fernet, new_fernet) -> int:
    """对 rows 里的加密列做旧解密→新加密，返回成功轮换的字段数。"""
    rotated = 0
    for row in rows:
        for col in columns:
            value = row.get(col)
            if not value:
                continue
            try:
                plaintext = old_fernet.decrypt(value.encode("utf-8"))
                row[col] = new_fernet.encrypt(plaintext).decode("utf-8")
                rotated += 1
            except Exception:
                # 解不开（非 Fernet 密文或密钥不对），保留原值
                print(f"    [警告] {col} 无法用旧密钥解密，保留原值（长度 {len(value)}）")
    return rotated


async def main() -> None:
    parser = argparse.ArgumentParser(description="SQLite → MySQL 数据迁移")
    parser.add_argument("--source", default="apeadmin.db", help="源 SQLite 文件路径")
    parser.add_argument(
        "--old-jwt-secret",
        default=None,
        help="旧的 JWT_SECRET（源库加密数据所用）。不传则不做密钥轮换",
    )
    args = parser.parse_args()

    src_path = Path(args.source)
    if not src_path.exists():
        print(f"[错误] 源数据库不存在: {src_path.resolve()}")
        sys.exit(1)

    # 运行时环境必须是 MySQL（读 .env）
    from src.core.config import settings

    if settings.DB_TYPE != "mysql":
        print(f"[错误] 当前 DB_TYPE={settings.DB_TYPE}，请先把 .env 切到 mysql 再运行")
        sys.exit(1)

    print(f"源: SQLite  {src_path.resolve()}")
    print(f"目标: MySQL {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    if args.old_jwt_secret:
        print(f"密钥轮换: 启用（旧密钥 → 当前 .env 的 JWT_SECRET）")
    print()

    old_fernet = _make_fernet(args.old_jwt_secret) if args.old_jwt_secret else None
    new_fernet = _make_fernet(settings.JWT_SECRET)

    sqlite_engine = create_async_engine(f"sqlite+aiosqlite:///{src_path}")
    mysql_engine = create_async_engine(settings.database_url, echo=False)

    # 按拓扑序取表（sorted_tables 保证父表先于子表，外键不炸）
    tables = list(Base.metadata.sorted_tables)

    total_rows = 0
    migrated_tables = 0

    try:
        # 1. MySQL 建空表（幂等）
        async with mysql_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("[1/4] MySQL 建表完成（幂等，已有表跳过）")

        # 2. 逐表迁移（MySQL 端临时关外键检查，双重保险）
        print("[2/4] 迁移数据...")
        async with mysql_engine.begin() as mconn:
            if settings.DB_TYPE == "mysql":
                await mconn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        try:
            for table in tables:
                name = table.name
                try:
                    async with sqlite_engine.connect() as sconn:
                        rows = (await sconn.execute(table.select())).mappings().all()
                except Exception as exc:
                    # 源库无此表 → 跳过
                    print(f"  - {name:<38} 跳过（源库无此表: {type(exc).__name__}）")
                    continue

                rows = [dict(r) for r in rows]

                # 加密字段密钥轮换
                if old_fernet and name in ENCRYPTED_COLUMNS:
                    n = rotate_secrets(rows, ENCRYPTED_COLUMNS[name], old_fernet, new_fernet)
                    if n:
                        print(f"    密钥轮换 {n} 个加密字段")

                async with mysql_engine.begin() as mconn:
                    await mconn.execute(delete(table))
                    if rows:
                        # 分批插入，避免单条 SQL 过大
                        BATCH = 200
                        for i in range(0, len(rows), BATCH):
                            await mconn.execute(insert(table), rows[i : i + BATCH])

                if rows:
                    print(f"  - {name:<38} {len(rows):>6} 行")
                    total_rows += len(rows)
                    migrated_tables += 1
        finally:
            async with mysql_engine.begin() as mconn:
                if settings.DB_TYPE == "mysql":
                    await mconn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

        # 3. 迁移插件 schema 版本表（避免服务器上 migration 重跑 v0002~v0013）
        print("[3/4] 迁移插件 schema 版本表...")
        async with sqlite_engine.connect() as sconn:
            has_table = (
                await sconn.execute(
                    text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{VERSION_TABLE}'")
                )
            ).scalar_one_or_none()
            if has_table:
                versions = (
                    await sconn.execute(text(f"SELECT version, applied_at FROM {VERSION_TABLE} ORDER BY version"))
                ).mappings().all()
                async with mysql_engine.begin() as mconn:
                    await mconn.execute(
                        text(
                            f"CREATE TABLE IF NOT EXISTS {VERSION_TABLE} "
                            "(version INTEGER PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
                        )
                    )
                    await mconn.execute(text(f"DELETE FROM {VERSION_TABLE}"))
                    for v in versions:
                        await mconn.execute(
                            text(f"INSERT INTO {VERSION_TABLE} (version, applied_at) VALUES (:version, :applied_at)"),
                            {"version": v["version"], "applied_at": v["applied_at"]},
                        )
                print(f"  - {VERSION_TABLE} 迁移 {len(versions)} 条版本记录（当前 v{versions[-1]['version']}）")
            else:
                print(f"  - {VERSION_TABLE} 源库不存在（全新库），跳过")

        # 4. 重置 MySQL 自增起点（避免与导入 ID 冲突）
        print("[4/4] 校正自增起点...")
        async with mysql_engine.begin() as mconn:
            for table in tables:
                try:
                    pk = list(table.primary_key.columns)[0].name
                    max_id = (
                        await mconn.execute(
                            text(f"SELECT COALESCE(MAX(`{pk}`), 0) FROM `{table.name}`")
                        )
                    ).scalar()
                    if max_id:
                        await mconn.execute(
                            text(f"ALTER TABLE `{table.name}` AUTO_INCREMENT = {int(max_id) + 1}")
                        )
                except Exception:
                    pass  # 无自增主键的表跳过

        print()
        print("=" * 60)
        print(f"迁移完成：{total_rows} 行，{migrated_tables} 张表")
        print("=" * 60)

    finally:
        await sqlite_engine.dispose()
        await mysql_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
