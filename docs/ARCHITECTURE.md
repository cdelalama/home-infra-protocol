<!-- doc-version: 0.11.0 -->
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

## Data Flow

```text
project repo contracts (future)
        |
        v
source-of-truth repo
  docs + catalogs + decisions
        |
        +--> portal
        +--> MCP server
        +--> canonical validators
        +--> recovery workflow
```

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
