<!-- doc-version: 0.10.1 -->
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
│   └── status-snapshot.schema.json
├── examples/
│   ├── home-infra/
│   │   ├── catalog/
│   │   │   ├── services.yml
│   │   │   └── hosts.yml
│   │   └── HANDOFF.md
│   └── project/
│       ├── infra.contract.yml
│       └── docs/
│           └── INFRA_CONTRACT.md
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── ARCHITECTURE.md
│   ├── COMPLETION_RULE.md
│   ├── PROJECT_CONTRACTS.md
│   ├── GOVERNANCE.md
│   ├── SECURITY_MODEL.md
│   ├── RECOVERY_MODEL.md
│   ├── PARALLEL_ENVIRONMENTS_PROPOSAL.md
│   ├── STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md
│   ├── SYNC_JOB_CONTRACT_PROPOSAL.md
│   ├── AUTHENTICATION_PLACEMENT_PROPOSAL.md
│   ├── LLM_WORKFLOW.md
│   ├── STRUCTURE.md
│   ├── VERSIONING_RULES.md
│   ├── version-sync-manifest.yml
│   ├── llm/
│   └── operations/
├── scripts/
│   ├── bump-version.sh
│   ├── check-version-sync.sh
│   ├── pre-commit-hook.sh
│   ├── dockit-generate-external-context.sh
│   └── dockit-validate-session.sh
├── src/
│   └── .gitkeep
└── tests/
    ├── .gitkeep
    ├── test_authentication_placement.py
    ├── test_status_snapshot_next_run.py
    └── test_status_snapshot_labels.py
```

## Notes

- `schemas/` contains protocol schema drafts.
- `examples/` must stay sanitized and generic.
- `src/` is reserved for future validator or reference tooling.
- `tests/` contains focused protocol/schema regression tests.
- `docs/llm/` is working memory for LLM-assisted maintenance.
