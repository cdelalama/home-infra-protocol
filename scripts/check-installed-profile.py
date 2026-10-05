#!/usr/bin/env python3
"""Report installed homelab guidance drift; never overwrite adopter files."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "AGENTS.md": "integrations/dockit/templates/AGENTS.md",
    ".claude/checklists/homelab-project.md": "integrations/dockit/checklists/PROJECT_CHECKLIST.md",
}
HEADING = "## Required integration validation"
LIMIT = 1024 * 1024
SECTIONS = {
    "AGENTS.md": ["Mandatory updates", "Required integration validation"],
    ".claude/checklists/homelab-project.md": ["Required consumers (owner-resolved obligations)", "Required integration validation"],
}
RETIRED = {
    "portal_visible_conditional": r"only\s+(?:if|when)[\s\S]{0,100}?portal.visible",
    "retired_portal_sync": r"(?:infra-portal/)?scripts/sync-catalog-to-nas\.sh",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalized(data):
    return data.decode("utf-8-sig").replace("\r\n", "\n").rstrip() + "\n"


def comparable(text):
    return re.sub(r"\[[xX ]\]", "[ ]", text)


def section(text, title):
    matches = list(re.finditer(r"^## " + re.escape(title) + r"[ \t]*$", text, re.M))
    if len(matches) != 1:
        return None
    return re.split(r"^## ", text[matches[0].end():], maxsplit=1, flags=re.M)[0].strip()


def lineage(profile_root, template):
    """Published ancestors only. Historical equality is evidence, not a heuristic."""
    def git(*args):
        return subprocess.check_output(["git", "-C", str(profile_root), *args],
                                       stderr=subprocess.DEVNULL, timeout=10)
    try:
        revisions = git("log", "origin/main", "--format=%H", "--", template).decode().splitlines()
        result = {}
        for revision in revisions:
            text = normalized(git("show", revision + ":" + template))
            result.setdefault(comparable(text), {"revision": revision,
                "version": git("show", revision + ":VERSION").decode().strip()})
        return result
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return {}


def integration_section(text):
    matches = list(re.finditer(r"^" + re.escape(HEADING) + r"\s*$", text, re.M))
    if len(matches) != 1:
        return None
    remainder = text[matches[0].end():]
    return re.split(r"^## ", remainder, maxsplit=1, flags=re.M)[0].strip()


def read_bounded(path, root):
    # Refuse redirected instructions, including symlinked parent directories.
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("instruction path leaves project root")
    for parent in (path, *path.parents):
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError("instruction path uses a symlink")
    with path.open("rb") as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("instruction file exceeds size limit")
    return data


def inspect(project, profile_root=ROOT, published_history=True):
    project = Path(project).resolve(strict=True)
    if not project.is_dir():
        raise ValueError("project root is not a directory")
    rows = []
    for target, template in FILES.items():
        expected = read_bounded(profile_root / template, profile_root)
        expected_text = normalized(expected)
        expected_section = integration_section(expected_text)
        if not expected_section:
            raise ValueError("canonical integration section is missing or ambiguous")
        canonical_sections = {title: section(expected_text, title) for title in SECTIONS[target]}
        if any(value is None for value in canonical_sections.values()):
            raise ValueError("canonical required section is missing or ambiguous")
        row = {"path": target, "expected_sha256": digest(expected)}
        historical = lineage(profile_root, template) if published_history else {}
        try:
            actual = read_bounded(project / target, project)
            actual_text = normalized(actual)
            integration = integration_section(actual_text)
            row.update(sha256=digest(actual), integration_section=(
                "current" if integration == expected_section else
                "missing_or_ambiguous" if integration is None else "different"))
            row["state"] = ("pristine_current" if comparable(actual_text) == comparable(expected_text) else
                            "pristine_stale" if comparable(actual_text) in historical else "customized")
            if row["state"] == "pristine_stale":
                row["historical_match"] = historical[comparable(actual_text)]
            row["eol_only"] = actual != expected and actual_text == expected_text
            row["retired_guidance"] = [name for name, pattern in RETIRED.items()
                                       if re.search(pattern, actual_text, re.I)]
            row["sections"] = {}
            for title in SECTIONS[target]:
                current_section = canonical_sections[title]
                installed_section = section(actual_text, title)
                if installed_section is None:
                    status = "missing_or_ambiguous"
                elif comparable(installed_section) == comparable(current_section):
                    status = "current"
                elif any(comparable(installed_section) == comparable(section(old, title) or "") for old in historical):
                    status = "stale"
                else:
                    status = "customized"
                row["sections"][title] = status
        except FileNotFoundError:
            row.update(state="missing", integration_section="missing")
        except (OSError, ValueError, UnicodeError):
            row.update(state="unverified", integration_section="unverified")
        rows.append(row)
    alias = project / "CLAUDE.md"
    try:
        if alias.is_symlink():
            alias_state = "canonical_link" if alias.resolve(strict=True) == project / "AGENTS.md" else "different_target"
        elif alias.exists():
            alias_text = normalized(read_bounded(alias, project))
            if alias_text.strip() == "AGENTS.md":
                alias_state = "symlink_materialized"
            elif not (project / "AGENTS.md").exists():
                alias_state = "standalone_file"
            else:
                alias_state = "matching_copy" if alias_text == normalized(read_bounded(project / "AGENTS.md", project)) else "different_copy"
        else:
            alias_state = "missing"
    except (OSError, ValueError, UnicodeError):
        alias_state = "unverified"
    complete = all(r["state"] == "pristine_current" for r in rows) and alias_state in {"canonical_link", "matching_copy"}
    absent = all(r["state"] == "missing" for r in rows) and alias_state == "missing"
    try:
        git_state = subprocess.check_output(["git", "-C", str(project), "status", "--porcelain", "--", *FILES, "CLAUDE.md"],
                                           text=True, stderr=subprocess.DEVNULL, timeout=10).splitlines()
        head = subprocess.check_output(["git", "-C", str(project), "rev-parse", "HEAD"], text=True,
                                       stderr=subprocess.DEVNULL, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        git_state, head = None, None
    return {"project_root": str(project), "result": "NOT_ADOPTED" if absent else "CURRENT" if complete else "REVIEW_REQUIRED",
            "files": rows, "claude_alias": alias_state,
            "head": head, "working_guidance_changes": git_state,
            "bytes_observed": "working_tree", "mutations": False,
            "scope": "Installed instruction equality only; not integration or runtime acceptance."}


def source_identity():
    def git(*args):
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True,
                                       stderr=subprocess.DEVNULL, timeout=10).strip()
    return {"revision": git("rev-parse", "HEAD"),
            "modified": bool(git("status", "--porcelain", "--", *FILES.values(),
                                 "scripts/check-installed-profile.py")),
            "network_freshness": "not_checked"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = {"schema_version": 1, "source": source_identity(), **inspect(args.project)}
        print(json.dumps(result, indent=2))
        return 0  # Report-only: never changes an integration or deployment verdict.
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError):
        print(json.dumps({"result": "UNVERIFIED", "message": "Cannot inspect canonical profile or project root."}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
