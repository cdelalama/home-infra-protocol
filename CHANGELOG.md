<!-- doc-version: 0.1.4 -->
# Changelog

All notable changes to Home Infra Protocol are tracked here.

## [0.2.5] - 2026-05-03

### Changed

- `SPEC.md` *Consumer support for `interface`* matrix: row for `infra-portal` updated from version `0.8.0` to `0.8.1`. Notes column documents the new `expect_status` ground-truth contract (non-2xx codes like `406` from MCP `/mcp` and `404` by-design endpoints can be declared healthy). Bug surfaced by the post-deploy audit on 2026-05-03 — unifi-mcp was permanently `down` despite the operator confirming the MCP is in active use; root cause was `httpProbe` gating `up` behind `acceptable === 2xx-3xx` even when `matches === true`. Fix shipped in `infra-portal` 0.8.1 with 11 unit tests; production updated in the same session. Doc-only patch on this side.

## [0.2.4] - 2026-05-03

### Changed

- **DF-002 closed in production**: status moves from `partially
  implemented (protocol 0.2.0 + infra-portal repo 0.8.0; deployment
  to production pending)` to `implemented (protocol 0.2.0 +
  infra-portal 0.8.0 in production from 2026-05-03)` after the
  operator promoted `infra-portal:0.8.0` to NAS following the
  six-step evidence plan in `~/src/home-infra/docs/SESSION_HANDOFF_2026-05-04_ECOSYSTEM_RECONCILIATION.md`
  §8. Runtime evidence: `docker ps` healthy, `/api/health` returns
  `0.8.0`, `mosquitto` status flipped from `unknown` to `up`,
  `interface` field exposed in `/api/catalog`. The "operationally
  deployed" rule from `DEPLOYMENT_EVIDENCE_PROPOSAL.md` is now
  satisfied for the first time in production.

## [0.2.3] - 2026-05-03

### Fixed

- **DF-002 status corrected** to match the new ontology in
  `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md`. Previous status read
  `implemented (protocol 0.2.0 + infra-portal 0.8.0)`, but the new
  rule on "operationally deployed" requires `running` and `serving`
  to be confirmed by runtime evidence — and `infra-portal` 0.8.0
  only exists in repo, not in production (production runs `0.7.2`).
  The status is now `partially implemented (protocol 0.2.0 +
  infra-portal repo 0.8.0; deployment to production pending)`.
  Found by GPT-5 audit: the proposal's first ejemplar would have
  contradicted itself.
- **DF-029 status normalised in LLM-DocKit** (cross-repo follow-up
  of the same audit): the previous draft used the non-legend
  status `partially accepted`. Corrected to `accepted` in
  `~/src/LLM-DocKit/docs/DOWNSTREAM_FEEDBACK.md`, with a note
  clarifying that the DF moves to `partially implemented (X.Y.Z)`
  only when an actual template change ships in a release. Tracked
  in the LLM-DocKit commit of the same date.
- This patch is itself an instance of the Consensus Protocol's
  failure mode "decision later overturned" applied to documentation
  drift, captured here without a new REVIEWS entry because the
  change is mechanical (status text alignment), not deliberative.

## [0.2.2] - 2026-05-03

### Added

- `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md`: self-contained proposal for
  the Deployment Evidence Contract, addressing DF-002 + DF-003 + the
  cross-protocol DF-029 in LLM-DocKit. Introduces a typed six-state
  lifecycle vocabulary (`declared / implemented / built / transferred
  / running / serving`), an explicit intent-vs-evidence rule, and an
  optional `deployment` block on `Service` with nested `expected.image`
  and `expected.health` sub-blocks. Severity levels (INFO/WARN/FAIL)
  are defined as semantics, not enforcement. Five concrete homelab
  scenarios documented inline as acceptance test for the schema. Five
  anti-patterns named explicitly. The proposal does not implement the
  schema change; that is the next session's job, with the acceptance
  checklist included.
