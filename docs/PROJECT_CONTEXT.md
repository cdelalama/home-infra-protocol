<!-- doc-version: 0.12.0 -->
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
| `scripts/validate-project-interface.py` | Canonical contract/status validation | No network or runtime mutation; invoked across repo boundaries |
| `integrations/dockit/` | Current homelab profile | Starter template includes sync and telemetry paths |

## Current Status (2026-07-30)

Protocol 0.12.0 adds optional project capability declarations and runtime
capability observations. It makes support, policy, scope, risk, restriction
reason, and enablement path explicit while keeping runtime availability in a
project-owned telemetry snapshot. The canonical validator enforces declaration
and observation identity, job ownership, completeness, and the policy/evidence
boundary.

This first publication defines the producer contract and reusable profile.
Consumer support remains unclaimed until a real Infra Portal release passes
strict-ingress, strict-egress, stale, mismatch, and operator-UI evidence.

DF-015 remains privately incubated until its 2026-08-04 evidence review.
`operational_review` is deliberately absent from the reusable profile and
validator. Existing `next_run_at`, freshness, recovery, and authority semantics
remain unchanged.

## Upcoming Milestones

1. Exercise capability transparency through one real project producer, Home
   Infra acceptance, Infra Portal rendering, and Hermes self-description.
2. Record consumer support only after runtime evidence exists.
3. Review DF-015 on 2026-08-04 without pre-promoting its private field.
4. Exercise the private all-surface closure model on one other proxied service.
5. Promote only recovery fields that survive both cases into a separate
   sanitized proposal; keep host identity, proxy products, secrets, backups,
   and commands private.
6. Sync LLM-DocKit as a dedicated tooling patch after reviewing its
   session-gate and global Codex hook-installation boundary.
7. Keep later status and recovery vocabulary adopter-driven rather than adding
   speculative fields.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
