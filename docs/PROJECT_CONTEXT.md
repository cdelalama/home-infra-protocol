<!-- doc-version: 0.13.6 -->
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

## Current Status (2026-08-22)

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
restart-durable last-valid continuity. At that reconciliation, all projected
evidence was missing and no occurrence was completed. The adopter intentionally
remains pinned to the accepted 0.13.1 contract revision; that patch was
documentation only.

Protocol 0.13.3 repairs the release-integrity defect exposed when ForgeOS
validated the reusable profile against the 0.13.2 checkout: `VERSION` had
advanced while the profile marker remained 0.13.1. The profile marker is now a
first-class version-sync target updated by the official bump script. This
tooling correction changes no contract, adopter pin, authority, or runtime.

Protocol 0.13.4 reconciles the later adopter reality without changing the
contract. Infra Portal 0.27.1 remains the restart-durable dashboard consumer;
Hermes Lab 0.10.3 is now a deployed deterministic consumer with its private
ledger and delivery transport disabled; and Home Infra independently probes
Hermes' machine-readable consumer status. Home Infra 0.18.1 revision
`0a41f54a64c0880bcec8363d7e0af5177381cd48` records the accepted projection
baseline with three series, 34 open occurrences, 34 missing evidence results
and zero completed occurrences. Those result counts are attributed source
evidence, not a permanent protocol invariant. The accepted contract remains
Protocol 0.13.1 at
`2664f49050720daea834fff5ef091c7fd9fff7d9`.

Protocol 0.13.5 repairs the reusable DocKit profile integration without
changing SPEC or schema semantics. Newborn projects use Home Infra's typed
registry and acceptance catalog, project contracts can be implemented through
ForgeOS's contract-only interface skill, and full deliveries remain a separate
explicit workflow. Clean Home Infra sources are validated, committed and
pushed before shared edge apply or Portal synchronization; direct NAS proxy
patching and the legacy Portal sync command are prohibited by regression tests.

Protocol 0.13.6 reconciles completed downstream adoption without changing the
contract. NAS Backup's project-owned evidence implementation is accepted and
deployed, and the first recurring occurrence is verified and completed on
time. Deployed Hermes Lab 0.11.0 migrated its private ledger to schema v2,
seeded the accepted 34-occurrence baseline without inventing historical
events, and retains transition visibility with every proactive transport
  disabled. The last valid accepted projection contains one completed occurrence
  and 33 open occurrences with missing evidence. These are attributed live
  adopter facts, not permanent protocol counts. The 2026-08-22 publisher then
  failed closed as `publisher_head_not_published` after its local Home Infra
  checkout fell behind `origin/main`; the channel became stale and Hermes
  reported `input_stale` while retaining prior state. This is channel failure,
  not authoritative withdrawal or absence of obligations.

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

1. Restore Home Infra publication freshness under the owning project's
   authority, then continue normal monitored operation of the first recurring
   adopter and use
   later evidence changes to exercise Hermes transition history without
   manufacturing completion in Home Infra or a consumer.
2. Evaluate proactive delivery separately from projection consumption
   and keep delivery/acknowledgement distinct from project evidence.
3. Preserve the resolved backup trial as a regression fixture and the current
   recurring chain as the first real multi-frequency adoption record. Portal
   and Hermes are two independent consumer implementations of that one private
   chain, not evidence of universal compatibility.
4. Keep ForgeOS profile revalidation, MCP adoption, recovery and DF-016
   incident lifecycle work behind their separate gates.
5. Sync LLM-DocKit as a dedicated tooling patch after reviewing its
   session-gate and global Codex hook-installation boundary.
6. Keep later status and recovery vocabulary adopter-driven rather than adding
   speculative fields.

## References

- Private implementation: `home-infra`
- First consumer: `infra-portal`
- Scaffold: `LLM-DocKit`
