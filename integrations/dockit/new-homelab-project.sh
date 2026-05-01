#!/bin/sh
# new-homelab-project.sh -- One-shot bootstrap for a new homelab project.
#
# Combines (1) the generic LLM-DocKit scaffold via
# scripts/dockit-init-project.sh in cdelalama/LLM-DocKit, (2) the homelab
# integration profile via ../apply-profile.sh in this repo, and (3)
# optionally a GitHub repo + push.
#
# Strict layering:
#   - dockit-init-project.sh handles generic scaffold (no GitHub, no profile).
#   - apply-profile.sh handles the homelab files (AGENTS.md, contract,
#     checklist).
#   - This script is the orchestrator. It never reimplements logic from the
#     other two; if both are unavailable it aborts.
#   - It does NOT edit ~/src/home-infra/. The caller (typically the
#     /new-homelab-project Claude skill) edits home-infra/docs/PROJECTS.md
#     and commits there with judgement, after this script returns.
#
# Usage:
#   new-homelab-project.sh <name> [options]
#
# Options:
#   --description "..."        One-line description (recorded in PROJECTS row).
#   --host <id>                Target host: nas | dev-vm | pihas | zwave | zigbee.
#   --exposes-ui               Mark that the project exposes UI/API/status.
#   --language <lang>          Conversation language (default: Spanish).
#   --target-dir <path>        Defaults to ~/src/<name>.
#   --github                   Create GitHub repo and push (otherwise local-only).
#   --visibility <v>           GitHub visibility: private (default) | public.
#   --dockit-source <path>     Override LLM-DocKit checkout (default: ~/src/LLM-DocKit).
#
# External effects:
#   - Local: creates a directory, runs git inside it. Aborts if target exists.
#   - GitHub: only when --github is passed. Aborts if cdelalama/<name> already
#     exists on GitHub.
#
# Exit codes:
#   0 success
#   1 validation failure (bad name, target exists, missing tool, name taken)
#   2 a sub-step failed (dockit-init-project, apply-profile, gh)

set -eu

PROJECT_NAME=""
DESCRIPTION=""
HOST=""
EXPOSES_UI=false
LANGUAGE="Spanish"
TARGET_DIR=""
CREATE_GITHUB=false
VISIBILITY="private"
DOCKIT_SOURCE="${LLM_DOCKIT_ROOT:-$HOME/src/LLM-DocKit}"
GH_OWNER="cdelalama"
TODAY=$(date +%Y-%m-%d)

PROFILE_DIR=$(cd "$(dirname "$0")" && pwd)

# ── Parse arguments ──────────────────────────────────────────────────────────

while [ $# -gt 0 ]; do
    case "$1" in
        --description)   DESCRIPTION="${2:?--description requires a value}"; shift 2 ;;
        --host)          HOST="${2:?--host requires a value}"; shift 2 ;;
        --exposes-ui)    EXPOSES_UI=true; shift ;;
        --language)      LANGUAGE="${2:?--language requires a value}"; shift 2 ;;
        --target-dir)    TARGET_DIR="${2:?--target-dir requires a path}"; shift 2 ;;
        --github)        CREATE_GITHUB=true; shift ;;
        --visibility)    VISIBILITY="${2:?--visibility requires a value}"; shift 2 ;;
        --dockit-source) DOCKIT_SOURCE="${2:?--dockit-source requires a path}"; shift 2 ;;
        --help|-h)
            sed -n '2,40p' "$0"
            exit 0
            ;;
        -*)
            echo "ERROR: unknown flag: $1" >&2
            exit 2
            ;;
        *)
            if [ -z "$PROJECT_NAME" ]; then
                PROJECT_NAME="$1"; shift
            else
                echo "ERROR: unexpected argument: $1" >&2
                exit 2
            fi
            ;;
    esac
done

# ── Validate inputs ──────────────────────────────────────────────────────────

if [ -z "$PROJECT_NAME" ]; then
    echo "ERROR: project name required" >&2
    sed -n '2,40p' "$0" >&2
    exit 1
fi

case "$PROJECT_NAME" in
    *[!a-z0-9-]*|"")
        echo "ERROR: project name must be a slug ([a-z0-9-]+): $PROJECT_NAME" >&2
        exit 1
        ;;
esac

case "$VISIBILITY" in
    private|public) ;;
    *) echo "ERROR: visibility must be 'private' or 'public', got: $VISIBILITY" >&2; exit 1 ;;
esac

if [ -n "$HOST" ]; then
    case "$HOST" in
        nas|dev-vm|pihas|zwave|zigbee) ;;
        *) echo "ERROR: --host must be one of: nas, dev-vm, pihas, zwave, zigbee" >&2; exit 1 ;;
    esac
fi

if [ -z "$TARGET_DIR" ]; then
    TARGET_DIR="$HOME/src/$PROJECT_NAME"
fi

if [ -e "$TARGET_DIR" ]; then
    echo "ERROR: target already exists: $TARGET_DIR" >&2
    exit 1
fi

# ── Locate the two underlying scripts ────────────────────────────────────────

DOCKIT_INIT="$DOCKIT_SOURCE/scripts/dockit-init-project.sh"
APPLY_PROFILE="$PROFILE_DIR/apply-profile.sh"

if [ ! -x "$DOCKIT_INIT" ]; then
    echo "ERROR: dockit-init-project.sh not found or not executable: $DOCKIT_INIT" >&2
    echo "Hint: ensure cdelalama/LLM-DocKit is at $DOCKIT_SOURCE and pulled." >&2
    exit 1
fi

