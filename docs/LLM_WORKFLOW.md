<!-- doc-version: 0.3.0 -->
# LLM Workflow

LLM agents using this protocol should follow a simple discipline.

## Before Work

1. Read the source-of-truth repo handoff.
2. Read the relevant catalog entries.
3. Read the affected project contract or runbook if one exists.
4. State whether the work is infrastructure-changing or consumer-only.

## During Work

- Update human docs and catalogs in the same session as the live change.
- Do not invent missing fields.
- Mark unknowns explicitly.
- Keep telemetry separate from intent.

## When Changing Field Semantics

When a session changes the meaning, default, or required-when rule of an
existing field — or introduces a new field with a permissive default — it
must:

1. Re-sweep the affected adopter catalogs **read-only**. For this ecosystem,
   the canonical adopter is `~/src/home-infra/catalog/services.yml`.
2. Identify any entry where the new rule would be wrong (default no longer
   correct, required-when rule now triggers, etc.).
3. Halt and report drift to the operator. Do **not** edit cross-repo from
   this session — the catalog touch belongs to a separate operator-authorised
   commit in the source-of-truth repo.

This convention prevents the failure mode where a permissive default fires
silently for an adopter and the issue surfaces only when a user clicks a
broken affordance (DF-004 root cause: between protocol 0.2.0 and 0.3.0 the
`interface: web` default fired silently for `unifi-mcp` because the original
"MUST declare explicitly" rule covered only non-HTTP URLs, leaving HTTPS APIs
without HTML on the wrong side of the line).

## Before Claiming Completion

Run the Completion Rule checklist in `docs/COMPLETION_RULE.md`.
