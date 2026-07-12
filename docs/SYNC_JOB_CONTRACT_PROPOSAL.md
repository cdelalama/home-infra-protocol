<!-- doc-version: 0.7.1 -->
# Sync Job Contract Proposal

## Status

Implemented in protocol 0.6.0.

## Problem

The ecosystem has two similar-looking but different runtime loops:

1. Source sync loops: a project synchronizes local state from an external
   authority.
2. Telemetry publisher loops: a project observes local infrastructure or
   runtime state and publishes a snapshot.

Examples of source sync:

- Message Vault synchronizes Gmail.
- Future Telegram archive work synchronizes Telegram.
- Plaud Mirror synchronizes Plaud recordings.
- ForumVault synchronizes a forum source.

Examples of telemetry publishing:

- Host capacity monitoring publishes disk-pressure state.
- A future hardware watcher could publish UPS, temperature, or filesystem
  observations.

The protocol should make those loops visible without putting the loop itself
inside Hermes or Infra Portal. The project that owns the data owns the loop.
Consumers read and warn.

## Decision

Extend `schemas/project-contract.schema.json` with two additive arrays:

- `sync_jobs[]`
- `telemetry_jobs[]`

Both declare a scheduled status publisher and publish the same
`schemas/status-snapshot.schema.json` output.

The distinction is enforced:

- `sync_jobs[]` requires `source`.
- `telemetry_jobs[]` rejects `source`.

This keeps the vocabulary honest. A sync job has an external authority it is
trying to catch up with. A telemetry job observes itself or its host and has no
external source of truth.

## Shared Shape

```yaml
schedule:
  mode: internal-loop
  cadence: PT15M
stale_after: PT45M
runtime:
  host_id: nas
  service_id: example-runner
status_url: https://example.internal/status.json
safety:
  idempotent: true
  lock: sqlite
  max_runtime: PT30M
  backoff: exponential
```

Required shared fields:

- `id`: stable slug.
- `schedule`: mode plus cadence where applicable.
- `runtime.host_id`: where the producer runs.
- `status_url`: where consumers read the status snapshot.

Optional shared fields:

- `runtime.service_id`: service/container/daemon identity when there is one.
  Host-level cron jobs may omit it.
- `stale_after`: freshness window. Required for periodic modes; optional for
  non-periodic modes.
- `safety`: idempotence, lock, maximum runtime, and backoff hints.

## Schedule Modes

Periodic modes:

| Mode | Meaning |
|------|---------|
| `cron` | An external scheduler runs the producer periodically. |
| `internal-loop` | The runtime process runs its own periodic loop. |

Rules:

- `cadence` is required.
- `stale_after` is required.
- Validators SHOULD enforce `stale_after > cadence`.
- Validators SHOULD recommend `stale_after >= cadence + max_runtime` when
  `safety.max_runtime` is present.

Non-periodic modes:

| Mode | Meaning |
|------|---------|
| `webhook` | The producer runs after external events arrive. |
| `manual` | The producer runs only when the operator or another workflow invokes it. |

Rules:

- `cadence` is forbidden.
- `stale_after` is optional.
- If `stale_after` is present, it means silence budget: warn if no successful
  event/snapshot has appeared within that duration.
- If `stale_after` is absent, the job never becomes stale by time. Consumers
  may still show the latest snapshot and its observed time.

## Sync Jobs

```yaml
sync_jobs:
  - id: gmail-incremental-sync
    source:
      kind: gmail
      authority: external
    schedule:
      mode: internal-loop
      cadence: PT15M
    stale_after: PT45M
    runtime:
      host_id: nas
      service_id: msgvault-import-runner
    status_url: https://msgvault.example.internal/status.json
    safety:
      idempotent: true
      lock: sqlite
      max_runtime: PT30M
      backoff: exponential
```

`source` is required. The protocol keeps the source shape generic:

- `kind`: provider or source family, such as `gmail`, `telegram`, `plaud`, or
  `forum`.
- `authority`: why this source is authoritative, such as `external`,
  `upstream`, `provider`, or an adopter-defined value.

## Telemetry Jobs

```yaml
telemetry_jobs:
  - id: dev-vm-host-capacity
    schedule:
      mode: cron
      cadence: PT5M
    stale_after: PT15M
    runtime:
      host_id: dev-vm
    status_url: TBD
```

`source` is forbidden. A telemetry job observes local state. Host capacity,
UPS telemetry, or local filesystem pressure are not "behind" an external
source; their stale state means the collector has stopped publishing.

The `status_url` serving path is deployment-specific. For host capacity, the
protocol does not decide whether the snapshot is served by Infra Portal, a
static edge path, a per-host endpoint, or another publisher. The contract only
requires consumers to have a URL to read once the adopter chooses a serving
path.

## Consumer Responsibilities

Consumers join declaration and snapshot:

1. Read `sync_jobs[]` and `telemetry_jobs[]` from the project contract or an
   ingested source-of-truth representation.
2. Fetch `status_url`.
3. Validate the payload against `schemas/status-snapshot.schema.json`.
4. Derive freshness from `observed_at` plus `stale_after` when applicable.
5. Apply consumer policy for display, notification, dedupe, and escalation.

Consumers do not execute the sync. Hermes may alert about a stale Gmail sync,
but Message Vault still owns the Gmail loop. Infra Portal may show host disk
pressure, but the host-capacity producer still owns the measurement.

## Relationship To Upstream Watch

This contract is not the same as upstream-release watch.

- Upstream watch asks: did an external project release something new?
- Source sync asks: is this project's local data current against its source?
- Telemetry publishing asks: did this producer recently observe local state?

Hermes is the natural central owner for upstream watch. Individual projects are
the natural owners for source sync and telemetry publishing. The common protocol
surface is the declaration plus status snapshot.

## Acceptance Criteria

- `schemas/project-contract.schema.json` accepts additive `sync_jobs[]` and
  `telemetry_jobs[]`.
- `sync_jobs[]` requires `source`.
- `telemetry_jobs[]` rejects `source`.
- Periodic schedule modes require `cadence`; non-periodic modes forbid it.
- Periodic jobs require `stale_after`.
- The docs state that validators should enforce `stale_after > cadence` for
  periodic jobs.
- The docs state that `stale_after` on webhook/manual jobs is a silence budget.
- `examples/project/infra.contract.yml` includes sanitized examples of one
  sync job and one telemetry job.
