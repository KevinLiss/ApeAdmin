"""Backend message internationalization.

Provides locale-aware message lookup via Accept-Language header.
Frontend sends Accept-Language: zh-CN or en-US on every request.
"""
from fastapi import Request

# ---------------------------------------------------------------------------
# Message dictionaries
# ---------------------------------------------------------------------------

_ZH = {
    # auth
    "auth.login_failed": "用户名或密码错误",
    "auth.login_success": "登录成功",
    "auth.logout_success": "已退出登录",
    "auth.profile_no_change": "无修改内容",
    "auth.profile_updated": "资料更新成功",
    "auth.old_password_wrong": "原密码不正确",
    "auth.new_password_same_as_old": "新密码不能与原密码相同",
    "auth.password_changed_relogin": "密码修改成功，请重新登录",
    "auth.invalid_refresh_token": "刷新令牌无效",
    "auth.user_not_found_or_disabled": "用户不存在或已被禁用",

    # user
    "user.username_exists": "用户名 '{username}' 已存在",
    "user.created": "创建成功",
    "user.not_found": "用户不存在",
    "user.updated": "更新成功",
    "user.deleted": "删除成功",
    "user.password_reset": "密码已重置",
    "user.cannot_delete_self": "不能删除当前登录用户",
    "user.cannot_disable_self": "不能禁用当前登录用户",

    # role
    "role.code_exists": "角色编码 '{code}' 已存在",
    "role.created": "创建成功",
    "role.not_found": "角色不存在",
    "role.updated": "更新成功",
    "role.deleted": "删除成功",
    "role.cannot_delete_builtin": "系统内置角色不可删除",

    # menu
    "menu.parent_not_found": "父级菜单不存在",
    "menu.button_cannot_be_parent": "按钮类型不能作为父级菜单",
    "menu.cannot_select_self_or_child": "不能选择当前菜单或其下级作为父级",
    "menu.hierarchy_cycle": "菜单层级存在循环，请先修复父级关系",
    "menu.hierarchy_broken": "菜单层级引用了不存在的父级",
    "menu.created": "创建成功",
    "menu.not_found": "菜单不存在",
    "menu.updated": "更新成功",
    "menu.deleted": "删除成功",

    # dept
    "dept.created": "创建成功",
    "dept.not_found": "部门不存在",
    "dept.updated": "更新成功",
    "dept.deleted": "删除成功",

    # setting
    "setting.updated_count": "已更新 {count} 项设置",
    "setting.key_not_found": "设置项 '{key}' 不存在",
    "setting.updated": "设置 '{key}' 已更新",
    "setting.image_format_only": "仅支持图片格式：jpg / jpeg / png / gif / webp / svg / ico",
    "setting.image_too_large": "图片大小不能超过 10MB",
    "setting.uploaded": "上传成功",

    # plugin
    "plugin.not_found": "插件不存在",
    "plugin.toggle_failed": "热拔插失败：{error}，建议重启后端",
    "plugin.toggled_active": "插件已启用，运行时生效",
    "plugin.toggled_inactive": "插件已禁用，运行时生效",
    "plugin.config_saved": "配置已保存",
    "plugin.zip_only": "仅支持 .zip 格式的插件包",
    "plugin.package_too_large": "插件包大小不能超过 50MB",
    "plugin.install_failed": "插件 '{filename}' 导入失败（manager）：{error}",
    "plugin.install_cleanup": "临时上传文件已清理；请根据错误信息修复后重试。",
    "plugin.installed": "插件安装成功，运行时生效",
    "plugin.restarting": "后端正在重启，请等待约 5 秒后刷新页面",
    "plugin.uninstall_failed": "插件卸载失败：{error}，建议重启后端",
    "plugin.uninstalled": "插件 '{name}' 已卸载，运行时生效",

    # file
    "file.default_name": "未命名文件",
    "file.folder_not_found": "文件夹不存在",
    "file.download_forbidden": "无下载权限",
    "file.folder_created": "文件夹创建成功",
    "file.folder_renamed": "文件夹已重命名",
    "file.root_folder_not_deletable": "根文件夹不可删除",
    "file.folder_deleted_with_files": "已删除文件夹及其下 {count} 个文件",
    "file.unsupported_type": "不支持的文件类型",
    "file.file_too_large": "文件大小不能超过 50MB",
    "file.uploaded": "文件上传成功",
    "file.invalid_path": "非法路径",
    "file.dir_not_found": "目录不存在",
    "file.not_found": "文件不存在",
    "file.delete_failed": "删除失败：{error}",
    "file.deleted": "文件已删除",
    "file.content_missing": "文件内容不存在",
    "file.already_in_folder": "文件已在目标文件夹",
    "file.moved": "文件已移动",
    "file.root_folder_not_movable": "根文件夹不可移动",
    "file.cannot_move_to_self": "不能移动到自身",
    "file.cannot_move_to_subtree": "不能移动到自身子文件夹中",
    "file.folder_moved": "文件夹已移动",
    "file.asset_group_not_found": "素材分组不存在",
    "file.only_image": "仅支持图片格式",

    # log
    "log.not_found": "日志不存在",
    "log.deleted": "删除成功",
    "log.cleared": "已清空所有日志",

    # ai_provider
    "ai_provider.name_exists": "供应商 '{name}' 已存在",
    "ai_provider.created": "创建成功",
    "ai_provider.not_found": "供应商不存在",
    "ai_provider.updated": "更新成功",
    "ai_provider.deleted": "删除成功",
    "ai_provider.test_ok": "连通成功",
    "ai_provider.test_failed": "连通失败",

    # chat
    "chat.provider_not_found": "指定的模型供应商不存在",
    "chat.provider_disabled": "该模型供应商已被禁用",
    "chat.no_provider_configured": "未配置任何可用的模型供应商，请先在「模型密钥管理」中添加",

    # chat_session
    "chat_session.default_title": "新对话",
    "chat_session.not_found": "会话不存在",
    "chat_session.created": "会话已创建",
    "chat_session.renamed": "会话已重命名",
    "chat_session.deleted": "会话已删除",
    "chat_session.message_saved": "消息已保存",

    # system
    "system.super_admin_only": "仅超级管理员可执行版本更新",
    "system.tar_gz_only": "仅支持 .tar.gz 格式的部署包",
    "system.package_too_large": "部署包大小不能超过 200MB",
    "system.invalid_path": "非法路径: {path}",
    "system.suspicious_package": "部署包解压后体积过大或文件数过多，疑似恶意包",
    "system.extract_failed": "无法解压，请检查文件是否为有效的 .tar.gz 包",
    "system.extract_error": "解压失败: {error}",
    "system.empty_package": "部署包为空或结构不正确",
    "system.missing_src": "部署包结构不正确：缺少 src/ 目录",
    "system.update_complete": "版本更新完成，后端正在重启，请等待约 5 秒后刷新页面",

    # validation (exceptions.py)
    "validation.field_username": "用户名",
    "validation.field_password": "密码",
    "validation.field_email": "邮箱",
    "validation.field_verification_code": "邮箱验证码",
    "validation.field_nickname": "昵称",
    "validation.field_old_password": "原密码",
    "validation.field_new_password": "新密码",
    "validation.field_code": "验证码",
    "validation.field_phone": "手机号",
    "validation.field_amount": "金额",
    "validation.field_title": "标题",
    "validation.field_content": "内容",
    "validation.format_invalid": "{field}格式不正确",
    "validation.too_short": "{field}长度不足（至少 {min} 个字符）",
    "validation.too_long": "{field}超出长度限制（最多 {max} 个字符）",
    "validation.required": "请填写{field}",
    "validation.gte": "{field}不能小于 {min}",
    "validation.lte": "{field}不能大于 {max}",
    "validation.json_invalid": "请求数据格式错误",
    "validation.field_invalid": "{field}填写有误，请检查后重试",
    "validation.params_invalid": "请求参数有误，请检查后重试",

    # common
    "common.success": "success",
    "common.internal_error": "Internal Server Error",
}

