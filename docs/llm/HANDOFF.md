<!-- doc-version: 0.1.5 -->
# LLM Work Handoff

This file is the current operational snapshot. Durable decisions live in
`docs/llm/DECISIONS.md`.

## Current Status

- Last Updated: 2026-05-01 - Claude
- Session Focus: Patch 0.1.5 — three GPT-5-review fixes against the
  0.1.4 ship.
- Status: 0.1.5 fixes three real issues found by GPT-5 reviewing the
  freshly published 0.1.4. (1) `new-homelab-project.sh` was
  splitting a `--description` with spaces into multiple args to
  `gh repo create`; rewritten to use POSIX positional parameters so
  the description survives as a single argv element. (2)
  `PROJECT_CHECKLIST.md` listed `docker compose restart edge-caddy`
  or `caddy reload` as equivalent — both wrong on QNAP NAS where
  `docker compose` is not on PATH and reload alone may not pick up
  new vhosts; replaced with the full compose-plugin path and an
  explicit note preferring `restart` for new vhosts. (3)
  `templates/AGENTS.md` mandated PROJECTS.md updates "whenever a
  project bumps version" — too aggressive for projects with
  frequent internal patches; scoped to deployed-reality changes
  (project created or retired, deployed version on a host changes,
  status / host / exposure / URL changes). End-to-end smoke test
  against `/tmp/smoke-homelab` confirmed: branch is `main`, AGENTS.md
  reflects the new wording, checklist reflects the QNAP path,
  `set --` quoting verified mechanically with a description
  containing spaces (argv[7] = the entire description).

## Patch 0.1.5 Outcome

- `integrations/dockit/new-homelab-project.sh`: `gh repo create`
  invocation rewritten to build argv via POSIX positional
  parameters. `set -- "$GH_OWNER/$PROJECT_NAME" "--$VISIBILITY"
  "--source=$TARGET_DIR" --remote=origin --push` then conditionally
  `set -- "$@" --description "$DESCRIPTION"` if non-empty, then
  `gh repo create "$@"`. Verified by stubbing `gh` with a printer
  and reading argv element by element: the description with three
  spaces survives as a single arg.
- `integrations/dockit/checklists/PROJECT_CHECKLIST.md`: edge-caddy
  reload step now uses the full path
  `/usr/local/lib/docker/cli-plugins/docker-compose -f
  /share/Container/compose/edge-caddy/docker-compose.yml restart
  edge-caddy`, with a note that `restart` is the safer pattern for
  new vhosts (Caddy's `reload` may not pick up new sites depending
  on how it was started). The QNAP-specific path is required
  because `docker compose` is not on PATH on QNAP per
  `~/src/home-infra/docs/CONVENTIONS.md`.
- `integrations/dockit/templates/AGENTS.md`: PROJECTS.md
  mandatory-update rule tightened. Was: "whenever a project is
  created, bumps version, or changes status" — too aggressive for
  projects with frequent internal patches. Now: deployed-reality
  scope (created / retired, deployed version on a host changes,
  status / host / exposure changes). Internal patches that don't
  reach a host don't warrant a PROJECTS.md update.
- 25 doc-version targets synced via `scripts/bump-version.sh 0.1.5`.

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
