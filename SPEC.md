<!-- doc-version: 0.9.0 -->
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
- `environment`
- `project_id`
- `preview`
- `state_policy`
- `exposure`
- `host_id`
- `runtime`
- `image`
- `tags`
- `description`
- `status`
- `deps`
- `runbook`
- `secrets_source`
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

#### `environment`

`environment` declares the lifecycle environment of the service record. The
protocol defines a closed initial vocabulary:

- `production` - the default when the field is omitted. Consumers MUST preserve
  existing production semantics for all v0.1.x-v0.4.x catalogs that do not
  declare the field.
- `development` - an operator-visible, private development preview. It may be
  useful to open from a portal before the project reaches its target production
  host, but it is not production deployment evidence.

Do not add `staging`, `preview`, `experimental`, or other values until a real
adopter needs them. Validators MUST reject unknown `environment` values so a
typo such as `environment: develpoment` cannot pass as a silent convention.

`environment` is orthogonal to the rest of the service taxonomy:

- It does not replace `category`. A data service remains `category: data` even
  when a temporary development preview exists.
- It does not replace `interface`. A development preview can still be `web`,
  `api`, `none`, or another interface kind.
- It does not replace `exposure.visibility`. A development preview can be
  operator-visible while still being non-production.
- It does not replace `deployment`. Production deployment intent and evidence
  remain modeled by the deployment lifecycle vocabulary and the optional
  `deployment` block.

Semantics for `environment: development`:

- A development entry MUST remain inside the operator/private boundary. A
  catalog link to a development preview must not imply public internet
  exposure or relaxed authentication.
- A development entry MUST NOT be used to claim that the project is
  operationally deployed to its production target.
- A stopped development preview SHOULD be rendered as dormant, neutral, or
  informational by consumers rather than as a production incident.
- A live development preview may show healthy runtime status, but that status
  is evidence only for the preview, not for production deployment completion.

#### Parallel runtimes and preview lifecycle

The protocol regulates runtimes that exist. It does not require every project
under active development to keep a development runtime alive. A project can be
actively changed in git and still have only a production runtime in the service
catalog.

When multiple runtimes of the same project exist, the catalog should make that
relationship explicit:

- `project_id` groups service records that represent the same project across
  environments. A production-only service can omit it; if a production runtime
  and a development runtime coexist, both SHOULD declare the same `project_id`.
- `preview_of` is an optional override for rare cases where `project_id +
  environment` is not enough to pair records. It is not required for the common
  case and should not become a second source of truth for normal pairings.
- `preview.purpose` explains why a development runtime exists.
- `preview.expires_at` declares when the preview should be reviewed, renewed,
  or retired. It is an RFC3339 UTC timestamp.
- `state_policy` declares the runtime's side-effect policy:
  `none | read_only | isolated | production_write`.
- `state_policy_justification` may point to the reviewed reason for risky
  policies, especially `production_write` in a development runtime.

Development runtime lifecycle is computed by consumers from catalog intent and
observed status. Catalogs MUST NOT contain hand-maintained `last_confirmed`,
`observed_*`, or `actual_*` fields for preview freshness. They rot for the same
reason runtime evidence rots elsewhere in the protocol.

Suggested consumer signals:

| Signal | Meaning | Typical action |
|--------|---------|----------------|
| `parallel-environments` | Production and development runtimes share a `project_id`. | Group the cards and show both roles. |
| `expired-preview` | `now > preview.expires_at`. | Ask the operator to renew or retire the preview. |
| `stale-data` | The runtime status snapshot or probe is stale. | Warn that the preview may be abandoned. |
| `unbounded-preview` | Development runtime has no `preview.expires_at`. | Soft warning; require intent before the preview ages. |
| `undeclared-effects` | Development runtime lacks `state_policy`. | Warn that side effects are unknown. |
| `production-write-preview` | Development runtime declares `state_policy: production_write`. | Strong warning; require reviewed justification. |
| `secret-overlap-risk` | Development runtime appears to use the same production secret source as its production pair. | Treat as possible production-write risk even if self-declared policy is weaker. |

The side-effect rule is deliberately stricter than the visual grouping rule:

> Development previews may duplicate surfaces, not ownership of production
> state, unless an explicit reviewed exception says otherwise.

`state_policy` is a declaration, not the only evidence. Validators SHOULD
cross-check other fields when possible. For example, if a development runtime
and its production pair share the same secret-store project/config, a validator
may warn about `secret-overlap-risk` even when the development service declares
`state_policy: isolated`.

`shadow` is not a third `environment` value. A shadow runtime observes or
compares production-like state without taking ownership of external effects;
model it with an appropriate `state_policy` (usually `read_only`) and document
its purpose in the service or project contract.

Consumers MAY compare development and production versions when both records
expose comparable versions. Version drift is useful display context, but it is
not the load-bearing lifecycle signal because many previews use moving tags or
local builds.

