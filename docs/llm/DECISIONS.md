<!-- doc-version: 0.9.2 -->
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
