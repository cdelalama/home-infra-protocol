<!-- doc-version: 0.13.6 -->
# Repository Structure

```text
home-infra-protocol/
├── README.md
├── SPEC.md
├── VERSION
├── CHANGELOG.md
├── LLM_START_HERE.md
├── HOW_TO_USE.md
├── schemas/
│   ├── services.schema.json
│   ├── hosts.schema.json
│   ├── project-contract.schema.json
│   ├── status-snapshot.schema.json
│   └── operational-obligations-projection.schema.json
├── examples/
│   ├── home-infra/
│   │   ├── catalog/
│   │   │   ├── services.yml
│   │   │   └── hosts.yml
│   │   ├── operational-obligations.json
│   │   └── HANDOFF.md
│   └── project/
│       ├── infra.contract.yml
│       ├── status/
│       │   └── telemetry.json
│       └── docs/
│           └── INFRA_CONTRACT.md
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── COMPLETION_RULE.md
│   ├── PROJECT_CONTRACTS.md
│   ├── CAPABILITY_TRANSPARENCY.md
│   ├── GOVERNANCE.md
│   ├── SECURITY_MODEL.md
│   ├── RECOVERY_MODEL.md
│   ├── PARALLEL_ENVIRONMENTS_PROPOSAL.md
│   ├── STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md
│   ├── SYNC_JOB_CONTRACT_PROPOSAL.md
│   ├── AUTHENTICATION_PLACEMENT_PROPOSAL.md
│   ├── RECOVERY_ACCEPTANCE_PROPOSAL.md
│   ├── INCIDENT_LIFECYCLE_PROPOSAL.md
│   ├── OPERATIONAL_OBLIGATIONS_PROPOSAL.md
│   ├── LLM_WORKFLOW.md
│   ├── STRUCTURE.md
│   ├── VERSIONING_RULES.md
│   ├── version-sync-manifest.yml
│   ├── llm/
│   └── operations/
├── scripts/
│   ├── bump-version.sh
│   ├── check-version-sync.sh
│   ├── validate-project-interface.py
│   ├── pre-commit-hook.sh
│   ├── dockit-generate-external-context.sh
│   └── dockit-validate-session.sh
├── src/
│   └── .gitkeep
└── tests/
    ├── .gitkeep
    ├── test_authentication_placement.py
    ├── test_capability_transparency.py
    ├── test_operational_obligations.py
    ├── test_project_interface_validator.py
    ├── test_status_snapshot_next_run.py
    └── test_status_snapshot_labels.py
```

## Notes

- `schemas/` contains protocol schema drafts.
- `examples/` must stay sanitized and generic.
- `scripts/validate-project-interface.py` is the canonical project
  contract/status validator; downstream repos invoke it without copying.
- `src/` is reserved for future reference tooling.
- `tests/` contains focused protocol/schema regression tests.
- `docs/llm/` is working memory for LLM-assisted maintenance.