Schema note: 0.7.0 adds these fields without making old
`environment: development` entries schema-invalid. Validators SHOULD warn on
missing lifecycle/side-effect metadata; future major versions may promote some
warnings into required fields after adopter evidence.

#### `exposure`

`exposure` declares how the service is meant to be reached. It separates the
operator-facing address from implementation details such as a proxy backend.
The service's top-level `url` remains the primary address consumers display,
probe, or copy.

Shape:

```yaml
url: https://service.example.internal/
interface: web
exposure:
  visibility: operator
  canonical: true
  backend_url: http://127.0.0.1:8080
```

Fields:

- `visibility` — one of `operator | local | hidden`.
  - `operator`: `url` is meant to work from a real operator client.
  - `local`: `url` may be loopback, host-local, tunnel-only, or otherwise not
    generally operator-resolvable.
  - `hidden`: consumers may keep the service out of navigation surfaces.
- `canonical` — whether the top-level `url` is the canonical address for this
  service.
- `backend_url` — optional implementation address used by a proxy or runbook.
  Loopback/private backend addresses belong here, not in the operator-facing
  `url`.
- `authentication` — optional provider-neutral declaration of where
  authentication is intended to be enforced. When present, it requires `mode`:
  - `none`: this service surface declares no authentication requirement.
  - `application`: authentication is implemented inside the application,
    including built-in login supplied by upstream software.
  - `proxy`: authentication is enforced by ingress or reverse proxy.

Authentication placement is intent, not runtime evidence. A consumer MAY
render the declared mode neutrally or compare it with separate adopter-owned
policy. A consumer MUST NOT label a service protected solely because the mode
is `application` or `proxy`, infer a provider or authorization model, or write
an observation back into catalog truth.

The public protocol does not define provider selection, credentials, signup or
session policy, expectations, deadlines, waivers, consumer-derived assessment
states, negative authentication probes, or action-plane authorization.
Additional members under `authentication` are adopter extensions and carry no
protocol semantics unless promoted through a later evidence-backed change.

Example:

```yaml
exposure:
  visibility: operator
  canonical: true
  authentication:
    mode: application
```

For `interface: web` with `exposure.visibility: operator`, catalogs SHOULD use
an operator-resolvable hostname in `url`, not a host-local implementation
address. Validators SHOULD flag literal loopback or private IP hosts in that
case (`127.0.0.1`, `localhost`, `0.0.0.0`, RFC1918 literals). Validators SHOULD
apply this rule to the literal `url` host only, not to DNS resolution: a
canonical hostname that resolves to a private LAN IP is valid in a split-horizon
homelab; a literal private IP in the catalog is not.

The protocol deliberately does not name a DNS provider, reverse proxy, or
certificate mechanism. Adopters may layer a local profile on top, such as
"operator web URLs must be `https://*.example.internal/` and route through
edge-caddy".

#### Consumer support for authentication placement

| Consumer | Version | Reads `mode` | Notes |
|----------|---------|--------------|-------|
| infra-portal | 0.16.3 | yes | Renders the declaration as "Auth declared" and uses strict browser egress. Any assessment joined from private adopter policy is consumer output, not protocol truth. |

#### Consumer support for `interface`

This matrix records which catalog-side values which known consumer supports
as of which version. Adopters consult it before designing around a value
that has not yet landed in their consumer of choice. Updating this matrix
when a consumer ships a new capability is part of the consumer's release.

| Consumer | Version | Renders by `interface` | TCP probe | Notes |
|----------|---------|------------------------|-----------|-------|
| infra-portal | 0.8.1 | yes | yes | `web` → open in new tab; `none` → silent no-op; `api`/`mqtt`/`tcp`/`ssh`/`other` → clipboard copy + toast. TCP probe via `node:net` `Socket` connect; missing host or port yields `unknown` rather than crashing the loop. `expect_status` is treated as ground truth when declared (so non-2xx codes like `406` from MCP `/mcp` and `404` by-design endpoints can be marked healthy explicitly — fixed in 0.8.1). Production at 0.8.1 since 2026-05-03. DF-002 closed. |

#### Consumer support for `environment`

This matrix records which known consumers understand `Service.environment`.
Consumers that do not appear here must be treated as ignoring the field.

| Consumer | Version | Reads `environment` | Development health semantics | Notes |
|----------|---------|---------------------|------------------------------|-------|
| infra-portal | 0.11.0 | yes | stopped or failed development previews render as `dormant`, not production `down` | Production health behavior is unchanged. Development services render a neutral DEV treatment, are excluded from active production incidents, and keep the field visible in service details. Production at 0.11.0 since 2026-05-25. DF-008 closed in protocol 0.5.0. |

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
  pattern: upstream-docker
  deviations: []
  expected:
    image: infra-portal:0.8.0
    health:
      url: https://infra.example.internal/api/health
      version_json_path: $.version
      version: 0.8.0
