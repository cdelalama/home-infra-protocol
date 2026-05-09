<!-- doc-version: 0.4.0 -->
# Versioning Rules

Home Infra Protocol uses Semantic Versioning.

## Version Source

- `VERSION` is the primary project version.
- `CHANGELOG.md` records user-visible changes.
- `docs/version-sync-manifest.yml` lists files that must carry matching version
  markers.

## Impact Levels

### Patch

- Clarifications.
- Example fixes.
- Non-breaking documentation improvements.
- Validator bug fixes once validators exist.

### Minor

- Additive schema fields.
- New optional contract sections.
- New examples or validator capabilities that do not break existing users.

### Major

- Removing or renaming fields.
- Changing authority rules.
- Incompatible schema behavior.

## Rules

- Prefer additive changes.
- Do not remove or rename fields without a major version.
- Keep examples and schemas aligned.
- Run `scripts/check-version-sync.sh` before committing.

## Version Bump

Use:

```bash
scripts/bump-version.sh <new_version>
```

The script updates `VERSION`, tracked doc markers, and `CHANGELOG.md`.
