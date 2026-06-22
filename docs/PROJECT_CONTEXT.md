<!-- doc-version: 0.7.0 -->
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
- Defer runtime tooling until the specification has stabilized.

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

## Current Status (2026-06-22)

Protocol 0.7.0 implements the parallel-runtime and development-preview
anti-rot contract. Development runtimes remain optional, but when they exist
the protocol can group them with production, declare preview lifecycle, and
make side-effect ownership auditable.

## Upcoming Milestones

1. Adopt the 0.7.0 service fields in the private `home-infra` catalog and
   auditor.
2. Teach `infra-portal` to group parallel production/development runtimes and
   render lifecycle/side-effect warnings.
3. Keep project-owned sync/telemetry adoption moving through real adopters
   such as `msgvault-lab`, host-capacity telemetry, and ForumVault.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
