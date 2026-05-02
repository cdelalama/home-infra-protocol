<!-- doc-version: 0.1.6 -->
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
│   └── project-contract.schema.json
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
    └── .gitkeep
```

## Notes

- `schemas/` contains protocol schema drafts.
- `examples/` must stay sanitized and generic.
- `src/` is reserved for future validator or reference tooling.
- `docs/llm/` is working memory for LLM-assisted maintenance.
