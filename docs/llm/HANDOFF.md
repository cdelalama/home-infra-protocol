<!-- doc-version: 0.3.0 -->
# LLM Work Handoff

This file is the current operational snapshot. Durable decisions live in
`docs/llm/DECISIONS.md`.

## Open work — next concrete step

**DF-004 closure** (option (a), patch **0.3.1**). The DF entry's
*Implementation hints (option (a))* block lists the exact files to touch,
the version bump, and the read-only cross-repo sweep. No proposal needed,
no Consensus run needed — the recommended option is already named in the
DF and the closure is a routine clarification + adopter guidance.

A fresh Claude Code session opening this repo should be able to read
`docs/DOWNSTREAM_FEEDBACK.md` DF-004 and `docs/LLM_WORKFLOW.md` and ship
0.3.1 without bespoke context. The master roadmap at
`~/src/home-infra/docs/SESSION_HANDOFF_2026-05-04_ECOSYSTEM_RECONCILIATION.md`
§3 *Session 6* points at this same task with the short prompt.

## Pending session — Ecosystem Reconciliation

A multi-day deliberation on 2026-05-02→04 produced two cross-repo proposals AND surfaced a significant prior-art gap: `~/src/llm-council` predates much of `LLM-DocKit/docs/CONSENSUS_PROTOCOL_PROPOSAL.md`. Reconciliation gated to Session 4 of the roadmap.

**Master roadmap**: `~/src/home-infra/docs/SESSION_HANDOFF_2026-05-04_ECOSYSTEM_RECONCILIATION.md`

**For this repo specifically**: Session 1 (Implement DEPLOYMENT_EVIDENCE_PROPOSAL.md) **shipped in 0.3.0** (this session). Session 4 is the one that produces `docs/ECOSYSTEM_MAP.md` here. Remaining sessions documented with copy-pasteable prompts in the master roadmap.

## Current Status

- Last Updated: 2026-05-06 - Claude Opus 4.7 (1M context) (meta cleanup — no code change, no schema change)
- Session Focus: Meta cleanup — close the gaps that were forcing bespoke prompts for routine DF closures. Three doc additions: (1) `docs/llm/HANDOFF.md` gains an *Open work — next concrete step* block at the top so a fresh session sees what to ship without conversational context; (2) `docs/LLM_WORKFLOW.md` gains a *When Changing Field Semantics* section formalising the read-only adopter-catalog sweep convention (the lesson DF-004 itself teaches at its tail); (3) `docs/DOWNSTREAM_FEEDBACK.md` template gains an *Implementation hints* block — actionable file-by-file translation of the chosen option — and DF-004 is retroactively populated with the block for option (a). Net effect: the dispatch prompt for closing DF-004 (Session 6 in the master roadmap) drops from ~100 lines of bespoke context to ~4 lines pointing at this repo's own docs. No version bump, no schema/SPEC contract change.

- Previous: Advisory turn 2026-05-06 (commit `20c2a1a`) — ecosystem-map summary + dispatch-prompt critique. No code change in that turn either. The current meta cleanup supersedes the bespoke-prompt approach implied by that advisory turn.

- Previous: Minor 0.3.0 — Deployment Evidence Contract shipped end-to-end per `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md` *Acceptance criteria*. `schemas/services.schema.json` gains the optional `deployment` block (`expected.image` + `expected.health` with `url`/`version_json_path`/`version`); `SPEC.md` *Service* gains the six-state vocabulary, the "operationally deployed" rule, the intent-vs-evidence rule, and a brief description of the `deployment` block; `examples/home-infra/catalog/services.yml` shows three of the five proposal scenarios on sanitized hostnames; `docs/PROJECT_CONTRACTS.md` notes the same block applies to project-level service objects. `docs/DOWNSTREAM_FEEDBACK.md` DF-003 → `implemented (0.3.0)`. Implementation 2026-05-03; commit + push 2026-05-04.

- Previous: Patch 0.2.5 — SPEC matrix row for `infra-portal` synced to 0.8.1 (the `expect_status` ground-truth bug fix shipped in `infra-portal` immediately after 0.8.0 was promoted, when the post-deploy audit surfaced unifi-mcp permanently `down` because of the same logic gap). Doc-only on this side; the bug fix + tests + deploy live in `infra-portal`.

- Previous: Patch 0.2.4 — DF-002 closed in production. The operator promoted `infra-portal:0.8.0` to NAS following the six-step evidence plan; runtime evidence confirmed (`docker ps` healthy, `/api/health` 0.8.0, mosquitto `up`, `interface` field exposed). DF-002 status moves from `partially implemented` to `implemented (protocol 0.2.0 + infra-portal 0.8.0 in production from 2026-05-03)`. First time the "operationally deployed" rule from `DEPLOYMENT_EVIDENCE_PROPOSAL.md` is fully satisfied in production.

- Previous: Patch 0.2.3 — mechanical fix-forward after a GPT-5
  audit caught two status-string drifts introduced by 0.2.2: DF-002
  was marked `implemented` but the new "operationally deployed"
  ontology requires production evidence (only repo evidence exists),
  and DF-029 in LLM-DocKit used the non-legend status
  `partially accepted`. Both corrected. No schema change. The earlier
  0.2.2 work — the `DEPLOYMENT_EVIDENCE_PROPOSAL.md` and the
  consensus REVIEWS entry — stands.
