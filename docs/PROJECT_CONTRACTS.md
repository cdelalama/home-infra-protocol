<!-- doc-version: 0.10.0 -->
# Project Contracts

Project contracts let individual project repositories describe how they
participate in a larger infrastructure.

They are future upstream inputs to a source-of-truth repo. The source-of-truth
repo remains the authority after ingesting, copying, or validating them.

## Suggested Files

- `infra.contract.yml` for machine-readable metadata.
- `docs/INFRA_CONTRACT.md` for human-readable explanation and runbook links.

## Suggested Fields

- `id`
- `name`
- `repository`
- `services`
- `runtime`
- `deploy`
- `sync_jobs`
- `telemetry_jobs`
- `runbooks`
- `secret_refs`

Secret references name variables and stores only. They never include values.

When a project lists service objects under `services` rather than just ids,
each object's `interface` field follows the same convention as the catalog's
`Service.interface` (see `SPEC.md` *Service*): recommended values
`web | api | mqtt | tcp | ssh | none | other`, optional with default `web`,
required when `url` is not `http(s)://`.

The optional `deployment` block (see `SPEC.md` *Service / `deployment`* and
`schemas/services.schema.json`) carries the same semantics in a project-level
service object as in a catalog entry: `deployment.expected.image` and
`deployment.expected.health` declare the operator's intent for what should be
running, and the intent-vs-evidence rule applies — the project repo declares
intent, consumers read evidence at probe time, and the block is never edited
to match observed reality. A project that does not own the deployment of its
declared services may omit the block entirely.

## Sync And Telemetry Jobs

Project contracts may declare status-producing runtime loops.

Use `sync_jobs[]` when the project synchronizes local state from an external
source of truth. Examples: Gmail archive sync, Telegram archive sync, Plaud
recording sync, forum archive sync. `sync_jobs[]` entries require `source`.

Use `telemetry_jobs[]` when the project observes local runtime or host state.
Examples: host capacity, disk pressure, UPS telemetry, hardware temperature.
`telemetry_jobs[]` entries must not declare `source`.

Both arrays publish the same status snapshot shape at `status_url`. The
snapshot schema is `schemas/status-snapshot.schema.json`.

Freshness is never self-declared inside the snapshot. The producer writes
`observed_at`; the declaration writes `stale_after`; consumers derive freshness
by joining the two.

Schedule rules:

- `cron` and `internal-loop` are periodic. They require `cadence` and
  `stale_after`.
- `webhook` and `manual` are non-periodic. They forbid `cadence`.
  `stale_after` is optional and means silence budget when present.
- Validators should enforce `stale_after > cadence` for periodic jobs.
- `runtime.host_id` is required. `runtime.service_id` is optional because a
  host-level cron may not map to a service record.

Consumer policy:

- Infra Portal may render the latest snapshot and derived freshness.
- Hermes may alert when producer severity is at least `warning` or derived
  freshness is stale.
- Consumers must gate alertability by intent: disabled production services and
  `environment: development` previews are not production incidents.

## Example

See `examples/project/infra.contract.yml`.
