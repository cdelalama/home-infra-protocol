<!-- doc-version: 0.2.3 -->
# How To Use This Repository

Home Infra Protocol is currently a draft specification repository.

## Read First

1. `LLM_START_HERE.md`
2. `SPEC.md`
3. `docs/PROJECT_CONTEXT.md`
4. `docs/ARCHITECTURE.md`
5. `docs/GOVERNANCE.md`
6. `docs/COMPLETION_RULE.md`
7. `docs/PROJECT_CONTRACTS.md`
8. `docs/llm/HANDOFF.md`

## Intended Build Path

1. Stabilize the v0.1 protocol vocabulary.
2. Add JSON Schemas for catalog and project contract entities.
3. Add sanitized examples.
4. Add a validator CLI.
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
