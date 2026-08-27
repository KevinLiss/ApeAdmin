# Apehub Web Plugin Remediation Requirements

## 1. Background

When importing `apehub_web-1.0.1.zip` into ApeAdmin, the first installation can succeed, but a repeated import or hot-plug operation fails with:

```text
Table 'apeui_site_config' is already defined for this MetaData instance.
Specify 'extend_existing=True' to redefine options and columns on an existing Table object.
```

The plugin is named `apehub_web`, but its implementation still reuses the previous ApeUI model, route, and seed naming. This causes duplicate SQLAlchemy table registration and makes the plugin difficult to upgrade or coexist with an older ApeUI package.

The plugin package also currently provides only a health endpoint. The static website pages are present, but the corresponding business APIs and ApeAdmin backend management pages are not complete.

## 2. Scope

This remediation applies to the `apehub_web` plugin package and its installation contract with ApeAdmin. It covers:

- Plugin identity and package naming
- ORM model and database table registration
- Installation, upgrade, re-import, disable, and uninstall lifecycle
- API and static route registration
- Frontend management pages and menu declarations
- Error handling and acceptance testing

## 3. Required Fixes

### 3.1 Unify Plugin Identity

The following identifiers must be consistent:

- `plugin.json.name`
- Python package directory
- Python module import path
- `PluginInterface.name`
- API route prefix
- Static resource prefix
- Database table prefix
- Seed function names
- Display name and documentation

Recommended naming:

```text
Plugin name: apehub_web
Python package: src.plugins.builtin.apehub_web
API prefix: /api/v1/apehub-web
Static prefix: /apehub-web
Database prefix: apehub_web_
```

If backward compatibility requires retaining `/apeui` or `apeui_*` names, this must be explicitly documented and implemented as a compatibility layer. The plugin must not silently mix `apehub_web` and `apeui` identifiers.

### 3.2 Resolve ORM Table Conflicts

The current models define tables such as:

```text
apeui_site_config
apeui_site_content
apeui_doc_category
apeui_doc
apeui_profile
apeui_plugin
apeui_plugin_file
apeui_plugin_demo
apeui_order
apeui_income
apeui_withdrawal
```

The plugin team must choose one of the following strategies:

#### Preferred strategy: rename tables

Rename tables to the plugin-owned prefix:

```text
apehub_web_site_config
apehub_web_site_content
apehub_web_doc_category
apehub_web_doc
apehub_web_profile
apehub_web_plugin
apehub_web_plugin_file
apehub_web_plugin_demo
apehub_web_order
apehub_web_income
apehub_web_withdrawal
```

All foreign keys, relationships, seed code, queries, uninstall logic, and documentation must be updated accordingly.

#### Compatibility strategy: retain existing tables

If existing production data must remain in `apeui_*` tables:

1. Treat the tables as a formally versioned shared schema.
2. Add an explicit migration/version check.
3. Ensure model registration is performed only once per process.
4. Make repeated installation skip already-registered models safely.
5. Ensure old `apeui` and new `apehub_web` packages cannot register conflicting declarative classes in the same `MetaData` instance.
6. Document the ownership and upgrade path.

Adding `extend_existing=True` alone is not an acceptable fix. It can hide incompatible columns and mapper conflicts without resolving the underlying ownership problem.

### 3.3 Make Lifecycle Operations Idempotent

The following operations must be safe to run repeatedly:

- Install on a clean database
- Install when tables already exist
- Re-import the same version
- Upgrade from an older version
- Disable and re-enable
- Uninstall while preserving data
- Uninstall and reinstall
- Failed installation rollback

Required behavior:

- A failed import must not leave a partially copied plugin directory.
- A failed install must not leave a partially registered route, event, MCP tool, or ORM model.
- Re-importing the same version must either update cleanly or return a clear “already installed” result.
- Upgrade must use an explicit migration path.
- Uninstall must remove only resources owned by this plugin.
- Database data must not be deleted unless the uninstall request explicitly asks for data removal.

### 3.4 Complete API and Static Route Contract

The plugin must declare and implement all routes referenced by its static pages.

At minimum, provide:

- Site configuration read/update
- Site content read/update
- Documentation list/detail/category APIs
- Public plugin list/detail APIs
- Plugin package/demo APIs
- User profile APIs
- Order creation/list/detail APIs
- Withdrawal creation/list APIs
- Health check API

