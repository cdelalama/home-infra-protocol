<!-- doc-version: 0.1.4 -->
# Changelog

All notable changes to Home Infra Protocol are tracked here.

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
