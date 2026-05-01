<!-- doc-version: 0.1.3 -->
# LLM Work Handoff

This file is the current operational snapshot. Durable decisions live in
`docs/llm/DECISIONS.md`.

## Current Status

- Last Updated: 2026-05-01 - Claude
- Session Focus: Patch 0.1.3 — homelab profile for LLM-DocKit projects.
- Status: 0.1.3 ships an opt-in profile under `integrations/dockit/`
  (5 files: `INTEGRATION.md`, `templates/AGENTS.md`,
  `templates/infra.contract.yml`,
  `checklists/PROJECT_CHECKLIST.md`, `apply-profile.sh`). New homelab
  projects scaffolded from `cdelalama/LLM-DocKit` apply this profile
  with one command and immediately see the source-of-truth
  conventions, the deploy checklist, and an experimental contract
  template. `apply-profile.sh` is POSIX `sh`, idempotent, never
  overwrites; smoke-tested locally (create + idempotent re-run).
  `LLM-DocKit` stays general-purpose; the homelab-specific layer
  lives here on purpose.

## Patch 0.1.3 Outcome

- `integrations/dockit/INTEGRATION.md`: design rationale (separation
  from LLM-DocKit, multi-LLM rationale with `AGENTS.md` canonical),
  what gets installed, how to apply, what the profile does NOT do,
  future-native-support notes.
- `integrations/dockit/templates/AGENTS.md`: required reading order,
  mandatory `home-infra` updates rule, anti-rules. LLM-neutral
  language so Codex / Cursor / others can read the same file.
- `integrations/dockit/templates/infra.contract.yml`: protocol-
  aligned template with `TODO:` placeholders. Marked optional and
  experimental.
- `integrations/dockit/checklists/PROJECT_CHECKLIST.md`: operational
  checklist for "deploy is done" — build, secrets, runtime, network
  + TLS, source-of-truth updates, project docs, optional contract,
  smoke checks.
- `integrations/dockit/apply-profile.sh`: POSIX `sh`, idempotent.
  `cp -n` semantics for files (existing files never replaced),
  symlink `CLAUDE.md → AGENTS.md` so Claude Code's loader picks up
  the canonical content without duplicating it. Smoke-tested:
  fresh dir → 4 created; re-run → 4 skipped.
- `docs/version-sync-manifest.yml`: added
  `integrations/dockit/INTEGRATION.md`. 25 doc-version targets
  synced via `scripts/bump-version.sh 0.1.3`.

## Patch 0.1.2 Outcome

- `README.md`: new "Ecosystem map" section between *Overview* and
  *Quick Start*. Five-row table (LLM-DocKit, this repo,
  `home-infra`, `infra-portal`, `infra-agent`) with role,
  visibility and status. Explanatory paragraph above the table
  states why visibility differs.
- `LLM-DocKit` framed as separate-on-purpose so it can be reused
  outside this homelab; `infra-agent` flagged as planned, not yet
  created.
- 24 doc-version targets synced via `scripts/bump-version.sh 0.1.2`.

## Patch 0.1.1 Outcome

- `docs/GOVERNANCE.md`: field policy, ownership boundaries, project
  bootstrap rules, and compliance-claim freshness rules. The protocol
  now records that new ecosystem projects start from LLM-DocKit unless
  the user explicitly approves a waiver.

## Project Summary

Home Infra Protocol defines a reusable way to describe small infrastructure in
Git so humans, portals, MCP servers, recovery workflows, and LLM agents share a
single current memory.

The first private implementation is expected to be `home-infra`; the first
consumer pattern is expected to be `infra-portal`.

## Important Constraints

- Do not copy private infrastructure facts from `home-infra` into this public
  protocol repo.
- Keep examples sanitized.
- Do not build runtime services before the spec and schemas stabilize.
- Prefer additive schema evolution.
- New ecosystem projects such as a future `infra-agent` should start from
  `cdelalama/LLM-DocKit` unless Carlos explicitly approves a waiver.

## Next Concrete Steps

1. Review the v0.1 draft and governance rules with the user.
2. Decide whether the repo should remain spec-only for v0.1.
3. Add CI validation once a validator exists.
4. Add protocol version declarations for private implementations later.
5. If `infra-agent` starts, document its stats contract as a candidate
   telemetry-provider extension before wiring it into `infra-portal`.

## Files To Read First

- `README.md`
- `SPEC.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/COMPLETION_RULE.md`
- `docs/GOVERNANCE.md`
- `docs/PROJECT_CONTRACTS.md`
