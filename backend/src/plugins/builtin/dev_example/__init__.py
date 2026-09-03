"""插件开发示例包。

.. note::
   本文件只需要一行：从 ``plugin.py`` 导出插件入口类。
   插件管理器发现插件时，会 import 本包的 ``__init__``，
   然后在其中查找 ``PluginInterface`` 的子类。
"""
from src.plugins.builtin.dev_example.plugin import DevExamplePlugin

__all__ = ["DevExamplePlugin"]
