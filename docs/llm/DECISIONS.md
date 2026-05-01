<!-- doc-version: 0.1.4 -->
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
