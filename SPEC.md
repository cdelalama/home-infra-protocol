<!-- doc-version: 0.1.6 -->
# Home Infra Protocol Specification

> Status: Draft v0.1

## Purpose

Home Infra Protocol defines how a small infrastructure records durable truth so
humans, LLM agents, portals, MCP servers, and recovery workflows can read the
same current state.

The protocol is optimized for Git-based source-of-truth repositories maintained
by a human operator with LLM assistance.

## Principles

1. **Source of truth is explicit.** One repo owns inventory and intent.
2. **Markdown and catalogs coexist.** Markdown explains context; structured YAML
   gives tools a stable contract.
3. **Consumers do not author truth.** Portals and MCP servers read and warn; they
   do not silently rewrite canonical inventory.
4. **Telemetry is measurement, not intent.** Runtime status can reveal drift but
   does not replace documented state.
5. **Completion is auditable.** An infrastructure change is incomplete until the
   source-of-truth repo and relevant consumers agree.
6. **Schema evolution is additive by default.** Removing or renaming fields
   requires a coordinated release.
7. **Secrets are references only.** Catalogs may name secret stores and variable
   names, never secret values.

## Governance

Field policy, ownership boundaries, project bootstrap rules, and compliance
claim rules live in `docs/GOVERNANCE.md`.

## Core Entities

### Host

A physical machine, VM, appliance, or logical runtime location that can host
services.

Minimum fields:

- `id`
- `name`
- `role`
- `ip` or another address reference

### Service

A user-visible or operator-visible capability. Internal implementation
components can be modeled later, but the minimal catalog focuses on services a
human or agent may need to find, open, verify, or reason about.

Minimum fields:

- `id`
- `name`
- `category`
- `url`

Recommended fields:

- `host_id`
- `runtime`
- `image`
- `tags`
- `description`
- `status`
- `deps`
- `runbook`

### Project Contract

A project repo can describe how it participates in the infrastructure. These
contracts are upstream inputs to a source-of-truth repo; they are not direct
portal inputs unless the source-of-truth repo chooses to ingest them.

### Consumer

A tool that reads protocol data. Examples: portal, MCP server, validator, search
index, recovery planner.

### Telemetry Source

A system that measures runtime state, such as health probes or a host stats
agent. Telemetry can be displayed and stored, but it is not an inventory source
unless explicitly promoted through the source-of-truth repo.

## Required Behaviors

- A consumer must tolerate unknown fields.
- A consumer must fail loudly when no valid catalog is available on boot.
- A consumer may keep the last valid catalog when a later reload is invalid.
- A source-of-truth repo must document when generated or copied data is not
  authoritative.
- A project contract must not contain secret values.

## Completion Rule

See `docs/COMPLETION_RULE.md`.

## Security Model

See `docs/SECURITY_MODEL.md`.