- `docs/llm/REVIEWS.md`: structured audit-trail entry for the consensus
  run that produced the proposal. Format follows the new
  `CONSENSUS_PROTOCOL_PROPOSAL.md` *Recording mechanism* in LLM-DocKit.
  Captures causality (who proposed what, which objection changed which
  decision, what risk was accepted) — not transcript. Eight load-bearing
  decisions documented; three explicit rejections.
- `docs/version-sync-manifest.yml`: `DEPLOYMENT_EVIDENCE_PROPOSAL.md`
  added (28 markers total).

### Changed

- `docs/DOWNSTREAM_FEEDBACK.md`: DF-003 status moved from `open` to
  `accepted` with cross-reference to the new proposal. DF-002 narrative
  updated to reflect the deploy-lag gap (repo `infra-portal` 0.8.0
  vs production 0.7.2) — the symptom that motivated the run.

### Fixed

## [0.2.1] - 2026-05-02

### Changed

- `SPEC.md` *Consumer support for `interface`* matrix: row for
  `infra-portal` updated from `(pending)/(pending)/(pending)` to
  `0.8.0 / yes / yes` after the consumer-side change shipped in
  `infra-portal` commit `717f468`. Notes column documents the
  dispatch rules (`web` → open in tab; `none` → silent no-op +
  toast; `api`/`mqtt`/`tcp`/`ssh`/`other` → clipboard copy + toast)
  and explicitly calls out that production still runs
  `infra-portal:0.7.2` until the operator promotes the image — so
  adopters reading the matrix do not infer that production already
  supports the new values.
- `docs/DOWNSTREAM_FEEDBACK.md`: DF-002 moves from
  `partially implemented (protocol 0.2.0)` to
  `implemented (protocol 0.2.0 + infra-portal 0.8.0)`. DF-001 was
  already `implemented (0.2.0)` since the previous bump. The two
  inaugural DF entries are now both closed and stay in place as an
  audit trail for future adopters.

## [0.2.0] - 2026-05-02

### Added

- `Service.interface` field (string, optional) on `schemas/services.schema.json`.
  First additive schema field since 0.1.0; first concrete result of the
  `DOWNSTREAM_FEEDBACK.md` channel installed in 0.1.6. Recommended enum:
  `web | api | mqtt | tcp | ssh | none | other`. Schema stays additive
  (`additionalProperties: true`) so 0.1.x consumers ignore the new field.
- `SPEC.md` *Service* section documents the seven recommended values, the
  implicit default (`web`) for backward compatibility, and the rule that
  `interface` MUST be set explicitly when `url` is not `http(s)://`.
- `SPEC.md` gains a *Consumer support for `interface`* matrix listing which
  schema values which known consumer supports as of which version. This is
  the permanent guardrail against the DF-002 class of failure ("schema
  accepts X, consumer doesn't implement X"). Initial row for `infra-portal`
  shows `(pending)` cells; the portal updates them when its consumer-side
  change ships.
- `examples/home-infra/catalog/services.yml` shows three values: existing
  `infra` and `home-dashboard` entries gain `interface: web` (explicit-
  when-already-web pattern), plus two new sanitized entries `example-mqtt`
  (`mqtt://broker.example.internal:1883`, `interface: mqtt`,
  `status.type: tcp`) and `example-api` (`https://api.example.internal/v1`,
  `interface: api`).
- `docs/PROJECT_CONTRACTS.md` notes that when a project lists service
  objects under `services` rather than just ids, each object's `interface`
  follows the same convention as `Service.interface`.

### Changed

- `docs/DOWNSTREAM_FEEDBACK.md`: DF-001 status moves from `accepted` to
  `implemented (0.2.0)`. DF-002 status moves from `open` to
  `partially implemented (protocol 0.2.0)` — the SPEC.md matrix is the (b)
  guardrail; the consumer-side cure (a, TCP probe in `infra-portal`)
  is tracked in that repo's HANDOFF *Pending work* item 1.

### Fixed

## [0.1.6] - 2026-05-02

### Added

- `docs/DOWNSTREAM_FEEDBACK.md`: living log of real-adopter observations
  about protocol gaps, modelled on `LLM-DocKit:docs/DOWNSTREAM_FEEDBACK.md`.
  Format: `DF-NNN` entries with Source / Date / Category / Status /
  Observation / Protocol implication. The protocol's `GOVERNANCE.md`
  *Field Policy* requires real-adopter motivation for every new field;
  this file is the canonical channel where that motivation gets
  captured. Two inaugural entries:
  - **DF-001** — `Service` records a single `url` but adopters need to
    declare whether the service has a navigable web UI. Surfaced by
    `tomatic` choosing to expose Mosquitto (a non-web service) in the
    catalog and `infra-portal` rendering an "open" button that fails
    silently. Status: `accepted`.
  - **DF-002** — `status.type: "tcp"` is in the schema enum but
    `infra-portal` v0.7.2 doesn't implement it (`health.ts:82-86`
    returns "not implemented"). The schema and consumer have drifted.
    Status: `open`.
