<!-- doc-version: 0.10.1 -->
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

## Current Status (2026-07-18)

Protocol 0.10.1 is published with optional producer-owned `next_run_at`,
assertion-independent UTC-Z validation, explicit expired-plan semantics, and
schedule-mode presentation rules. Freshness remains strictly derived from
`observed_at + stale_after`. Infra Portal and the Plaud/ForumVault producers
have completed the first rollout; msgvault remains at its deploy-observe-
promote gate. DF-013 remains open and its second proxied-service recovery gate
is unchanged.

## Upcoming Milestones

1. Reconcile and deploy msgvault's isolated 0.24.0 schedule-evidence branch,
   observe a future producer-owned `next_run_at`, then let Home Infra promote
   it from `pending` to `required`.
2. Exercise the private all-surface closure model on one other proxied service.
3. Promote only recovery fields that survive both cases into a separate
   sanitized proposal; keep host identity, proxy products, secrets, backups,
   and commands private.
4. Sync LLM-DocKit 4.13.1 as a dedicated tooling patch after reviewing its
   session-gate and global Codex hook-installation boundary.
5. Keep later status and recovery vocabulary adopter-driven rather than adding
   speculative fields.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