```

Fields:

- `deployment.pattern` — the declared deployment pattern or provenance, such
  as `upstream-docker`, `custom-image`, or an adopter-defined profile.
- `deployment.deviations` — documented intentional deviations from that
  pattern. If a service overrides an upstream entrypoint, changes the upstream
  process model, or splits an upstream single-container topology into multiple
  services, the catalog should record the field changed, reason, date, and
  decision authority. An empty array means no known intentional deviations.
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

#### `secrets_source`

`secrets_source` declares where secret values for a service come from, without
including the values. It operationalizes the principle "Secrets are references
only" for service catalogs and project contracts.

Shape:

```yaml
secrets_source:
  kind: doppler
  project: service-name
  config: prd
  variables:
    - API_TOKEN
```

Only `kind` is universal. `project`, `config`, `path`, and `variables` are
portable reference fields that adopters may interpret for their chosen secret
store. The protocol does not require Doppler, Vault, SOPS, 1Password, or any
other specific product.

If a service has runtime secret material, adopters SHOULD declare
`secrets_source`. A local `.env` file may exist as generated runtime output, but
it should not become an invisible source of truth. Validators MAY warn when a
service description or runbook mentions secret-bearing `.env` files while no
`secrets_source` is declared.

### Project Contract

A project repo can describe how it participates in the infrastructure. These
contracts are upstream inputs to a source-of-truth repo; they are not direct
portal inputs unless the source-of-truth repo chooses to ingest them.

Project contracts may declare project-owned status producers:

- `sync_jobs[]`: loops that synchronize local state from an external source of
  truth. Each sync job requires `source`.
- `telemetry_jobs[]`: loops that observe local runtime or host state. Telemetry
  jobs must not declare `source`.

Both arrays use the same scheduled publisher shape:

- `schedule.mode`: `cron | internal-loop | webhook | manual`.
- `schedule.cadence`: required for `cron` and `internal-loop`, forbidden for
  `webhook` and `manual`.
- `stale_after`: required for periodic modes; optional silence budget for
  `webhook` and `manual`. If omitted for non-periodic jobs, the job does not
  become stale by time.
- `runtime.host_id`: required host where the producer runs.
- `runtime.service_id`: optional service/container/daemon identity.
- `status_url`: URL that serves a status snapshot.
- `safety`: optional idempotence, lock, maximum-runtime, and backoff hints.

For periodic jobs, validators SHOULD enforce `stale_after > cadence`. If
`safety.max_runtime` is present, validators SHOULD recommend
`stale_after >= cadence + max_runtime`.

### Status Snapshot

A status snapshot is the standard machine-readable output of a Telemetry
Source. The formal schema is `schemas/status-snapshot.schema.json`; the prose
contract is `docs/STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md`.

Required fields:

- `observed_at`: UTC RFC3339 timestamp ending in `Z`.
- `condition`: producer-emitted aggregate condition, `ok | degraded`.
- `severity`: producer-recommended ordered severity.
- `summary`: display-only human summary.

Optional `checks[]` split machine identity from presentation:

- `name`: stable machine-readable identifier used for joins and logic.
- `label`: optional concise human-facing label. Producers SHOULD provide it
  when `name` contains implementation syntax, abbreviations, or other text that
  is not suitable as an operator-facing label.
- `summary`: optional plain-language result for the check. It SHOULD describe
  what the operator needs to know and SHOULD NOT expose internal field names or
  `key=value` diagnostics as the primary UI copy.

Consumers MUST use typed fields and `name` for logic. They MAY display `label`
when present and derive a cosmetic fallback from `name` when it is absent. They
MUST NOT parse `label` or `summary`.

`severity` is ordered:

| Value | Ordinal |
|-------|---------|
| `none` | 0 |
| `info` | 1 |
| `watch` | 2 |
| `warning` | 3 |
| `critical` | 4 |

The producer proposes severity; consumers apply policy. A consumer may alert
on `warning` and above, suppress development previews, suppress disabled
services, deduplicate repeated alerts, or escalate persistent failures.

Snapshots do not contain freshness. Freshness is derived by the consumer:

```text
freshness = now - snapshot.observed_at <= declaration.stale_after ? fresh : stale
```

This requires a join between the status snapshot and the job declaration.
`stale_after` belongs in the declaration, not in runtime output.

### Consumer

A tool that reads protocol data. Examples: portal, MCP server, validator, search
index, recovery planner.

### Telemetry Source

A system that measures runtime state, such as health probes or a host stats
agent. Telemetry can be displayed and stored, but it is not an inventory source
unless explicitly promoted through the source-of-truth repo.

Telemetry Sources SHOULD publish status snapshots when their output needs to be
read by consumers such as Infra Portal, Hermes, MCP servers, or validators.

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