_EN = {
    # auth
    "auth.login_failed": "Invalid username or password",
    "auth.login_success": "Login successful",
    "auth.logout_success": "Signed out",
    "auth.profile_no_change": "No changes to save",
    "auth.profile_updated": "Profile updated successfully",
    "auth.old_password_wrong": "Current password is incorrect",
    "auth.new_password_same_as_old": "New password cannot be the same as the current password",
    "auth.password_changed_relogin": "Password changed successfully, please sign in again",
    "auth.invalid_refresh_token": "Invalid refresh token",
    "auth.user_not_found_or_disabled": "User not found or disabled",

    # user
    "user.username_exists": "Username '{username}' already exists",
    "user.created": "Created successfully",
    "user.not_found": "User not found",
    "user.updated": "Updated successfully",
    "user.deleted": "Deleted successfully",
    "user.password_reset": "Password has been reset",
    "user.cannot_delete_self": "You cannot delete the currently logged-in user",
    "user.cannot_disable_self": "You cannot disable the currently logged-in user",

    # role
    "role.code_exists": "Role code '{code}' already exists",
    "role.created": "Created successfully",
    "role.not_found": "Role not found",
    "role.updated": "Updated successfully",
    "role.deleted": "Deleted successfully",
    "role.cannot_delete_builtin": "Built-in roles cannot be deleted",

    # menu
    "menu.parent_not_found": "Parent menu not found",
    "menu.button_cannot_be_parent": "Button type cannot be a parent menu",
    "menu.cannot_select_self_or_child": "Cannot select current menu or its children as parent",
    "menu.hierarchy_cycle": "Menu hierarchy has a cycle, please fix parent relationships first",
    "menu.hierarchy_broken": "Menu hierarchy references a non-existent parent",
    "menu.created": "Created successfully",
    "menu.not_found": "Menu not found",
    "menu.updated": "Updated successfully",
    "menu.deleted": "Deleted successfully",

    # dept
    "dept.created": "Created successfully",
    "dept.not_found": "Department not found",
    "dept.updated": "Updated successfully",
    "dept.deleted": "Deleted successfully",

    # setting
    "setting.updated_count": "{count} settings updated",
    "setting.key_not_found": "Setting '{key}' not found",
    "setting.updated": "Setting '{key}' updated",
    "setting.image_format_only": "Only image formats supported: jpg / jpeg / png / gif / webp / svg / ico",
    "setting.image_too_large": "Image size cannot exceed 10MB",
    "setting.uploaded": "Upload successful",

    # plugin
    "plugin.not_found": "Plugin not found",
    "plugin.toggle_failed": "Hot-swap failed: {error}, recommend restarting the backend",
    "plugin.toggled_active": "Plugin enabled, effective at runtime",
    "plugin.toggled_inactive": "Plugin disabled, effective at runtime",
    "plugin.config_saved": "Configuration saved",
    "plugin.zip_only": "Only .zip format is supported",
    "plugin.package_too_large": "Plugin package size cannot exceed 50MB",
    "plugin.install_failed": "Plugin '{filename}' import failed (manager): {error}",
    "plugin.install_cleanup": "Temporary upload file cleaned up; please fix the error and try again.",
    "plugin.installed": "Plugin installed successfully, effective at runtime",
    "plugin.restarting": "Backend is restarting, please wait ~5 seconds and refresh the page",
    "plugin.uninstall_failed": "Plugin uninstall failed: {error}, recommend restarting the backend",
    "plugin.uninstalled": "Plugin '{name}' uninstalled, effective at runtime",

    # file
    "file.default_name": "Untitled file",
    "file.folder_not_found": "Folder not found",
    "file.download_forbidden": "No download permission",
    "file.folder_created": "Folder created successfully",
    "file.folder_renamed": "Folder renamed",
    "file.root_folder_not_deletable": "Root folder cannot be deleted",
    "file.folder_deleted_with_files": "Deleted folder and {count} files within",
    "file.unsupported_type": "Unsupported file type",
    "file.file_too_large": "File size cannot exceed 50MB",
    "file.uploaded": "File uploaded successfully",
    "file.invalid_path": "Invalid path",
    "file.dir_not_found": "Directory not found",
    "file.not_found": "File not found",
    "file.delete_failed": "Delete failed: {error}",
    "file.deleted": "File deleted",
    "file.content_missing": "File content not found",
    "file.already_in_folder": "File is already in the target folder",
    "file.moved": "File moved",
    "file.root_folder_not_movable": "Root folder cannot be moved",
    "file.cannot_move_to_self": "Cannot move to itself",
    "file.cannot_move_to_subtree": "Cannot move to its own subfolder",
    "file.folder_moved": "Folder moved",
    "file.asset_group_not_found": "Asset group not found",
    "file.only_image": "Only image formats are supported",

    # log
    "log.not_found": "Log not found",
    "log.deleted": "Deleted successfully",
    "log.cleared": "All logs cleared",

    # ai_provider
    "ai_provider.name_exists": "Provider '{name}' already exists",
    "ai_provider.created": "Created successfully",
    "ai_provider.not_found": "Provider not found",
    "ai_provider.updated": "Updated successfully",
    "ai_provider.deleted": "Deleted successfully",
    "ai_provider.test_ok": "Connection successful",
    "ai_provider.test_failed": "Connection failed",

    # chat
    "chat.provider_not_found": "The specified model provider does not exist",
    "chat.provider_disabled": "The model provider has been disabled",
    "chat.no_provider_configured": "No model provider configured, please add one in Model Providers first",

    # chat_session
    "chat_session.default_title": "New Chat",
    "chat_session.not_found": "Session not found",
    "chat_session.created": "Session created",
    "chat_session.renamed": "Session renamed",
    "chat_session.deleted": "Session deleted",
    "chat_session.message_saved": "Message saved",

    # system
    "system.super_admin_only": "Only super admin can perform version updates",
    "system.tar_gz_only": "Only .tar.gz format is supported",
    "system.package_too_large": "Package size cannot exceed 200MB",
    "system.invalid_path": "Invalid path: {path}",
    "system.suspicious_package": "Package is too large or contains too many files after extraction, possibly malicious",
    "system.extract_failed": "Cannot extract, please verify the file is a valid .tar.gz package",
    "system.extract_error": "Extract failed: {error}",
    "system.empty_package": "Package is empty or has incorrect structure",
    "system.missing_src": "Package structure is incorrect: missing src/ directory",
    "system.update_complete": "Version update complete, backend is restarting, please wait ~5 seconds and refresh",

    # validation (exceptions.py)
    "validation.field_username": "Username",
    "validation.field_password": "Password",
    "validation.field_email": "Email",
    "validation.field_verification_code": "Verification code",
    "validation.field_nickname": "Nickname",
    "validation.field_old_password": "Current password",
    "validation.field_new_password": "New password",
    "validation.field_code": "Code",
    "validation.field_phone": "Phone",
    "validation.field_amount": "Amount",
    "validation.field_title": "Title",
    "validation.field_content": "Content",
    "validation.format_invalid": "Invalid {field} format",
    "validation.too_short": "{field} is too short (minimum {min} characters)",
    "validation.too_long": "{field} is too long (maximum {max} characters)",
    "validation.required": "Please enter {field}",
    "validation.gte": "{field} cannot be less than {min}",
    "validation.lte": "{field} cannot be greater than {max}",
    "validation.json_invalid": "Invalid request data format",
    "validation.field_invalid": "Invalid {field}, please check and try again",
    "validation.params_invalid": "Invalid request parameters, please check and try again",

    # common
    "common.success": "success",
    "common.internal_error": "Internal Server Error",
}

_MESSAGES = {"zh-CN": _ZH, "en-US": _EN}


def get_locale(request: Request) -> str:
    """Extract locale from Accept-Language header."""
    lang = request.headers.get("Accept-Language", "zh-CN")
    primary = lang.split(",")[0].strip().split(";")[0]
    if primary.startswith("en"):
        return "en-US"
    return "zh-CN"


def t(key: str, locale: str = "zh-CN", **kwargs) -> str:
    """Translate a message key with optional format arguments."""
    msgs = _MESSAGES.get(locale, _ZH)
    msg = msgs.get(key, _ZH.get(key, key))
    return msg.format(**kwargs) if kwargs else msg
