# ApeAdmin Frontend Integration

The backend package includes the Vue source under `frontend/` for delivery.
The ApeAdmin frontend bundle must install the same files into these host paths
before it is built:

- `frontend/src/api/apehub_web.ts`
- `frontend/src/views/apehub_web/admin/Config.vue`
- `frontend/src/views/apehub_web/admin/Content.vue`
- `frontend/src/views/apehub_web/admin/Docs.vue`
- `frontend/src/views/apehub_web/admin/Plugins.vue`
- `frontend/src/views/apehub_web/admin/Orders.vue`
- `frontend/src/views/apehub_web/admin/Withdrawals.vue`
- `frontend/src/views/apehub_web/admin/Users.vue`

ApeAdmin resolves menu components with its existing view import convention.
Consequently the menu component values (`apehub_web/admin/*`) map directly to
the `frontend/src/views/apehub_web/admin/*.vue` files. Build the ApeAdmin
frontend after placing these files; no runtime route component is loaded from a
backend ZIP.

All seven pages use `/api/v1/apehub-web/*`, expose loading, empty, error, and
operation-feedback states, and rely on ApeAdmin's existing authentication and
permission routing for direct navigation and refresh.
