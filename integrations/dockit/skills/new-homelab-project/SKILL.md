---
description: Bootstrap a brand-new project that participates in the homelab. Asks the operator a few questions, scaffolds from LLM-DocKit, applies the homelab profile, optionally creates the GitHub repo, then registers the project in home-infra/docs/PROJECTS.md. Use when the operator says they want to start a new project from `~/src/` (or anywhere) and the project will run on a homelab host.
---

# Skill: New homelab project

This skill is a thin conversational layer over
`~/src/home-infra-protocol/integrations/dockit/new-homelab-project.sh`.
The script does the structural work; this file documents how to drive
it from a Claude Code session and how to close the loop in
`~/src/home-infra/docs/PROJECTS.md`.

The operator's UX target is: from `~/src/`, type "quiero empezar un
proyecto nuevo" (or invoke `/new-homelab-project` directly) and the
agent does everything from there.

## When to use

Trigger this skill when **all** of the following hold:

- The operator wants to start a **new** project (not adopt an
  existing one — `/adopt-dockit` covers that case).
- The project will run on a homelab host (NAS, dev-vm, pihas,
  zwave, zigbee), or its host placement is undecided but the
  operator confirms it belongs to the homelab.
- The project does not exist yet at `~/src/<name>/` or as a
  GitHub repo at `cdelalama/<name>`.

If the operator wants a project that is explicitly **not** part of
the homelab (for example a ForgeOS general-purpose tool), do not
apply this skill. Use `dockit-init-project.sh` directly instead and
skip the homelab profile.

## Pre-flight checks

Before asking any question, verify silently:

- `~/src/LLM-DocKit/scripts/dockit-init-project.sh` exists and is
  executable. If not, stop and tell the operator the LLM-DocKit
  checkout is missing or stale.
- `~/src/home-infra-protocol/integrations/dockit/new-homelab-project.sh`
  exists and is executable.
- `~/src/home-infra-protocol/integrations/dockit/apply-profile.sh`
  exists and is executable.
- `~/src/home-infra/docs/PROJECTS.md` exists.
- `gh auth status` succeeds (only if the operator will likely want a
  GitHub repo; the orchestrator validates this itself, so a missing
  `gh` is recoverable — just disable the GitHub option if absent).

## Questions to ask the operator

Ask the minimum set in one round (use the AskUserQuestion tool when
available, or a clear bullet list otherwise). All have defaults:

1. **Project name** (slug, `[a-z0-9-]+`). No default.
2. **One-line description** for README and the homelab catalog.
   Default: empty (skipped).
3. **Target host** (where it will run): `nas`, `dev-vm`, `pihas`,
   `zwave`, `zigbee`, or `TBD` if not yet decided. Default: `TBD`.
4. **Will it expose a UI / API / status endpoint?** (yes/no).
   Default: no. Affects the PROJECTS.md status text and is a hint
   that an `edge-caddy` route will likely be added later.
5. **Create the GitHub repo and push now?** (yes/no). Default: yes.
   If yes, visibility is `private` unless the operator says
   otherwise.

Do not ask for `--language` — read it from
`~/.claude/CLAUDE.md` (the operator's global instructions name the
conversation language). If absent, default to Spanish.

## Build a plan and confirm

Before running anything, print a literal plan to the operator:

```
Plan:
  1. Create directory ~/src/<name>
  2. Scaffold from LLM-DocKit X.Y.Z (language: <lang>)
  3. Apply homelab profile (AGENTS.md + CLAUDE.md symlink + checklist + contract template)
  4. Initial git commit (chore: initial scaffold + chore: apply homelab profile)
  5. Create GitHub repo cdelalama/<name> (<visibility>)         [only if confirmed]
  6. Push to origin/main                                         [only if confirmed]
  7. Edit ~/src/home-infra/docs/PROJECTS.md adding row:
       | <name> | ~/src/<name> | 0.1.0 | <status text> | <host> |
  8. Commit + push in ~/src/home-infra
       chore: register new project <name>

Proceed? [Y/n]
```

`<status text>`:
- "Scaffolded" if no UI exposed,
- "Scaffolded, exposes UI/API" if UI exposed.

If the operator says no or wants to change anything, adjust and
re-print the plan. Do not start until they confirm.

## Execute the plan

After confirmation:

### Step 1 — Run the orchestrator

Run the orchestrator script with the appropriate flags. Use the
shell directly:

```sh
~/src/home-infra-protocol/integrations/dockit/new-homelab-project.sh \
    <name> \
    --target-dir ~/src/<name> \
    --language "<lang>" \
    [--description "<desc>"] \
    [--host <host>] \
    [--exposes-ui] \
    [--github [--visibility private|public]]
```

