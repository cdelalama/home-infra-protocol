<!-- doc-version: 0.12.2 -->
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
| `docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md` | Non-normative human-action obligation design | Absolute occurrences; evidence completion stays project-owned |
| `scripts/validate-project-interface.py` | Canonical contract/status validation | No network or runtime mutation; invoked across repo boundaries |
| `integrations/dockit/` | Current homelab profile | Starter template includes sync and telemetry paths |

## Current Status (2026-08-07)

Protocol 0.12.2 closes DF-015's dated evidence review and publishes a
proposal-only operational-obligations design. The resolved backup trial and a
second real private pilot justify a neutral abstraction, while the lack of a
second independent implementation prevents a consumer-support claim.

The proposal assigns declaration to the project, acceptance and preservation
to Home Infra, runtime evidence to the project producer, time derivation to
each consumer, and delivery/acknowledgement to Hermes. Only matching verified
project evidence may satisfy an occurrence. Recurring policy stays private;
each occurrence is materialized with absolute UTC timestamps.

No normative semantics changed. `operational_review` remains absent from the
reusable profile and validator, and no obligation field exists in SPEC,
schemas, examples, templates, or validation. Existing `preview.expires_at`,
`next_run_at`, capability reviews, DF-016 incidents, freshness, recovery, and
health semantics remain separate.

## Upcoming Milestones

1. Obtain explicit maintainer acceptance or rejection of
   `docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md` before normative work.
2. If accepted, implement one additive protocol minor for the optional project
   declaration, sanitized projection, canonical validation, examples, and
   compatibility tests only.
3. Gate Home Infra, Infra Portal, Hermes, ForgeOS, and project adoption as
   separately authorized follow-up work.
4. Preserve the resolved backup trial as a regression fixture and use the
   current private pilot plus a real multi-frequency program for adoption
   evidence.
5. Keep recovery and DF-016 incident lifecycle work separate from operational
   obligations.
6. Sync LLM-DocKit as a dedicated tooling patch after reviewing its
   session-gate and global Codex hook-installation boundary.
7. Keep later status and recovery vocabulary adopter-driven rather than adding
   speculative fields.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
