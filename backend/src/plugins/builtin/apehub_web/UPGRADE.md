# Apehub_web Upgrade Notes

## Version 1.2.2

Migration `v0005_legacy_asset_path.py` replaces the retired default
`/apeui/assets/logo.png` reference with the bundled Apehub_web logo. Other
custom Logo values remain untouched.

## Version 1.2.1

Migration `v0004_default_assets.py` supplies the legacy static assets as
defaults: `/apehub-web/assets/logo.png` for the site logo and
`/apehub-web/assets/screenshot.png` for the Hero image. It updates only blank
fields, so a configured custom image is never overwritten.

## Version 1.2.0

Migration `v0003_email_verification.py` adds the
`apehub_web_email_verification` table. Registration now requires a one-time
six-digit code delivered through the configured QQ SMTP account. Codes are
stored only as keyed digests, expire after five minutes, are consumed after
one successful use, and are rate-limited by email and request IP.

Configure `mail_user`, `mail_code`, `mail_host` (`smtp.qq.com`), and
`mail_port` (`465`) in the Apehub_web management configuration before enabling
public registration. The configuration API never returns `mail_code`; sending
an empty value on an update also preserves the existing authorization code.

## Version 1.1.0

## Scope

Version 1.1.0 replaces the retired `apeui` plugin identity with the
plugin-owned `apehub_web` identity:

- API: `/api/v1/apehub-web`
- Static site: `/apehub-web`
- Database tables: `apehub_web_*`
- Permissions: `apehub_web:*`

## Legacy data migration

On the first installation, migration `v0002_migrate_apeui.py` detects the
legacy `apeui_site_config` table and copies all supported `apeui_*` records
into matching `apehub_web_*` tables. It preserves primary keys and foreign-key
references, so existing documents, plugins, files, demos, orders, incomes, and
withdrawals remain readable.

The migration is recorded in `apehub_web_schema_version` and therefore runs
only once. It does not delete the old `apeui_*` tables. Keep those tables until
the copied data has been checked and a separately approved backup/retirement
procedure is performed.

If a target `apehub_web_*` table already contains data while legacy data is
still present, migration stops with an explicit error rather than merging two
unknown data sets. Resolve that conflict from a backup or a reviewed migration
plan, then retry.

## Lifecycle behavior

- Reinstall is idempotent: tables, seed records, menu records, and role grants
  are checked before creation.
- Disable hides the plugin menu branch and unregisters its runtime routes while
  retaining plugin data by default.
- Enable restores the shipped menu branch and runtime routes.
- Uninstall with `keep_data=true` removes the package and runtime resources but
  preserves `apehub_web_*` data. Setting `keep_data=false` drops only the
  `apehub_web_*` tables.

## Upgrade order

1. Back up the database and the existing plugin package.
2. Disable the retired plugin if it is active.
3. Import `apehub_web-1.1.0.zip`.
4. Confirm schema versions 1 and 2 exist in `apehub_web_schema_version`.
5. Compare row counts between legacy and new tables before retiring legacy data.