Each API must define:

- Request and response schema
- Authentication requirement
- Permission requirement
- Validation errors
- Empty-data behavior
- Persistence behavior

The current health endpoint alone is insufficient for the website's business pages.

### 3.5 Correct ApeAdmin Management Menus

Do not register menus for pages that are not shipped in the plugin package.

Every declared menu component must have a matching frontend page. For example:

```text
apehub_web/admin/Config
apehub_web/admin/Content
apehub_web/admin/Docs
apehub_web/admin/Plugins
apehub_web/admin/Orders
apehub_web/admin/Withdrawals
apehub_web/admin/Users
```

If these pages are not ready, remove the menus from the plugin seed until they are implemented. A visible menu that resolves to a missing component and then to 404 is not acceptable.

Each management page must support:

- Loading state
- Empty state
- API error state
- Permission denial state
- Successful operation feedback
- Browser refresh and direct URL access

### 3.6 Align Permissions

Permissions in menu seed data must match backend endpoint checks. Use a consistent namespace, for example:

```text
apehub_web:config:list
apehub_web:config:edit
apehub_web:content:list
apehub_web:content:edit
apehub_web:docs:list
apehub_web:plugins:review
apehub_web:orders:list
apehub_web:withdrawals:review
apehub_web:users:list
```

Do not mix `apeui:*`, `apehub:*`, and `apehub_web:*` permissions for the same feature.

## 4. Package Structure Requirements

The final ZIP package must contain:

```text
plugin.json
apehub_web/
  __init__.py
  plugin.py
  api.py
  models.py
  seed.py
  migrations/
  static/
    index.html
    plugins.html
    docs.html
    profile.html
    assets/
```

If ApeAdmin backend management pages are delivered as part of the plugin, include their source/build assets and document how ApeAdmin loads them. Do not rely on files that exist only in a developer's local checkout.

## 5. Error Handling Requirements

Installation errors must return an actionable message that identifies:

- Plugin name and version
- Failed lifecycle step
- Root exception category
- Whether files, database changes, and runtime registrations were rolled back
- Recommended next action

The UI must not show only a generic `422` or `500` toast when a plugin installation fails.

## 6. Acceptance Tests

### Clean installation

1. Start with a clean ApeAdmin database.
2. Import `apehub_web` once.
3. Confirm the plugin is listed and enabled.
4. Confirm all declared tables are created exactly once.
5. Confirm all declared routes return expected responses.

### Re-import and upgrade

1. Import the same ZIP a second time.
2. Confirm no `already defined for this MetaData instance` error occurs.
3. Confirm no duplicate tables, routes, menu rows, or permissions are created.
4. Import a higher version and run the migration.
5. Confirm existing data remains readable.

### Runtime lifecycle

1. Disable the plugin.
2. Confirm plugin routes and menus are unavailable or hidden as designed.
3. Confirm core ApeAdmin routes remain available.
4. Re-enable the plugin.
5. Confirm routes and menus recover without restarting the process unless explicitly required.
6. Uninstall with data preservation enabled.
7. Reinstall and confirm preserved data is usable.

### Frontend route verification

For every declared management page:

- Click the sidebar menu.
- Open the route directly in a new browser tab.
- Refresh the page.
- Confirm the page does not resolve to 404.
- Confirm browser console has no module-load or route-resolution errors.

### API verification

- Health endpoint returns HTTP 200.
- Public website APIs return HTTP 200 for valid requests.
- Invalid requests return structured validation errors.
- Unauthorized requests return HTTP 401.
- Insufficient permissions return HTTP 403.
- Missing records return structured HTTP 404 responses.

## 7. Deliverables

The plugin team must provide:

1. Updated source package
2. Updated `plugin.json`
3. Database migration/versioning files
4. Updated models, foreign keys, seed, and uninstall logic
5. Complete API implementation
6. Complete frontend management pages or removal of unfinished menus
7. Lifecycle test results
8. A fresh importable ZIP package
9. Upgrade notes describing compatibility with previous `apeui_*` data

## 8. Definition of Done

This issue is considered resolved only when:

- Repeated import does not produce metadata conflicts.
- No plugin page advertised in the menu leads to 404.
- Disabling and re-enabling the plugin is reversible.
- Failed installation rolls back files and runtime registrations.
- Existing data is preserved according to the documented migration strategy.
- The complete acceptance test set passes.
