<!-- doc-version: 0.13.2 -->
# Home Infra Integration for LLM-DocKit projects

This directory ships an opt-in profile that any project scaffolded
from `cdelalama/LLM-DocKit` can apply when it participates in the
homelab.

## What this is

A small, idempotent set of files copied into a new project so that
any LLM agent working in that repo (Claude Code, Codex CLI, Cursor,
or any future tool) immediately sees:

- the homelab's source-of-truth conventions,
- the mandatory `home-infra` updates that infrastructure changes
  trigger,
- a deploy checklist that lists what "deploy is done" really means,
- an `infra.contract.yml` starter aligned with the protocol's current
  `sync_jobs[]`, `telemetry_jobs[]`, capability-transparency, and
  status-snapshot interfaces;
- a mechanical validation path that always executes the canonical validator
  from this protocol checkout.

The profile is **not mandatory** for any project. It is the
recommended starting point for projects that will run on a homelab
host (NAS, dev-vm, pihas, zwave, zigbee).

## Why a separate profile, not part of LLM-DocKit

`cdelalama/LLM-DocKit` is general-purpose and reused outside this
homelab. Embedding homelab-specific content there would couple the
template to one user's infrastructure.

This profile lives where it naturally belongs: inside
`home-infra-protocol`, the public repository that describes how the
homelab is structured. New projects scaffold with `LLM-DocKit` first
(per `docs/GOVERNANCE.md` *Project Bootstrap Rule*) and then opt
into this profile if they will participate in the homelab.

## Layer ownership (refactored 2026-05-12)

Project-creation orchestration lives in **ForgeOS** (operator-toolbox
layer per ForgeOS D-008); this repo owns the homelab contract
(schemas + profile + checklists). The two collaborate: ForgeOS's
orchestrator at `~/src/forgeos/scripts/new-homelab-project.sh`
calls `apply-profile.sh` from this repo (across repo boundaries)
to layer the homelab contract on top of any LLM-DocKit scaffold.
The Claude Code skill `/new-homelab-project` likewise lives at
`~/src/forgeos/skills/new-homelab-project/SKILL.md`.

Until 2026-05-11 both lived under
`integrations/dockit/new-homelab-project.sh` and
`integrations/dockit/skills/new-homelab-project/` in this repo as a
historical accident. The 2026-05-12 framework refactor (see
`home-infra/docs/SESSION_HANDOFF_2026-05-12_FRAMEWORK_REFACTOR.md`)
moved them to ForgeOS because they are behaviour, not contract; this
repo's mission is the contract (schemas + profile + checklists), not
operator-toolbox orchestration.

## What gets installed

| Path in target | Source | Notes |
|----------------|--------|-------|
| `AGENTS.md` | `templates/AGENTS.md` | Canonical, LLM-neutral context for any agent. |
| `CLAUDE.md` | symlink → `AGENTS.md` | Claude Code's loader path; same content. |
| `infra.contract.yml` | `templates/infra.contract.yml` | Starter contract with explicit removable sync, telemetry, and capability examples plus `TODO` placeholders. |
| `.claude/checklists/homelab-project.md` | `checklists/PROJECT_CHECKLIST.md` | Operational deploy checklist. |

Existing files are never overwritten. The script can be re-run
safely; it reports what it created and what it skipped. Before copying, it
validates the canonical template marker and required sections with
`scripts/validate-project-interface.py --template`.

## How to apply

There are four entry points, all converging on the same five files
(`AGENTS.md`, `CLAUDE.md` symlink, `infra.contract.yml`,
`.claude/checklists/homelab-project.md`).

### 1. End-to-end one-shot (recommended)

If the project does not exist yet, the simplest path is the
orchestrator script `new-homelab-project.sh` in ForgeOS (operator
toolbox). It calls `cdelalama/LLM-DocKit:scripts/dockit-init-project.sh`
first (generic scaffold), then `apply-profile.sh` from this repo (the
homelab layer), and optionally creates a GitHub repo and pushes.
Example:

```sh
~/src/forgeos/scripts/new-homelab-project.sh \
    my-new-thing \
    --description "What this does" \
    --host nas \
    --exposes-ui \
    --github
```

By default the orchestrator creates the new project at
`~/src/<name>`, defaults to language `Spanish`, and **does not**
create a GitHub repository unless `--github` is passed (effects
visible to others stay opt-in). It deliberately does not edit
`~/src/home-infra/`; the corresponding `docs/PROJECTS.md` entry is
the operator's responsibility (or the
`/new-homelab-project` Claude skill below).

By default the orchestrator looks for the homelab profile at
`~/src/home-infra-protocol/integrations/dockit/` (this directory).
Override with `--profile-source <path>` or `HOMELAB_PROFILE_ROOT` env
var when the checkout lives elsewhere.

Run with `--help` to see all flags:

```sh
~/src/forgeos/scripts/new-homelab-project.sh --help
```

### 2. Claude Code skill

`~/src/forgeos/skills/new-homelab-project/SKILL.md` ships a
conversational wrapper around the orchestrator. When the operator
says they want to start a new project for the homelab, the skill
asks five questions (name, description, host, exposes-UI, GitHub
now?), prints a literal plan, confirms, runs the orchestrator, then
edits `~/src/home-infra/docs/PROJECTS.md` to register the project
and commits + pushes in `home-infra`. One-time setup:

```sh
ln -s ~/src/forgeos/skills/new-homelab-project \
      ~/.claude/skills/new-homelab-project
```

After the symlink is in place, every Claude Code session can invoke
`/new-homelab-project` from any directory.

### 3. Apply profile to an existing project

If the project already exists (for example you scaffolded it with
`/adopt-dockit` or by hand), apply only the homelab layer:

```sh
~/src/home-infra-protocol/integrations/dockit/apply-profile.sh
```

Or with an explicit target:

```sh
~/src/home-infra-protocol/integrations/dockit/apply-profile.sh ~/src/<existing-project>
```

`apply-profile.sh` is POSIX `sh` and idempotent. It runs the canonical
side-effect-free template check, then uses only `cp`, `mkdir`, and `ln` for the
target. It never touches `~/src/home-infra/` and never edits files that already
exist in the target. It validates the source template; it does not pretend an
existing target contract is complete.

### 4. Implement the interface in an existing project

ForgeOS owns the operator workflow
`skills/implement-home-infra-interface/SKILL.md`. Use it after the project has
a real producer/status design. The skill reads the target project's own
onboarding, classifies each loop as sync or telemetry, makes capability
restrictions and enablement paths explicit, replaces/removes the starter
examples, validates the real contract plus representative snapshots,
and stops before any Home Infra or runtime mutation unless separately
authorized.

The skill calls the canonical validator here:

```sh
~/src/home-infra-protocol/scripts/validate-project-interface.py \
  --contract ~/src/<project>/infra.contract.yml \
  --status <job-id>=<representative-status.json>
```

The validator is not copied into ForgeOS or the adopter.

## Multi-LLM rationale (`AGENTS.md` is canonical)

The operator works in parallel with several LLM tools (Claude Code,
Codex CLI, Cursor, others) for cross-checking and consensus. To keep
context identical across them, the profile uses one canonical
content file (`AGENTS.md`, the emerging cross-tool convention) and
ships a `CLAUDE.md` symlink for Claude Code's loader. Any other tool
that needs a different filename can be added as another symlink to
the same source — the content lives in one place, never in two
copies that can drift.

## What this profile does NOT do

- Does not edit `~/src/home-infra/`. Catalog and inventory updates
  remain the operator's job during deploy, surfaced by the
  checklist.
- Does not treat a TODO-bearing starter as a valid real contract. Strict
  validation is a later project-owned implementation gate.
- Does not declare runtime success or protocol adoption from schema validation.
  A full deploy/evidence cycle and explicit source-of-truth acceptance remain
  separate.
- Does not add private adopter-only incubation such as `operational_review` or
  optional `operational_obligations` to the reusable profile. Projects add the
  normative section only when they have real dated work; the starter avoids
  placeholder obligations.
- Does not embed homelab content in `LLM-DocKit`. `LLM-DocKit` stays
  general-purpose; this profile is the homelab-specific layer.

## Layering and the single source of truth

All three entry points (orchestrator in ForgeOS, skill in ForgeOS,
profile-only here) converge on the same `apply-profile.sh` in this
repo for the homelab layer. The skill calls the orchestrator; the
orchestrator calls `dockit-init-project.sh` (LLM-DocKit) and then
`apply-profile.sh` (this repo) via a configurable cross-repo path.
There is exactly one place where "what the homelab profile installs"
is decided: `apply-profile.sh`, and one place where the contract/status shape
is validated: `scripts/validate-project-interface.py`. Higher layers add concerns
(orchestrator adds GitHub creation; skill adds the PROJECTS.md edit)
without duplicating profile or validation logic.

If `cdelalama/LLM-DocKit` later grows a native profile mechanism
(for example `dockit init --profile <path>` reading a `~/.dockitrc`
`default_profile`), the orchestrator and skill delegate to it and
this file's `apply-profile.sh` becomes a thin shim — but the same
content lives in one place.

## Related

- `~/src/home-infra/docs/CONVENTIONS.md` — homelab build/deploy
  patterns, Doppler, NAS quirks. The canonical operational document.
- `../../docs/PROJECT_CONTRACTS.md` — contract spec the template
  follows.
- `../../docs/GOVERNANCE.md` — project bootstrap rule, ownership,
  compliance-claim policy.
- `~/src/home-infra-protocol/SPEC.md` — protocol entities and
  required fields.