if [ ! -x "$APPLY_PROFILE" ]; then
    echo "ERROR: apply-profile.sh not found or not executable: $APPLY_PROFILE" >&2
    exit 1
fi

# ── Pre-flight: GitHub name availability ─────────────────────────────────────

if [ "$CREATE_GITHUB" = true ]; then
    if ! command -v gh >/dev/null 2>&1; then
        echo "ERROR: --github requires the gh CLI to be installed and authenticated" >&2
        exit 1
    fi
    if gh repo view "$GH_OWNER/$PROJECT_NAME" >/dev/null 2>&1; then
        echo "ERROR: GitHub repo already exists: $GH_OWNER/$PROJECT_NAME" >&2
        echo "Refusing to overwrite. Pick another name or omit --github." >&2
        exit 1
    fi
fi

# ── Plan summary (informational) ─────────────────────────────────────────────

echo "Plan:"
echo "  Project:        $PROJECT_NAME"
echo "  Target dir:     $TARGET_DIR"
echo "  Language:       $LANGUAGE"
[ -n "$DESCRIPTION" ] && echo "  Description:    $DESCRIPTION"
[ -n "$HOST" ]        && echo "  Target host:    $HOST"
[ "$EXPOSES_UI" = true ] && echo "  Exposes UI:     yes"
echo "  LLM-DocKit:     $DOCKIT_SOURCE"
echo "  Homelab profile: $PROFILE_DIR"
if [ "$CREATE_GITHUB" = true ]; then
    echo "  GitHub:         create $GH_OWNER/$PROJECT_NAME ($VISIBILITY) and push"
else
    echo "  GitHub:         skipped (no --github flag)"
fi
echo ""

# ── Step 1: Generic LLM-DocKit scaffold ──────────────────────────────────────

echo "[1/4] Running dockit-init-project.sh ..."
"$DOCKIT_INIT" "$PROJECT_NAME" \
    --target-dir "$TARGET_DIR" \
    --language "$LANGUAGE" \
    --source "$DOCKIT_SOURCE" \
    || { echo "ERROR: dockit-init-project.sh failed" >&2; exit 2; }

# ── Step 2: Apply homelab profile ────────────────────────────────────────────

echo ""
echo "[2/4] Applying homelab profile ..."
"$APPLY_PROFILE" "$TARGET_DIR" \
    || { echo "ERROR: apply-profile.sh failed" >&2; exit 2; }

# ── Step 3: Commit the profile additions in the new project ─────────────────

cd "$TARGET_DIR"

if ! git diff --quiet || ! git diff --cached --quiet || \
   [ -n "$(git ls-files --others --exclude-standard)" ]; then
    git add -A
    git -c user.email='no-reply@local' -c user.name='homelab profile' \
        commit -q -m "chore: apply homelab profile

Installs AGENTS.md, CLAUDE.md (symlink), infra.contract.yml template
and .claude/checklists/homelab-project.md from
home-infra-protocol/integrations/dockit/." \
        || { echo "ERROR: profile commit failed" >&2; exit 2; }
    echo "  committed homelab profile additions"
else
    echo "  no changes to commit (profile may already have been applied)"
fi

# ── Step 4: GitHub (optional) ────────────────────────────────────────────────

if [ "$CREATE_GITHUB" = true ]; then
    echo ""
    echo "[3/4] Creating GitHub repo $GH_OWNER/$PROJECT_NAME ($VISIBILITY) ..."
    DESC_ARG=""
    [ -n "$DESCRIPTION" ] && DESC_ARG="--description $DESCRIPTION"
    # shellcheck disable=SC2086
    gh repo create "$GH_OWNER/$PROJECT_NAME" \
        "--$VISIBILITY" \
        --source="$TARGET_DIR" \
        --remote=origin \
        --push \
        $DESC_ARG \
        || { echo "ERROR: gh repo create failed (local repo intact at $TARGET_DIR)" >&2; exit 2; }
    echo "[4/4] Pushed to https://github.com/$GH_OWNER/$PROJECT_NAME"
else
    echo ""
    echo "[3/4] Skipped GitHub creation (no --github flag)"
    echo "[4/4] Local repository ready at $TARGET_DIR"
fi

# ── Suggested PROJECTS.md row (informational; the skill commits this) ────────

PROJECTS_VERSION="0.1.0"
PROJECTS_STATUS="Scaffolded"
[ "$EXPOSES_UI" = true ] && PROJECTS_STATUS="Scaffolded, exposes UI/API"

if [ -n "$HOST" ]; then
    PROJECTS_HOST="$HOST"
else
    PROJECTS_HOST="TBD"
fi

PROJECTS_ROW="| $PROJECT_NAME | ~/src/$PROJECT_NAME | $PROJECTS_VERSION | $PROJECTS_STATUS | $PROJECTS_HOST |"

echo ""
echo "Suggested row for ~/src/home-infra/docs/PROJECTS.md (Active Projects table):"
echo ""
echo "  $PROJECTS_ROW"
echo ""
echo "The /new-homelab-project skill will edit PROJECTS.md and commit + push"
echo "in home-infra. If you ran this script directly, do that step manually:"
echo "  cd ~/src/home-infra"
echo "  \$EDITOR docs/PROJECTS.md   # add the row above"
echo "  git add docs/PROJECTS.md && git commit -m \"chore: register new project $PROJECT_NAME\" && git push"
echo ""
echo "Summary:"
echo "  Local:   $TARGET_DIR"
[ "$CREATE_GITHUB" = true ] && echo "  Remote:  https://github.com/$GH_OWNER/$PROJECT_NAME"
echo "  Date:    $TODAY"
echo "  Done."
