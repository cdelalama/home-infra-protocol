<!-- doc-version: 0.2.0 -->
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
- an optional `infra.contract.yml` template aligned with the
  protocol's `docs/PROJECT_CONTRACTS.md`.

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

## What gets installed

| Path in target | Source | Notes |
|----------------|--------|-------|
| `AGENTS.md` | `templates/AGENTS.md` | Canonical, LLM-neutral context for any agent. |
| `CLAUDE.md` | symlink → `AGENTS.md` | Claude Code's loader path; same content. |
| `infra.contract.yml` | `templates/infra.contract.yml` | Optional, has `TODO:` placeholders. |
| `.claude/checklists/homelab-project.md` | `checklists/PROJECT_CHECKLIST.md` | Operational deploy checklist. |

Existing files are never overwritten. The script can be re-run
safely; it reports what it created and what it skipped.

## How to apply

There are three entry points, all converging on the same five files
(`AGENTS.md`, `CLAUDE.md` symlink, `infra.contract.yml`,
`.claude/checklists/homelab-project.md`).

### 1. End-to-end one-shot (recommended)

If the project does not exist yet, the simplest path is the
orchestrator script `new-homelab-project.sh` in this same directory.
It calls `cdelalama/LLM-DocKit:scripts/dockit-init-project.sh` first
(generic scaffold), then `apply-profile.sh` (the homelab layer), and
optionally creates a GitHub repo and pushes. Example:

```sh
~/src/home-infra-protocol/integrations/dockit/new-homelab-project.sh \
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

Run with `--help` to see all flags:

```sh
~/src/home-infra-protocol/integrations/dockit/new-homelab-project.sh --help
```

### 2. Claude Code skill

`integrations/dockit/skills/new-homelab-project/SKILL.md` ships a
conversational wrapper around the orchestrator. When the operator
says they want to start a new project for the homelab, the skill
asks five questions (name, description, host, exposes-UI, GitHub
now?), prints a literal plan, confirms, runs the orchestrator, then
edits `~/src/home-infra/docs/PROJECTS.md` to register the project
and commits + pushes in `home-infra`. One-time setup:

```sh
ln -s ~/src/home-infra-protocol/integrations/dockit/skills/new-homelab-project \
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

`apply-profile.sh` is POSIX `sh`, idempotent, and only runs `cp`,
`mkdir`, and `ln`. It never touches `~/src/home-infra/` and never
edits files that already exist in the target.

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
- Does not validate `infra.contract.yml`. No schema validator runs
  yet; that is planned for a later iteration of
  `home-infra-protocol/scripts/`.
- Does not declare protocol compliance. Any project that adopts this
  profile remains a candidate consumer until at least one full
  deploy cycle through the checklist proves the shape works.
- Does not embed homelab content in `LLM-DocKit`. `LLM-DocKit` stays
  general-purpose; this profile is the homelab-specific layer.

## Layering and the single source of truth

All three entry points (orchestrator, skill, profile-only) converge
on the same `apply-profile.sh` for the homelab layer. The skill
calls the orchestrator; the orchestrator calls
`dockit-init-project.sh` and then `apply-profile.sh`. There is
exactly one place where "what the homelab profile installs" is
decided: `apply-profile.sh`. Higher layers add concerns (orchestrator
adds GitHub creation; skill adds the PROJECTS.md edit) without
duplicating profile logic.

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
