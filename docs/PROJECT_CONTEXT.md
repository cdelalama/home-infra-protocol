<!-- doc-version: 0.13.3 -->
# Project Context - Home Infra Protocol

## Vision

Home Infra Protocol is a reusable specification for Git-based infrastructure
memory. It lets humans, dashboards, MCP servers, recovery workflows, and LLM
agents agree on what infrastructure exists, where truth lives, and when a
change is complete.

The protocol is motivated by a private implementation: `home-infra` as the
source-of-truth repository and `infra-portal` as a read-only consumer. This repo
extracts the reusable pattern without publishing private operational details.

## Objectives

- Define a minimal vocabulary for hosts, services, projects, dependencies,
  runbooks, probes, and consumers.
- Publish schemas for machine-readable catalogs and project contracts.
- Document the completion rule for human and LLM-assisted infrastructure
  changes.
- Provide sanitized examples that private repos can copy.
- Provide a canonical, side-effect-free validator that projects and
  orchestrators invoke without copying.
- Make project capabilities and intentional restrictions visible, explainable,
  runtime-verifiable, and evolvable without turning consumers into authorities.

## Stakeholders

- Product owner: Carlos de la Lama-Noriega
- Technical owner: Carlos de la Lama-Noriega
- Primary users: Carlos and LLM agents operating his infrastructure
- Future users: homelab and small-infra operators who want LLM-readable
  infrastructure memory

## Architectural Overview

The protocol separates source-of-truth repositories from consumers.

```text
source-of-truth repo
  human docs + machine catalogs
        |
        +--> visual portal
        +--> MCP server
        +--> validators
        +--> recovery workflows
```

Consumers may observe, render, validate, and warn. They must not silently become
authorities over inventory or intent.

## Key Components

| Component | Purpose | Notes |
|-----------|---------|-------|
| `SPEC.md` | Main protocol definition | Draft v0.1 |
| `schemas/` | JSON Schema drafts | Services, hosts, project contracts |
| `examples/` | Sanitized example repos/contracts | No real LAN details |
| `docs/COMPLETION_RULE.md` | Definition of done for infrastructure changes | Core LLM discipline |
| `docs/PROJECT_CONTRACTS.md` | Project-level contract direction | Future ingestion from project repos |
| `docs/CAPABILITY_TRANSPARENCY.md` | Capability declaration and runtime-evidence contract | Policy stays separate from availability |
| `docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md` | Evidence and rationale for the normative human-action contract | Absolute occurrences; evidence completion stays project-owned |
| `schemas/operational-obligations-projection.schema.json` | Strict sanitized accepted egress | Complete scope, publisher freshness, project evidence, no notification detail |
| `scripts/validate-project-interface.py` | Canonical contract/status validation | No network or runtime mutation; invoked across repo boundaries |
| `integrations/dockit/` | Current homelab profile | Starter template includes sync and telemetry paths |

## Current Status (2026-08-09)

Protocol 0.13.0 implemented DF-015 as an optional additive project declaration
and complete sanitized accepted projection. Protocol 0.13.1 corrects the
reference ordering so `due_at` and `starts_at` are compared as UTC instants,
including mixed fractional-second encodings, before any adopter pins the
contract. The resolved backup trial, a second real private pilot, and a
documented multi-frequency recovery workflow ground the contract without
claiming downstream adoption.

Protocol 0.13.2 records the first real recurring adoption chain without
changing the contract. NAS Backup declares three recovery series containing
34 absolute occurrences, Home Infra 0.16.0 accepts and continuously publishes
their complete sanitized projection, and Infra Portal 0.27.1 consumes it with
restart-durable last-valid continuity. All projected evidence remains missing
and no occurrence is completed. The adopter intentionally remains pinned to
the accepted 0.13.1 contract revision; this patch is documentation only.

Protocol 0.13.3 repairs the release-integrity defect exposed when ForgeOS
validated the reusable profile against the 0.13.2 checkout: `VERSION` had
advanced while the profile marker remained 0.13.1. The profile marker is now a
first-class version-sync target updated by the official bump script. This
tooling correction changes no contract, adopter pin, authority, or runtime.

The contract assigns declaration to the project, acceptance and preservation
to Home Infra, runtime evidence to the project producer, time derivation to
each consumer, and delivery/acknowledgement to Hermes. Only matching verified
project evidence may satisfy an occurrence. Recurring policy stays private;
each occurrence is materialized with absolute UTC timestamps.

The canonical validator enforces nested series/occurrence identity,
absolute windows, runbook joins, non-executable actions, complete projection
scope, project authority, evidence, and supersession. Completion, timeliness,
time state, channel integrity, next selection, and recurring ordering remain
derived. Recurring-series state is not applicable to one-time obligations.
Legacy
`operational_review` and the optional declaration both remain absent from the
reusable starter template. Existing `preview.expires_at`, `next_run_at`,
capability reviews, DF-016 incidents, freshness, recovery, and health semantics
remain separate.

## Upcoming Milestones

1. Add Hermes read-only consumption, deterministic delivery and a private
   acknowledgement ledger under a separately authorized adopter slice.
2. Evaluate proactive Buzz transport separately from projection consumption
   and keep delivery/acknowledgement distinct from project evidence.
3. Preserve the resolved backup trial as a regression fixture and the current
   recurring chain as the first real multi-frequency adoption record.
4. Keep recovery and DF-016 incident lifecycle work separate from operational
   obligations.
5. Sync LLM-DocKit as a dedicated tooling patch after reviewing its
   session-gate and global Codex hook-installation boundary.
6. Keep later status and recovery vocabulary adopter-driven rather than adding
   speculative fields.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
