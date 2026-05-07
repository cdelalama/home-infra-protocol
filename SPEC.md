<!-- doc-version: 0.3.1 -->
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

- `interface`
- `host_id`
- `runtime`
- `image`
- `tags`
- `description`
- `status`
- `deps`
- `runbook`
- `deployment`

#### `interface`

`interface` declares what kind of interface the service exposes so consumers
can render and probe it correctly. The protocol RECOMMENDS the values
`web | api | mqtt | tcp | ssh | none | other`; the schema does not enforce a
closed enum so adopters and consumers can extend the list as new interface
kinds are needed. Future closed-enum candidates start in `other`.

When `interface` is omitted, consumers MUST treat the service as having a web
UI (`interface: web`) for backward compatibility with v0.1.x catalogs. When
the service does not serve HTML at the listed `url`, the service MUST declare
`interface` explicitly so consumers can render and probe it correctly. For
HTTP APIs without HTML (MCP, REST, GraphQL, JSON-RPC), declare
`interface: api`. The earlier formulation of this rule (added in 0.2.0) only
covered URLs whose scheme was not `http(s)://`, which left HTTPS APIs without
HTML on the wrong side of the line and produced the failure mode recorded in
`docs/DOWNSTREAM_FEEDBACK.md` DF-004; the broader formulation above replaced
it in 0.3.1.

| Value | When to use | Consumer behaviour expectation |
|-------|-------------|--------------------------------|
| `web` | Service has a navigable HTML UI | Render an "open" affordance pointing at `url` |
| `api` | HTTP/HTTPS but no HTML UI (REST/GraphQL/MCP/etc.) | Render endpoint info; status probe still applies |
| `mqtt` | MQTT broker | Render a connection-string copy; topology edges to clients |
| `tcp` | Raw TCP service (database, custom protocol) | Render connection info; no clickable open |
| `ssh` | Operator-only SSH endpoint | Render `ssh user@host` copy; no clickable open |
| `none` | Service has no operator interface (background daemon, sync agent) | List the service but offer no interaction |
| `other` | Anything not in the recommended list | Render connection info; specific behaviour undefined |

#### Consumer support for `interface`

This matrix records which catalog-side values which known consumer supports
as of which version. Adopters consult it before designing around a value
that has not yet landed in their consumer of choice. Updating this matrix
when a consumer ships a new capability is part of the consumer's release.

| Consumer | Version | Renders by `interface` | TCP probe | Notes |
|----------|---------|------------------------|-----------|-------|
| infra-portal | 0.8.1 | yes | yes | `web` → open in new tab; `none` → silent no-op; `api`/`mqtt`/`tcp`/`ssh`/`other` → clipboard copy + toast. TCP probe via `node:net` `Socket` connect; missing host or port yields `unknown` rather than crashing the loop. `expect_status` is treated as ground truth when declared (so non-2xx codes like `406` from MCP `/mcp` and `404` by-design endpoints can be marked healthy explicitly — fixed in 0.8.1). Production at 0.8.1 since 2026-05-03. DF-002 closed. |

#### Deployment lifecycle vocabulary

Any infrastructure change passes through six independently-verifiable
states. Sessions (human or LLM) MUST use these names instead of the
overloaded word "deployed":

| State | Meaning | Typical verification |
|-------|---------|----------------------|
| `declared` | The service is in the catalog or in a project contract. | Read the catalog or contract. |
| `implemented` | The source code that delivers the service exists in repo. | `git log` / repo HEAD. |
| `built` | An artefact (image, binary) corresponding to `implemented` has been produced. | Image inspection, build log. |
| `transferred` | The artefact is available on the target host. | `docker images` on the host, file presence. |
| `running` | The process / container is active on the target host. | `docker ps`, `systemctl status`. |
| `serving` | The live endpoint confirms the expected version or capability set. For services without a version-bearing endpoint, the closest equivalent (image tag inspection, file fingerprint) confirms the expected artefact. | `curl /api/health`, container `image:tag` inspection. |

These six states are sequential but not synchronous. A patch can sit at
`implemented` for weeks before reaching `built`; an image can be `built`
on dev-vm before it is `transferred` to NAS; a container can be
`running` with the wrong image, in which case `running` is true and
`serving` is false. Each transition is verifiable independently.

#### Rule: "operationally deployed"

> **"Operationally deployed" can be claimed only when `running` and
> `serving` are confirmed by runtime evidence. For services with a
> version-bearing endpoint, `serving` MUST confirm the expected
> version.**

A `HISTORY.md` entry, ADR, PR description, or DF status that uses the
word "deployed" without naming the verification step that produced the
claim (curl response, image hash, container inspection, etc.) is a
violation of this rule. Validator PASS is necessary, not sufficient: a
validator checks the repo, not the runtime.

#### Rule: intent vs evidence

> **Catalog fields express intent. Evidence about runtime state never
> lives in the catalog. The catalog says "I expect 0.8.0 here";
> evidence is read by a consumer at probe time, never by editing a
> YAML file.**

The architectural division of labour:

- The source-of-truth repo (e.g. `home-infra`) owns intent.
- Consumers (e.g. `infra-portal`, future `infra-agent`) own evidence.
- Telemetry providers (future) measure the world.

Hand-maintained `observed_*` or `actual_*` fields are forbidden — they
rot predictably. If the runtime drifts from the catalog, the correct
response is to redeploy or to change the expectation intentionally,
not to silently lower the catalog to match the runtime.

#### `deployment`

The optional `deployment` block declares the operator's intent
precisely enough for a consumer to compare against the runtime.
Catalog declares intent; the consumer reads evidence. The formal
contract is `schemas/services.schema.json`; the prose contract is
`docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md`.

Shape (every level is optional — a service that omits `deployment`
gracefully falls out of any drift-detection consumer logic):

```yaml
deployment:
  expected:
    image: infra-portal:0.8.0
    health:
      url: https://infra.example.internal/api/health
      version_json_path: $.version
      version: 0.8.0
```

Fields:

- `deployment.expected.image` — image tag (or other artefact reference)
  the operator expects to be running. Omit for services without a
  controllable image (Cloudflare tunnels, third-party SaaS).
- `deployment.expected.health` — sub-block describing how a consumer
  reaches a version-bearing endpoint. Omit for services without one
  (`mosquitto`, `vaultwarden`).
  - `url` — endpoint URL.
  - `version_json_path` — JSONPath into the response that yields the
    version string.
  - `version` — expected value at that JSONPath.

When a consumer compares `deployment.expected` to runtime evidence, it
classifies the result with one of three normative severity names so
multiple consumers share vocabulary:

| Level | Meaning |
|-------|---------|
| `INFO` | No drift, or drift only in patch level under a configurable tolerance. |
| `WARN` | Minor version mismatch; or drift older than a configurable age threshold without an explicit deploy event. |
| `FAIL` | Major version mismatch; or the catalog declares a feature (such as a non-default `interface` or `status.type`) that the deployed binary cannot serve. |

The names are normative. The action each level triggers is **left to
the consumer**: a portal might paint the service red; an agent might
publish to a notification channel; a CI pipeline might gate a release.
The protocol defines vocabulary, not policy.

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
