---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'a9c95025-5423-45fc-8a95-496f7c24eb10'
  PropagateID: 'a9c95025-5423-45fc-8a95-496f7c24eb10'
  ReservedCode1: '4032b36f-6c72-4e80-bcfb-04a719bcae0e'
  ReservedCode2: '4032b36f-6c72-4e80-bcfb-04a719bcae0e'
---

# 插件 MCP 工具开发指南

本文档介绍如何为 ApeAdmin 插件编写 MCP（Model Context Protocol）工具，使 AI 助手能够通过自然语言调用插件提供的功能。

## 概述

ApeAdmin 的 MCP 架构允许每个插件注册自己的 AI 可调用工具。当用户在 AI 助手中提问时，LLM 可以自动选择并调用这些工具，无需用户手动操作后台界面。

### 核心概念

| 概念 | 说明 |
|------|------|
| **MCP Tool** | 一个可被 AI 调用的函数，有名称、描述、参数 Schema |
| **MCP Resource** | 只读数据源（如系统状态），AI 可读取 |
| **MCP Prompt** | 预定义的提示词模板 |
| **RBAC** | 工具可声明所需权限，只有有权限的用户才能调用 |

## 快速开始

### 方式一：声明式装饰器（推荐）

在插件的 `plugin.py` 中使用 `@mcp_tool` 装饰器：

```python
from src.mcp.decorators import mcp_tool, register_decorated_tools

class MyPlugin(PluginInterface):
    name = "my_plugin"

    def register_mcp_tools(self) -> None:
        """插件启用时自动调用，注册所有声明式 MCP 工具。"""
        register_decorated_tools(self, plugin_name=self.name)

    @mcp_tool("my_search", "搜索插件数据", permissions=["my_plugin:data:list"])
    def mcp_search(self, keyword: str, limit: int = 10) -> str:
        """搜索插件数据。

        Args:
            keyword: 搜索关键词。
            limit: 返回条数上限，默认10。
        """
        # 你的业务逻辑
        results = do_search(keyword, limit)
        return json.dumps(results, ensure_ascii=False)
```

### 方式二：手动注册

在 `register_mcp_tools()` 中直接调用 `mcp_manager`：

```python
def register_mcp_tools(self) -> None:
    from src.mcp.manager import mcp_manager

    mcp_manager.register_tool(
        name="my_search",
        description="搜索插件数据",
        handler=self._do_search,  # 可以是 async 函数
        required_permissions=["my_plugin:data:list"],
        plugin_name="my_plugin",
        category="my_plugin",
    )

async def _do_search(self, keyword: str = "", limit: int = 10) -> str:
    """搜索插件数据。

    Args:
        keyword: 搜索关键词。
        limit: 返回条数上限。
    """
    ...
```

## 生命周期

```
插件启用
  ├── on_load()
  ├── install()          → 创建表、播种数据
  ├── register(app)     → 注册 API 路由
  └── register_mcp_tools() → 注册 MCP 工具    ← 你在这里

插件禁用
  └── PluginManager 自动注销该插件注册的所有 MCP 工具
```

`register_mcp_tools()` 是 `PluginInterface` 的可选钩子。如果插件不提供 MCP 工具，不实现此方法即可（基类默认空实现）。

## 参数 Schema 自动推断

McpManager 会自动从函数签名推断 JSON Schema：

| Python 类型 | JSON Schema 类型 |
|-------------|-----------------|
| `int` | `integer` |
| `float` | `number` |
| `bool` | `boolean` |
| `str` | `string` |
| `list[str]` | `array` (items: string) |
| `dict` | `object` |
| `Optional[int]` | `integer` (非必填) |
| `Enum` 子类 | `string` + `enum` 值列表 |

**Docstring 参数说明**：如果使用 Google 风格的 docstring，参数描述会自动提取到 Schema 中：

```python
def my_tool(self, query: str, page: int = 1) -> str:
    """搜索数据。

    Args:
        query: 搜索关键词。
        page: 页码，从1开始。
    """
```

生成的 Schema 会包含 `query` 和 `page` 的 `description` 字段。

## 权限控制

工具通过 `required_permissions` 声明权限：

- **空列表**：公开工具，任何登录用户可调用
- **有权限**：用户的角色必须包含至少一个声明权限
- **超级管理员**（权限为 `*`）：可调用所有工具

```python
# 公开工具
@mcp_tool("public_search", "公开搜索", permissions=[])

# 需要管理权限
@mcp_tool("admin_stats", "管理统计", permissions=["my_plugin:admin:view"])
```

## 完整示例

参考 `backend/src/plugins/builtin/apehub_web/mcp_tools.py`，它注册了 4 个真实 MCP 工具：

| 工具名 | 说明 | 权限 |
|--------|------|------|
| `market_search` | 搜索插件市场 | 公开 |
| `market_plugin_detail` | 查看插件详情 | 公开 |
| `market_developer_info` | 查看开发者信息 | 管理员 |
| `market_stats` | 市场统计 | 公开 |

## 调试

1. **查看已注册工具**：在管理后台 → MCP 管理 → 工具列表 页面查看
2. **在线测试**：在工具列表页面点击"调用"按钮测试
3. **AI 调用**：在 AI 助手中提问，如"搜索插件市场有哪些AI插件"
4. **审计日志**：所有工具调用（含 AI 触发的）都记录在 MCP 调用日志中

## 插件市场声明

在插件市场的 `apehub_web_plugin` 表中，`mcp_tools` 字段（JSON）可以声明该插件提供的 MCP 工具清单，供市场页面展示：

```json
[
  {"name": "market_search", "description": "搜索插件市场"},
  {"name": "market_stats", "description": "市场统计"}
]
```

## 脚手架

快速生成新插件骨架（含 MCP 工具模板）：

```bash
cd backend
python -m src.plugins.scaffold my_plugin "My Plugin" "A cool plugin"
```

生成的插件包含 `mcp_tools.py` 模板文件，参考其中的 `@mcp_tool` 装饰器用法。

> AI生成