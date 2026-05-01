<!-- doc-version: 0.1.4 -->
# LLM Work Handoff

This file is the current operational snapshot. Durable decisions live in
`docs/llm/DECISIONS.md`.

## Current Status

- Last Updated: 2026-05-01 - Claude
- Session Focus: Patch 0.1.4 — orchestrator + Claude skill for
  end-to-end "new homelab project" UX.
- Status: 0.1.4 closes the loop on the operator's UX target ("from
  `~/src/`, tell the LLM to start a new project, everything just
  happens"). Three entry points now converge on the same homelab
  profile: the existing `apply-profile.sh` (profile-only), the new
  `new-homelab-project.sh` (orchestrator that calls LLM-DocKit's
  `dockit-init-project.sh` + `apply-profile.sh` + optional GitHub
  creation), and a Claude skill `/new-homelab-project` that wraps
  the orchestrator with a five-question conversation and closes the
  loop by editing `home-infra/docs/PROJECTS.md`. The orchestrator
  was smoke-tested end-to-end against `/tmp/smoke-homelab` (validator
  6/6 PASS, two-commit history, `AGENTS.md` + `CLAUDE.md` symlink
  present). Effects visible to others stay opt-in: `--github` is the
  flag that authorises GitHub repo creation; the skill confirms a
  literal plan with the operator before any external effect.

## Patch 0.1.4 Outcome

- `integrations/dockit/new-homelab-project.sh`: POSIX `sh`
  orchestrator. Inputs: `<name>` plus optional flags
  (`--description`, `--host`, `--exposes-ui`, `--language`,
  `--target-dir`, `--github`, `--visibility`, `--dockit-source`).
  Steps: (1) validate (slug, target absent, GitHub name available
  if `--github`); (2) call
  `~/src/LLM-DocKit/scripts/dockit-init-project.sh` for the generic
  scaffold; (3) call `apply-profile.sh` for the homelab layer; (4)
  commit profile additions in the new project as a second commit;
  (5) `gh repo create … --source=… --push` if `--github`. Prints a
  suggested PROJECTS.md row at the end; explicitly does NOT edit
  `~/src/home-infra/` itself (the skill or the operator does that
  with judgement).
- `integrations/dockit/skills/new-homelab-project/SKILL.md`: Claude
  Code skill. Asks the operator five questions in one round (name,
  description, host, exposes-UI, GitHub now?), prints a literal
  plan, waits for confirmation, runs the orchestrator with the
  matching flags, then edits `~/src/home-infra/docs/PROJECTS.md`
  (Active Projects table + Project Details subsection) and commits
  + pushes there. Failure modes documented: target exists, GitHub
  name taken, `gh` not authenticated, partial-success after local
  steps — all leave the local repo intact, none trigger destructive
  cleanup.
- `integrations/dockit/INTEGRATION.md` rewritten to document the
  three entry points (orchestrator, skill, profile-only) and added
  a "Layering and single source of truth" section emphasising that
  all three converge on the same `apply-profile.sh` so profile
  logic cannot drift between callers.
- 25 doc-version targets synced via `scripts/bump-version.sh 0.1.4`.

## One-time setup for the operator

To make `/new-homelab-project` discoverable from any Claude Code
session, create a single symlink:

```sh
ln -s ~/src/home-infra-protocol/integrations/dockit/skills/new-homelab-project \
      ~/.claude/skills/new-homelab-project
```

After that, "quiero empezar un proyecto nuevo" (or any equivalent
phrase) inside Claude Code from `~/src/` is enough — Claude proposes
the skill, asks the five questions, and runs the orchestrator.

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
