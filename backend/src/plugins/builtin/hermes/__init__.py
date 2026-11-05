"""Hermes AI 助手插件包。

.. note::
   插件管理器发现插件时会 import 本包的 ``__init__``，
   然后在其中查找 ``PluginInterface`` 的子类。
"""
from src.plugins.builtin.hermes.plugin import HermesPlugin

__all__ = ["HermesPlugin"]
