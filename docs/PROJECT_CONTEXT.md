<!-- doc-version: 0.11.0 -->
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
| `scripts/validate-project-interface.py` | Canonical contract/status validation | No network or runtime mutation; invoked across repo boundaries |
| `integrations/dockit/` | Current homelab profile | Starter template includes sync and telemetry paths |

## Current Status (2026-07-28)

Protocol 0.11.0 adds the first canonical executable validator for project
contracts and representative status snapshots. The homelab profile now reflects
the proven `sync_jobs[]` / `telemetry_jobs[]` interface instead of its stale May
prototype, and ForgeOS invokes the validator rather than copying it. This is a
validator/profile release, not a new status or job semantic.

DF-015 remains privately incubated until its 2026-08-04 evidence review.
`operational_review` is deliberately absent from the reusable profile and
validator. Existing `next_run_at`, freshness, recovery, and authority semantics
remain unchanged.

## Upcoming Milestones

1. Exercise the canonical validator through ForgeOS project creation and the
   dedicated interface-implementation workflow; fix validator bugs here rather
   than copying patches downstream.
2. Review DF-015 on 2026-08-04 without pre-promoting its private field.
3. Exercise the private all-surface closure model on one other proxied service.
4. Promote only recovery fields that survive both cases into a separate
   sanitized proposal; keep host identity, proxy products, secrets, backups,
   and commands private.
5. Sync LLM-DocKit as a dedicated tooling patch after reviewing its
   session-gate and global Codex hook-installation boundary.
6. Keep later status and recovery vocabulary adopter-driven rather than adding
   speculative fields.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
