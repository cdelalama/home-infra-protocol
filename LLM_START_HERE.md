<!-- doc-version: 0.1.3 -->
# LLM Start Guide - Home Infra Protocol

## Read This First

Home Infra Protocol is a specification project. It defines contracts, schemas,
examples, and future validator behavior for Git-based infrastructure memory.

Recommended reading order:

1. This file.
2. `SPEC.md`.
3. `docs/PROJECT_CONTEXT.md`.
4. `docs/ARCHITECTURE.md`.
5. `docs/COMPLETION_RULE.md`.
6. `docs/llm/HANDOFF.md`.
7. `docs/llm/DECISIONS.md`.

## Critical Rules

### Language Policy

- Conversation with Carlos: Spanish.
- Code, docs, comments, file names, schemas, and examples: English.
- Examples must be sanitized: no real private LAN IPs, hostnames, domains, or
  secrets from Carlos's home infrastructure.

<!-- DOCKIT-TEMPLATE:START doc-update-rules -->
### Documentation Update Rules
- Update docs/llm/HANDOFF.md every time you make a change.
- Append an entry to docs/llm/HISTORY.md in every session.
- HISTORY format: YYYY-MM-DD - <LLM_NAME> - <Brief summary> - Files: [list] - Version impact: [yes/no + details]
- Put long-form rationale in docs/llm/DECISIONS.md and link to it from HANDOFF.
- Prefer ASCII-only in docs/llm/* to avoid Windows encoding issues.
<!-- DOCKIT-TEMPLATE:END doc-update-rules -->

<!-- DOCKIT-TEMPLATE:START doc-sync-rules -->
### Documentation Sync Rules
- Keep this file's "Current Focus" section synchronized with docs/llm/HANDOFF.md "Current Status".
- Keep docs/STRUCTURE.md synchronized with the actual repository file tree.
- Keep docs/PROJECT_CONTEXT.md synchronized with architectural reality.
- Version markers (`<!-- doc-version: X.Y.Z -->`) in documentation files are managed by `scripts/bump-version.sh`. See `docs/version-sync-manifest.yml` for the full list of tracked files.
<!-- DOCKIT-TEMPLATE:END doc-sync-rules -->

<!-- DOCKIT-TEMPLATE:START commit-policy -->
### Commit Message Policy
- Every response that includes code or documentation changes must end with suggested commit information:
  - **Title:** under 72 characters
  - **Description:** under 200 characters, focused on user impact and why the change matters
- Format:
  `
  ## Commit Info
  **Title:** <concise title>
  **Description:** <short explanation of what changed and why>
  `
<!-- DOCKIT-TEMPLATE:END commit-policy -->

<!-- DOCKIT-TEMPLATE:START version-management -->
### Version Management
- Every commit that changes code/config files MUST include a version bump. The pre-commit hook enforces this.
- For version bumps, run `scripts/bump-version.sh <new_version>`; do not edit version strings manually.
- The bump script reads `docs/version-sync-manifest.yml` to update all tracked files atomically.
- Validate sync with `scripts/check-version-sync.sh` (also available as pre-commit hook).
- Do not bump versions without consulting docs/VERSIONING_RULES.md for impact level (patch/minor/major).
- Do NOT batch multiple code commits without versioning. No exceptions.
<!-- DOCKIT-TEMPLATE:END version-management -->

## Project-Specific Rules

- This repository is a protocol/specification project first, not a runtime.
- Keep real deployments in private implementation repos such as `home-infra`.
- Consumers such as portals, MCP servers, and agents must not become authorities
  unless the protocol explicitly assigns that role.
- Telemetry is not intent. Observed status can warn about drift, but it does not
  rewrite the source-of-truth catalog.
- Schema evolution should be additive until a major version.

## Current Focus

Source of truth: `docs/llm/HANDOFF.md`.

- Last Updated: 2026-05-01 - Codex.
- Working on: initial scaffold and v0.1 draft specification.
- Status: repository created from LLM-DocKit; no runtime implementation yet.

<!-- DOCKIT-TEMPLATE:START checklist -->
## Getting Started Checklist
- [ ] Read this entire file
- [ ] Review SPEC.md
- [ ] Review docs/PROJECT_CONTEXT.md
- [ ] Review docs/VERSIONING_RULES.md
- [ ] Read the current docs/llm/HANDOFF.md
- [ ] Install pre-commit hook: `cp scripts/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`
- [ ] Run `scripts/check-version-sync.sh` to verify version markers
- [ ] Confirm scope with the user
- [ ] Complete the work
- [ ] Update docs/llm/HANDOFF.md
- [ ] Add an entry to docs/llm/HISTORY.md
<!-- DOCKIT-TEMPLATE:END checklist -->

## Quick Navigation

- Protocol Spec: `SPEC.md`
- Governance: `docs/GOVERNANCE.md`
- Project Overview: `docs/PROJECT_CONTEXT.md`
- Architecture: `docs/ARCHITECTURE.md`
- Completion Rule: `docs/COMPLETION_RULE.md`
- Project Contracts: `docs/PROJECT_CONTRACTS.md`
- Security Model: `docs/SECURITY_MODEL.md`
- Recovery Model: `docs/RECOVERY_MODEL.md`
- LLM Workflow: `docs/LLM_WORKFLOW.md`
- Current Work State: `docs/llm/HANDOFF.md`
- Change History: `docs/llm/HISTORY.md`
- Decision Rationale: `docs/llm/DECISIONS.md`

<!-- DOCKIT-TEMPLATE:START llm-communication -->
## LLM-to-LLM Communication
When handing off to another LLM:
1. Update docs/llm/HANDOFF.md with the current state and next steps.
2. Append an entry to docs/llm/HISTORY.md following the required format.
3. Ensure the snapshot in this file matches the latest status.
<!-- DOCKIT-TEMPLATE:END llm-communication -->

<!-- DOCKIT-TEMPLATE:START do-not-touch -->
## Do Not Touch Zones
Use the Do Not Touch section in docs/llm/HANDOFF.md to flag any files or areas that must remain unchanged without explicit approval from the user.
<!-- DOCKIT-TEMPLATE:END do-not-touch -->

<!-- DOCKIT-EXTERNAL-CONTEXT:START -->
<!-- DOCKIT-EXTERNAL-CONTEXT:END -->

<!-- DOCKIT-TEMPLATE:START footer -->
---

Every change must be documented. If you are unsure about a rule, ask the user before proceeding.
<!-- DOCKIT-TEMPLATE:END footer -->
