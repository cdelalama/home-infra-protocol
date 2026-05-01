<!-- doc-version: 0.1.3 -->
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

From the new project's root:

```sh
~/src/home-infra-protocol/integrations/dockit/apply-profile.sh
```

Or pass the target explicitly:

```sh
~/src/home-infra-protocol/integrations/dockit/apply-profile.sh ~/src/<new-project>
```

The script is POSIX `sh`, idempotent, and only runs `cp`, `mkdir`,
and `ln`. It never touches `~/src/home-infra/` and never edits files
that already exist in the target.

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

## Future: native profile support in LLM-DocKit

When `LLM-DocKit` grows a generic profile mechanism (for example
`dockit init --profile <path>` reading a `~/.dockitrc`
`default_profile`), the same `apply-profile.sh` logic delegates to
that mechanism without changing this profile's content. Until then,
the manual invocation above is the supported path.

A Claude Code skill `/new-homelab-project <name>` is a separate,
optional convenience wrapper. If implemented, it should call the
exact same `apply-profile.sh` so the two entry points cannot
diverge.

## Related

- `~/src/home-infra/docs/CONVENTIONS.md` — homelab build/deploy
  patterns, Doppler, NAS quirks. The canonical operational document.
- `../../docs/PROJECT_CONTRACTS.md` — contract spec the template
  follows.
- `../../docs/GOVERNANCE.md` — project bootstrap rule, ownership,
  compliance-claim policy.
- `~/src/home-infra-protocol/SPEC.md` — protocol entities and
  required fields.