Read the script's stdout. If it exits non-zero, stop and report
the failure to the operator with the exact stdout/stderr; do not
attempt to "recover" — the script is designed to fail loud and the
operator decides.

If the script succeeds, the script's stdout contains a "Suggested
row for ~/src/home-infra/docs/PROJECTS.md" block. Use that exact
row in the next step.

### Step 2 — Edit `home-infra/docs/PROJECTS.md`

The orchestrator deliberately does NOT touch `home-infra` (per the
ownership rule: bash scripts are too brittle for that table; an
LLM with the Edit tool is the right operator).

Edit `~/src/home-infra/docs/PROJECTS.md`:

1. Read the file.
2. Locate the `## Active Projects` section's table.
3. Append the suggested row (from the orchestrator's stdout) as the
   **last row** of the Active Projects table. Match the existing
   column alignment style.
4. If the project name is a clear "template / utility" (developer
   tool not running as a service), use the `## Template / Utility
   Projects` table instead. Most projects belong in *Active*; ask
   the operator if unsure.
5. Add a `### <name>` subsection at the bottom of the
   `## Project Details` section with:
   - `**Purpose**: <description>` (use the description from the
     plan; if empty, leave a TODO).
   - `**Stack**: TODO` (the operator fills in once code lands).
   - `**Repo**: ~/src/<name>` and the GitHub URL if the repo was
     created.
   - `**Status**: Scaffolded YYYY-MM-DD`.

Keep the additions minimal — this is a register entry, not a full
project page. The new project's own docs/llm/HANDOFF.md is the
operational hub for that project; PROJECTS.md is just the index.

### Step 3 — Commit and push `home-infra`

In `~/src/home-infra`:

```sh
cd ~/src/home-infra
git add docs/PROJECTS.md
git commit -m "chore: register new project <name>

<one-line description if provided>

Scaffolded from LLM-DocKit. Repo at ~/src/<name>.
GitHub: https://github.com/cdelalama/<name>      # only if created
Target host: <host>"
git push origin main
```

This commit is conceptually distinct from the new project's own
commits; do not merge them.

### Step 4 — Final report

Print to the operator:

- New project location: `~/src/<name>`.
- GitHub URL if created.
- The two new project commits (orchestrator output) and the
  one home-infra commit (your action).
- Suggest: `cd ~/src/<name>` and start the first session by
  reading `AGENTS.md` and editing `docs/PROJECT_CONTEXT.md`.
- Note: the homelab checklist at
  `.claude/checklists/homelab-project.md` is now in the new
  project; remind the operator (and any future agent) to walk
  through it before declaring deploy done.

## Failure modes and how to handle them

- **Target dir already exists**: orchestrator aborts cleanly. Tell
  the operator; do not delete anything.
- **GitHub name taken**: orchestrator aborts before any local
  changes. Suggest a different name to the operator.
- **`gh` not authenticated**: orchestrator aborts. Tell the
  operator to run `gh auth login`, or re-run without `--github` to
  create local-only.
- **Local steps succeed but `gh repo create` fails after**: the
  local repo is intact at `~/src/<name>` with two commits. Do not
  delete it. Suggest the operator run `gh repo create
  cdelalama/<name> --private --source=~/src/<name> --push`
  manually after fixing the underlying issue.
- **PROJECTS.md edit fails or commit fails**: the new project
  exists and works; only the registry entry is missing. Tell the
  operator and offer to retry the edit.

Never run destructive cleanup (`rm -rf`) automatically. The
operator decides.

## Anti-patterns

- Do not ask the operator to confirm step-by-step. One plan, one
  confirmation, then execute.
- Do not reimplement what `new-homelab-project.sh` does. Always
  call it. If the orchestrator is missing or broken, that is a bug
  to report, not a reason to inline its logic.
- Do not edit anything in `~/src/home-infra/` other than
  `docs/PROJECTS.md`. INVENTORY.md, SERVICES.md and the catalog
  belong to the deploy phase, which has its own checklist in the
  new project's `.claude/checklists/homelab-project.md`.
- Do not push without an explicit confirmed plan, especially for
  GitHub.

## Reference

- `~/src/home-infra-protocol/integrations/dockit/new-homelab-project.sh`
  — the orchestrator. Read it if you are unsure what flags do what.
- `~/src/home-infra-protocol/integrations/dockit/INTEGRATION.md`
  — design rationale and what the homelab profile installs.
- `~/src/LLM-DocKit/scripts/dockit-init-project.sh`
  — the generic LLM-DocKit scaffold (called by the orchestrator).
- `~/src/home-infra/docs/CONVENTIONS.md` — homelab build/deploy
  patterns (the new project's own AGENTS.md links here).