- `docs/SERVICE_INTERFACE_PROPOSAL.md`: self-contained implementation
  proposal addressing DF-001. Adds an optional `interface` field to
  `Service` (recommended values: `web | api | mqtt | tcp | ssh | none |
  other`). Default is `web` for backward compatibility; explicit value
  required when `url` is not `http(s)://`. Schema stays additive
  (`additionalProperties: true`). Includes concrete file-by-file edits,
  acceptance checklist, and migration path for the next session to
  execute. The proposal also recommends adding a "Consumer support
  matrix" to SPEC.md as a permanent guardrail against the DF-002 class
  of failure (schema accepts X, consumer doesn't implement X).
- Both new docs added to `docs/version-sync-manifest.yml` (27 targets
  total).

### Changed

- The protocol now has a documented mechanism for evolving from real
  adopter signals: adopters file `DF-NNN` entries; structural changes
  go through `docs/*_PROPOSAL.md` documents; the audit trail stays
  visible. This closes the previously implicit gap where the
  GOVERNANCE field-policy rule existed but no canonical channel did.

### Fixed

## [0.1.5] - 2026-05-01

### Fixed

- `integrations/dockit/new-homelab-project.sh`: `--description` with
  spaces was being split into multiple arguments to `gh repo create`.
  The previous build constructed `DESC_ARG="--description $DESCRIPTION"`
  and expanded it unquoted, so `--description "Project with words"`
  reached `gh` as four separate positional args. Fixed using POSIX
  positional parameters (`set -- ... ; set -- "$@" --description
  "$DESCRIPTION"`) so the description survives as a single argv
  element regardless of internal spacing.
- `integrations/dockit/checklists/PROJECT_CHECKLIST.md`: the
  edge-caddy reload step previously listed `docker compose restart
  edge-caddy` or `caddy reload` as equivalent options. Both are
  wrong on QNAP NAS — the `docker compose` subcommand is not on
  PATH there (per `home-infra/docs/CONVENTIONS.md`) and `caddy
  reload` may not pick up newly added vhosts depending on how
  Caddy was started. Replaced with the full compose-plugin path
  (`/usr/local/lib/docker/cli-plugins/docker-compose -f
  /share/Container/compose/edge-caddy/docker-compose.yml restart
  edge-caddy`) and a note that `restart` is the safer pattern for
  new vhosts.

### Changed

- `integrations/dockit/templates/AGENTS.md`: tightened the
  `docs/PROJECTS.md` mandatory-update rule. Previously said
  "whenever a project is created, bumps version, or changes
  status" — too aggressive for projects with frequent internal
  patches. Now scopes the rule to **deployed reality**: project
  created or retired, deployed version on a host changes, status
  changes, host placement changes, exposure (UI / API / URL)
  changes. Internal patch releases that never reach a host do not
  warrant a PROJECTS.md update. Found by GPT-5 review.

## [0.1.4] - 2026-05-01

### Added

- `integrations/dockit/new-homelab-project.sh`: orchestrator that
  bootstraps a brand-new homelab project end-to-end. Runs
  `cdelalama/LLM-DocKit:scripts/dockit-init-project.sh` for the
  generic scaffold, then `apply-profile.sh` for the homelab layer,
  then optionally `gh repo create` + push when `--github` is
  passed. GitHub creation is opt-in (effects visible to others stay
  explicit). Aborts if the target directory already exists or if
  `cdelalama/<name>` is already taken on GitHub. Smoke-tested
  end-to-end against `/tmp/smoke-homelab`: validator 6/6 PASS, two
  commits in the new project (initial scaffold + apply homelab
  profile), `AGENTS.md` present, `CLAUDE.md` is the symlink.
- `integrations/dockit/skills/new-homelab-project/SKILL.md`:
  Claude Code skill that wraps the orchestrator with a five-question
  conversation (name, description, host, exposes-UI, GitHub now?),
  prints a literal plan, confirms, runs the orchestrator, then
  edits `~/src/home-infra/docs/PROJECTS.md` to register the project
  and commits + pushes in `home-infra`. One-time setup is a single
  symlink under `~/.claude/skills/`.

### Changed

- `integrations/dockit/INTEGRATION.md`: now documents three entry
  points (orchestrator, skill, profile-only) instead of just the
  profile-only path. Added a "Layering and single source of truth"
  section emphasising that all three entry points converge on the
  same `apply-profile.sh` for the homelab layer; higher layers add
  concerns (orchestrator adds GitHub creation; skill adds the
  PROJECTS.md edit) without duplicating profile logic.

### Fixed

## [0.1.3] - 2026-05-01

### Added

- New directory `integrations/dockit/`: opt-in profile for projects
  scaffolded from `cdelalama/LLM-DocKit` that participate in the
  homelab. Five files:
  - `INTEGRATION.md` — what the profile is, how to apply, design
    rationale, multi-LLM rationale (`AGENTS.md` canonical).
  - `templates/AGENTS.md` — LLM-neutral agent context for the new
    project (required reading order, mandatory `home-infra` updates
    rule, anti-rules).
  - `templates/infra.contract.yml` — protocol-aligned contract
    template with `TODO:` placeholders. Optional and experimental.
  - `checklists/PROJECT_CHECKLIST.md` — operational deploy checklist
    (build, secrets, runtime, network/TLS, source-of-truth updates,
    project docs, optional contract, smoke checks).
  - `apply-profile.sh` — POSIX `sh` script, idempotent. Copies the
    files into a target project; symlinks `CLAUDE.md → AGENTS.md`
    so Claude Code's loader picks up the same content. Never
    overwrites existing files.
- `integrations/dockit/INTEGRATION.md` added to
  `docs/version-sync-manifest.yml`.

### Changed

- This profile is intentionally hosted in `home-infra-protocol`,
  not in `LLM-DocKit`. `LLM-DocKit` stays general-purpose; the
  protocol owns the homelab-specific layer. A future native
  `dockit init --profile <path>` mechanism would delegate to the
  same `apply-profile.sh` to keep entry points in sync.

### Fixed

## [0.1.2] - 2026-05-01

### Added

- README "Ecosystem map" section listing the four ecosystem
  repositories alongside this one, with role and visibility per
  repo. The map makes the public/private split explicit so
  external readers can see why source-of-truth and consumer repos
  are intentionally not on GitHub publicly.

### Changed

- README clarifies that `LLM-DocKit` is kept separate from this
  protocol on purpose, so it can stay general-purpose. New
  ecosystem projects scaffold from `LLM-DocKit` first per
  `docs/GOVERNANCE.md` *Project Bootstrap Rule* and may opt into
  the protocol's contracts as they mature.

### Fixed

## [0.1.1] - 2026-05-01

### Added

- Added `docs/GOVERNANCE.md` with field policy, ownership boundaries,
  project bootstrap rules, and compliance-claim freshness rules.
- Documented that new ecosystem projects should start from LLM-DocKit unless
  the user explicitly approves a waiver.

### Changed

- Linked the governance rules from the README, spec, usage guide, start-here
  guide, and structure map.

### Fixed

## [0.1.0] - 2026-05-01

### Added

- Created the project from LLM-DocKit.
- Added the first draft protocol specification.
- Added JSON Schema drafts for services, hosts, and project contracts.
- Added sanitized examples for a source-of-truth repo and project contract.
- Documented completion, security, recovery, LLM workflow, and project contract
  direction.
