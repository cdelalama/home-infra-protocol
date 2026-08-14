<!-- doc-version: 0.13.4 -->
# How To Use This Repository

Home Infra Protocol is a specification and executable contract-validation
repository.

## Read First

1. `LLM_START_HERE.md`
2. `SPEC.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/ARCHITECTURE.md`
5. `docs/GOVERNANCE.md`
6. `docs/COMPLETION_RULE.md`
7. `docs/PROJECT_CONTRACTS.md`
8. `docs/STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md`
9. `docs/SYNC_JOB_CONTRACT_PROPOSAL.md`
10. `docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md`
11. `docs/llm/HANDOFF.md`

## Intended Build Path

1. Stabilize the v0.1 protocol vocabulary.
2. Add JSON Schemas for catalog and project contract entities.
3. Add sanitized examples.
4. Validate project contracts and their representative status snapshots with
   `scripts/validate-project-interface.py`.
5. Make private implementations such as `home-infra` declare which protocol
   version they implement.
6. Make consumers such as `infra-portal` declare which protocol version they
   consume.

## Documentation Rule

Every meaningful change should update:

- `docs/llm/HANDOFF.md`
- `docs/llm/HISTORY.md`
- relevant specification, schema, example, or architecture docs

The protocol's value depends on keeping the spec, schemas, and examples aligned.

## Validate A Project Interface

For a completed project-owned contract:

```bash
scripts/validate-project-interface.py \
  --contract /path/to/project/infra.contract.yml \
  --status <job-id>=/path/to/project/status.json \
  --obligations-projection /path/to/operational-obligations.json \
  --previous-obligations-projection /path/to/previous-operational-obligations.json
```

Repeat `--status` for each representative job snapshot. The validator never
contacts a runtime or Home Infra and does not prove deployment or acceptance.

When a project intentionally limits a product or agent feature, declare it in
`capabilities[]` rather than leaving the restriction only in environment
variables or prose. Non-enabled policies require a stable reason and explicit
enablement path. Runtime proof is published by the referenced telemetry job
and joined by exact capability id.

When a project requires dated human work, declare optional
`operational_obligations[]`. Materialize one-time or recurring occurrences as
absolute UTC windows, name the runbook and evidence requirement, and keep
commands out of `action`. Home Infra publishes the complete sanitized
projection; use `--obligations-projection` to validate its scope, authority,
declaration joins, evidence, and supersession against the project contract.
During Home Infra acceptance, also pass the previous accepted projection so a
stable series cannot change kind and a stable occurrence cannot silently
change its window; changed deadlines require a new superseding occurrence id.

The validator does not execute an action, acknowledge a notification,
calculate consumer state for a live clock, or prove Home Infra acceptance.
Passing shape and join validation is not deployment evidence.

For the canonical starter only:

```bash
scripts/validate-project-interface.py \
  --contract integrations/dockit/templates/infra.contract.yml \
  --template
```
