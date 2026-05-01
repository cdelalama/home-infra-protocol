#!/bin/sh
# apply-profile.sh — Apply the homelab profile to a target project directory.
#
# Idempotent. Existing files are never overwritten; existing CLAUDE.md is
# never replaced. Re-running the script after a partial apply finishes the
# job without surprises.
#
# Usage:
#   apply-profile.sh                 # apply to current directory
#   apply-profile.sh <target-dir>    # apply to <target-dir>
#
# What it does:
#   - Copy templates/AGENTS.md to <target>/AGENTS.md
#   - Symlink <target>/CLAUDE.md -> AGENTS.md (Claude Code's loader path)
#   - Copy templates/infra.contract.yml to <target>/infra.contract.yml
#   - Copy checklists/PROJECT_CHECKLIST.md to
#     <target>/.claude/checklists/homelab-project.md
#
# What it does NOT do:
#   - Edit ~/src/home-infra/ in any way
#   - Validate the contract or run any check
#   - Overwrite any file already present in the target

set -eu

TARGET="${1:-.}"
PROFILE_DIR=$(cd "$(dirname "$0")" && pwd)

if [ ! -d "$TARGET" ]; then
    echo "ERROR: target directory not found: $TARGET" >&2
    exit 1
fi

cd "$TARGET"
TARGET_ABS=$(pwd)

CREATED=0
SKIPPED=0

# 1. Canonical AGENTS.md
if [ -e AGENTS.md ]; then
    echo "skip   AGENTS.md (already present)"
    SKIPPED=$((SKIPPED + 1))
else
    cp "$PROFILE_DIR/templates/AGENTS.md" AGENTS.md
    echo "create AGENTS.md"
    CREATED=$((CREATED + 1))
fi

# 2. CLAUDE.md as symlink to AGENTS.md (Claude Code loader compatibility)
if [ -e CLAUDE.md ] || [ -L CLAUDE.md ]; then
    echo "skip   CLAUDE.md (already present)"
    SKIPPED=$((SKIPPED + 1))
else
    ln -s AGENTS.md CLAUDE.md
    echo "link   CLAUDE.md -> AGENTS.md"
    CREATED=$((CREATED + 1))
fi

# 3. infra.contract.yml (template with TODO placeholders)
if [ -e infra.contract.yml ]; then
    echo "skip   infra.contract.yml (already present)"
    SKIPPED=$((SKIPPED + 1))
else
    cp "$PROFILE_DIR/templates/infra.contract.yml" infra.contract.yml
    echo "create infra.contract.yml"
    CREATED=$((CREATED + 1))
fi

# 4. Project checklist under .claude/checklists/
mkdir -p .claude/checklists
if [ -e .claude/checklists/homelab-project.md ]; then
    echo "skip   .claude/checklists/homelab-project.md (already present)"
    SKIPPED=$((SKIPPED + 1))
else
    cp "$PROFILE_DIR/checklists/PROJECT_CHECKLIST.md" \
       .claude/checklists/homelab-project.md
    echo "create .claude/checklists/homelab-project.md"
    CREATED=$((CREATED + 1))
fi

echo ""
echo "Homelab profile applied to: $TARGET_ABS"
echo "Created: $CREATED   Skipped: $SKIPPED"
echo ""
echo "Next: open AGENTS.md and follow the required reading order."
