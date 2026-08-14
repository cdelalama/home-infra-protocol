<!-- doc-version: 0.13.4 -->
# Decision Log

Durable decisions for Home Infra Protocol.

## D-001: Use LLM-DocKit As The Scaffold

**Date:** 2026-05-01  
**Status:** Accepted

Create the protocol repository from `LLM-DocKit` so it starts with LLM handoff,
history, decision, versioning, and validation conventions.

## D-002: Keep v0.1 Specification-First

**Date:** 2026-05-01  
**Status:** Accepted

The first release is docs, schemas, and examples only. Runtime services, MCP
servers, agents, and validators are deferred until the vocabulary stabilizes.

## D-003: Treat Consumers As Non-Authoritative

**Date:** 2026-05-01  
**Status:** Accepted

Portals, MCP servers, validators, and telemetry agents consume or measure
protocol data. They must not silently become the source of infrastructure
truth.

## D-004: Separate Check Identity From Operator Copy

**Date:** 2026-07-13
**Status:** Accepted

Status snapshot checks keep required `name` as their stable machine-readable
identity and gain optional `label` for concise operator-facing copy. Producers
should supply a label when the stable name contains implementation syntax or
jargon. `summary` remains display-only plain language; neither label nor
summary may be parsed by consumers.

This preserves backward compatibility and machine joins while preventing a
consumer from either exposing raw identifiers or maintaining project-specific
label maps. A consumer may humanize `name` as a cosmetic fallback only.

## D-005: Keep Planned Execution Separate From Freshness

**Date:** 2026-07-16
**Status:** Accepted

An optional status-snapshot `next_run_at` is authored by the producer scheduler
and may be rendered as an attributed countdown. Consumers must not reconstruct
it from `observed_at + cadence`, because cadence is an interval rather than a
wall-clock schedule. An expired plan never means `due`; only the declaration's
`stale_after` plus snapshot `observed_at` determines freshness.

This restores useful scheduling visibility without making the consumer an
authority over producer execution or creating a second health signal.

## D-006: Keep Project-Interface Validation Canonical And Cross-Repo

**Date:** 2026-07-28
**Status:** Accepted

The executable validator for `infra.contract.yml` and status snapshots lives
only in `home-infra-protocol`, beside the schemas it enforces. ForgeOS,
profile application, and adopter projects invoke that canonical script across
the repository boundary. They do not copy or fork it.

The reusable homelab profile has a protocol-version marker and contains both
removable sync and telemetry examples. Template validation proves that the
starter matches the current protocol; strict validation proves that a concrete
contract and representative snapshots have the required shape. Neither path
proves deployment, runtime health, or Home Infra acceptance.

This converts a passive profile promise into an executable contract while
preserving the five-layer ownership model: protocol owns schemas and
validation; ForgeOS owns workflow; projects own producers; Home Infra owns
accepted intent; consumers derive presentation. At 0.11.0, private incubation
from DF-015, including `operational_review`, remained outside the reusable
profile pending its separate evidence gate. D-008 later implemented the public
contract while preserving the template's deliberate absence by default.

## D-007: Make Capability Restrictions Visible And Evolvable

**Date:** 2026-07-30
**Status:** Accepted for protocol 0.12.0

Project contracts declare operator-visible capabilities separately from
runtime health. Each declaration distinguishes product support, operator
policy, scope, risk, and the explicit path for changing a restriction. Every
non-enabled policy requires a stable reason code and an enablement block;
`not_planned` is an explicit outcome rather than an omitted capability.

Runtime proof remains project-owned telemetry. A capability may name one
telemetry job, whose snapshot carries only typed availability and deployment
lifecycle evidence. Runtime output never repeats or overrides support, policy,
scope, risk, enablement, or review intent.

Consumers join declaration and observation by exact id, render restrictions as
policy rather than incidents, and keep roadmap state separate. This prevents a
temporary safety choice from becoming an invisible product limitation while
preserving the protocol's intent/evidence and non-authoritative-consumer
boundaries.

## D-008: Materialize Operational Obligations As Absolute Occurrences

**Date:** 2026-08-07
**Status:** Accepted for protocol 0.13.0

Projects may declare optional one-time or recurring operational obligations as
stable series containing absolute UTC occurrence windows. The public contract
does not contain cron, RRULE, timezone, month-end, catch-up, retry, or
notification policy. Calendar interpretation stays with the project; every
consumer receives the same materialized timestamps and opaque identities.

Home Infra accepts project intent and publishes a complete sanitized
projection with revision attribution and a freshness budget for its own
publication channel. A stale, invalid, partial, or unavailable projection never
means that no obligations exist. Stateful operational consumers retain the last
valid attributed projection; stateless clients expose channel failure.

Completion derives only from matching project evidence with `result: verified`.
Cancellation and supersession are explicit project decisions that close work
without proving completion. Completed timeliness derives from evidence time,
not the reader's current clock. Hermes delivery and acknowledgement remain a
separate deployment ledger and never complete an occurrence.

Obligation actions are bounded non-executable explanations linked to runbooks.
Operational obligations remain separate from preview expiry, scheduler plans,
capability reviews, status freshness, service health, recovery acceptance, and
incident lifecycle.