- Previous: Patch 0.2.2 — Deployment Evidence Contract proposal +
  REVIEWS audit trail filed. (1) `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md`
  introduced the six lifecycle states, the intent-vs-evidence rule,
  and the optional `deployment` block on `Service`, with acceptance
  checklist. (2) `docs/llm/REVIEWS.md` recorded the consensus run that
  produced the proposal. (3) `docs/DOWNSTREAM_FEEDBACK.md` DF-003 →
  `accepted` with cross-reference. (4) Manifest extended. The
  proposal was self-contained so a future session could read it cold;
  that future session shipped in 0.3.0 (this entry's *Session Focus*
  above).

## Pending Proposals (for the next session)

(none — `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md` shipped in 0.3.0.)

The next structural extension surfaced by the new contract is
consumer-side: `infra-portal` (or a future `infra-agent`) reads
`deployment.expected.health.version` and reports drift in
`INFO/WARN/FAIL` terms. That work lives in the consumer repos, not
here.

## Open DF entries

- **DF-004** — Default `interface: web` when omitted is unsafe for
  HTTP APIs without HTML. Status: `open`. Mitigated in source projects
  (catalog now declares `interface: api` for the affected services).
  Three options (SPEC clarification → validator check → schema-required
  in v1.0) named in the entry; sequence (a)→(b)→(c).

## Patch 0.2.1 Outcome

- `SPEC.md`: *Consumer support for `interface`* matrix updated to
  reflect `infra-portal 0.8.0` (commit `717f468` in that repo).
  `Renders by interface`: yes. `TCP probe`: yes. Notes spell out
  the dispatch rules (`web` → open in tab; `none` → silent no-op;
  `api`/`mqtt`/`tcp`/`ssh`/`other` → clipboard copy + toast) and
  the production-vs-repo gap (production still runs 0.7.2).
- `docs/DOWNSTREAM_FEEDBACK.md`: DF-002 moved from
  `partially implemented (protocol 0.2.0)` to
  `implemented (protocol 0.2.0 + infra-portal 0.8.0)`. DF-001 was
  already `implemented (0.2.0)`.
- 27 doc-version targets synced via `scripts/bump-version.sh 0.2.1`.

## Minor 0.2.0 Outcome

- `schemas/services.schema.json`: added `interface` (string,
  optional) under each service item. Description names the
  recommended enum and the rule that the field SHOULD be explicit
  when the URL is not `http(s)://`. `additionalProperties: true`
  is preserved at both the service-item and root level, so
  consumers built against 0.1.x continue to load 0.2.0 catalogs
  without modification — they simply ignore the new field.
- `SPEC.md`: *Service* section gains `interface` in Recommended
  fields, plus a sub-section that documents the seven recommended
  values, the implicit default (`web`), and the explicit
  requirement when `url` is not `http(s)://`. A new *Consumer
  support for `interface`* matrix is the permanent guardrail
  against the DF-002 class of bug ("schema accepts X, consumer
  doesn't implement X"). The matrix initially lists `infra-portal`
  with `(pending)` cells; the portal updates them when the
  consumer-side change ships.
- `examples/home-infra/catalog/services.yml`: existing `infra` and
  `home-dashboard` entries gain `interface: web` to model the
  explicit-when-already-web pattern. Two new entries added:
  `example-mqtt` (`mqtt://broker.example.internal:1883`,
  `interface: mqtt`, `status.type: tcp`) and `example-api`
  (`https://api.example.internal/v1`, `interface: api`). Examples
  stay sanitized — no real LAN IPs, hostnames, or domains.
- `docs/PROJECT_CONTRACTS.md`: notes that when a project lists
  service objects (rather than just ids), `interface` follows the
  same convention as `Service.interface`.
- `docs/DOWNSTREAM_FEEDBACK.md`: DF-001 status moves from
  `accepted` to `implemented (0.2.0)`. DF-002 status moves from
  `open` to `partially implemented (protocol 0.2.0)`, with the
  rationale that the matrix is the (b) guardrail and (a) is the
  consumer-side TCP probe still pending in `infra-portal`.
- 27 doc-version targets synced via
  `scripts/bump-version.sh 0.2.0`.

## Patch 0.1.6 Outcome

- `docs/DOWNSTREAM_FEEDBACK.md` created. Format mirrors
  `LLM-DocKit:docs/DOWNSTREAM_FEEDBACK.md`. Two inaugural entries
  (DF-001 field-gap, DF-002 semantic-gap / consumer-drift) anchor
  the channel with real adopter evidence.
- `docs/SERVICE_INTERFACE_PROPOSAL.md` created. Self-contained
  implementation brief: problem, decision (option 3 of three),
  exact files to change, default-and-required rules, recommended
  enum values, migration path for existing catalogs, consumer-side
  responsibilities, schema-evolution sanity-check, acceptance
  criteria. Designed so a future session can read it cold and ship.
- `docs/version-sync-manifest.yml` extended with the two new
  documents (27 total markers).
- 27 doc-version targets synced via `scripts/bump-version.sh 0.1.6`.
- This patch deliberately changes nothing about SPEC, schemas, or
  examples — those changes are reserved for 0.2.0.

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
