<!-- doc-version: 0.13.6 -->
# Architecture

## Overview

Home Infra Protocol is a set of contracts, not a monolithic application.

It defines:

- source-of-truth repo responsibilities;
- machine-readable catalog entities;
- project-level contribution contracts;
- consumer responsibilities;
- completion and failure rules for LLM-assisted operations.

## Roles

| Role | Responsibility |
|------|----------------|
| Source-of-truth repo | Owns durable infrastructure intent and current observed state. |
| Project repo | May expose a contract describing how it participates in the infrastructure. |
| Consumer | Renders, validates, searches, or answers questions from source-of-truth data. |
| Telemetry source | Measures runtime state; never becomes source of intent. |
| LLM agent | Reads and updates the source-of-truth repo according to completion rules. |

Producer-owned runtime plans such as `next_run_at` flow through the telemetry
snapshot. Consumers may render them, but cadence remains declaration metadata
and freshness remains a separate consumer derivation.

Project-owned capability declarations flow through the project contract.
Optional availability evidence flows through the referenced telemetry
snapshot. Consumers join both by exact id, but never rewrite policy from
runtime evidence or infer availability from declared support.

The operational-obligations contract applies the same authority discipline to
required human work. A project declares each action and absolute occurrence
window, Home Infra accepts and preserves the intent, the project publishes
evidence, and consumers derive timing with their own clocks. Home Infra owns
the freshness budget for its complete sanitized publication channel. Hermes
delivery and acknowledgement remain deployment evidence, never proof that the
action was completed.

One-time and recurring obligations share the same nested series/occurrence
shape. Projects materialize absolute UTC windows; no consumer interprets a
calendar grammar. Completion derives only from verified project evidence,
while cancellation and supersession remain explicit non-completion decisions.

## Data Flow

```text
project repo contracts
        |
        v
source-of-truth repo
  docs + catalogs + decisions
        |
        +--> portal
        +--> notification agent
        +--> agent capability self-description
        +--> MCP server
        +--> canonical validators
        +--> recovery workflow
```

If the operational-obligations projection becomes stale, invalid, partial, or
unavailable, consumers do not replace it with an empty list. Stateful
operational consumers retain their last valid attributed projection; stateless
clients expose channel failure. Only a fresh, valid, complete projection can
authoritatively withdraw an obligation by omission.

The first private recurring chain now exercises this flow through two distinct
consumers. Infra Portal renders the accepted Home Infra projection and retains
an integrity-checked last valid copy; deployed Hermes Lab 0.11.0 evaluates the
same projection deterministically with a schema-v2 private ledger, evidence-
transition visibility, and transport disabled. The first project-owned
verified result completed its exact occurrence on time; neither consumer nor
Home Infra authored that result.
Home Infra monitors Hermes through its bounded machine-readable status rather
than inferring consumer health from Portal, publisher health, or Docker alone.
That monitor proves consumer health and channel freshness, not declaration or
evidence integrity, and none of these consumers gains project authority.

## Versioning Model

Protocol versions use SemVer.

- Patch: clarification, example fix, non-breaking schema metadata.
- Minor: additive schema fields, new optional contract sections, validator
  capabilities.
- Major: incompatible schema rename/removal or changed authority model.

## Roadmap

### Phase 0 - Draft Spec

- Define principles, roles, and minimal entities.
- Add schemas and examples.
- Document completion and LLM workflow.

### Phase 1 - Validator

- `scripts/validate-project-interface.py` validates project contracts and
  representative status snapshots without network or runtime access.
- ForgeOS and adopters invoke the canonical script across the repo boundary.
- Source-of-truth catalog validation remains separate work.

### Phase 2 - Reference Integrations

- Document how a portal consumes the protocol.
- Document how an MCP server queries the protocol.
- Document how project repos export contracts.

## Validator Ownership

Validation logic lives only in this repository beside the schemas. ForgeOS owns
operator workflow and invokes it. A project repo owns its concrete contract and
status producer and invokes it. Home Infra owns explicit acceptance of the
result. Infra Portal consumes accepted declarations and runtime snapshots.

No higher or lower layer copies the validator. This prevents a new class of
drift where each scaffold or project silently enforces a different protocol
version.

The reusable template marker is checked against `VERSION` whenever the profile
is applied or ForgeOS creates a project. Real contracts use strict validation.
Neither path grants authority to edit Home Infra or to claim a runtime is
healthy.

Capability validation extends the same boundary: the protocol validates shape
and cross-object joins; the project owns declarations and observations; Home
Infra accepts the interface; Portal and Hermes consume a sanitized projection.
