# Alembic 迁移纪律（必读）

> 本文件定义 schema 变更的唯一合法路径。违反纪律会导致生产升级失败
> （如 2.4.0 的 `Unknown column 'i18n_key'` 事故）。

## 两条通道，各管一摊

| 通道 | 用途 | 何时用 |
|---|---|---|
| **Alembic 迁移**（本目录） | 改列 / 重命名 / 数据回填 / 索引 / 删列 | 一切非"新增可空列"的变更 |
| **启动补丁白名单**（`core/dbmigrate.py`） | 仅新增可空列（additive ADD COLUMN） | 新 model 字段为 NULLable 且有默认安全类型时 |

`init_db()` 的 `create_all` 只建缺失的**表**，永远不加列。因此任何
改列、改类型、重命名、回填数据，都必须写 Alembic 迁移——没有例外。

## 新增变更的 Checklist

1. **改 model**：`src/models/` 里修改 SQLAlchemy 模型。
2. **写迁移**：
   ```bash
   cd backend && alembic revision -m "add xx column to yy"
   ```
   - `down_revision` 接到当前链尾（`alembic heads` 查看）。
   - **迁移必须幂等**：先 `sa.inspect(conn)` 检查表/列是否存在再变更
     （参考 `0001_add_menu_i18n_key.py` 的写法），因为生产库可能处于
     任意历史状态（含已被启动补丁提前补过列的库）。
   - `downgrade()` 同样幂等。
3. **新增可空列**：除迁移外，同时在 `dbmigrate.py` 的 `SCHEMA_PATCHES`
   白名单追加同一条 ADD COLUMN（启动补丁兜底未跑 Alembic 的在途部署）。
   待全部部署都升级过 Alembic 后，可将白名单整体退役。
4. **本地验证**：
   ```bash
   alembic upgrade head        # 对当前开发库（列可能已存在）
   cp apeadmin.db /tmp/fresh.db && alembic upgrade head  # 对全新库
   ```
5. **测试**：`backend/tests/` 涉及该表的用例保持全绿。

## 反模式（禁止）

- ❌ 只改 model 不写迁移（指望 create_all）——已有表不会长出新列。
- ❌ 在启动补丁白名单里写非 ADD COLUMN 的 DDL——白名单只允许加列。
- ❌ 写非幂等迁移——生产库状态不可假设。
