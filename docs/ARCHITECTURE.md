<!-- doc-version: 0.1.0 -->
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
        +--> validators
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

- CLI validates source-of-truth catalogs and project contracts.
- Examples run in CI.

### Phase 2 - Reference Integrations

- Document how a portal consumes the protocol.
- Document how an MCP server queries the protocol.
- Document how project repos export contracts.
