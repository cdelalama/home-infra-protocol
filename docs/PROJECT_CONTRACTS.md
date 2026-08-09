<!-- doc-version: 0.13.3 -->
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
- `capabilities`
- `operational_obligations`
- `runbooks`
- `secret_refs`

Secret references name variables and stores only. They never include values.

The reusable homelab profile installs a TODO-bearing starter contract. A
starter is orientation, not implementation evidence. A real interface is ready
for review only when TODOs are gone, irrelevant examples are removed, each
declared job has a representative sanitized status snapshot, and the canonical
validator passes.

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

## Capability Transparency

Use `capabilities[]` to declare what the project supports, how current policy
constrains it, what scope and risk apply, and how a restriction may evolve.
Capabilities are not jobs and do not represent health.

A capability may reference a `telemetry_jobs[]` entry through
`observation_job_id`. That job's status snapshot then publishes matching
runtime `capabilities[]` evidence. The declaration owns support, policy, scope,
risk, reason, enablement, and review intent. The snapshot owns only observed
availability and verification evidence.

See `docs/CAPABILITY_TRANSPARENCY.md` for the complete declaration, observation,
join, presentation, and security contract.

Freshness is never self-declared inside the snapshot. The producer writes
`observed_at`; the declaration writes `stale_after`; consumers derive freshness
by joining the two.

## Operational Obligations

Use optional `operational_obligations[]` when a project requires a human action
within a dated window and can name the project-owned evidence that proves it.
An obligation is not a job, incident, health check, notification, or command.

Each stable series declares `kind: one_time | recurring`, a responsible role,
plain-language action, runbook key, evidence requirement, and one or more
absolute UTC occurrences. A one-time series has exactly one occurrence. A
recurring series may have multiple materialized occurrences and an optional
horizon, but it never carries calendar or retry grammar.

The source-of-truth repo accepts the declaration and publishes a complete
sanitized projection conforming to
`schemas/operational-obligations-projection.schema.json`. It owns that
projection channel's `generated_at` and `stale_after`; the project continues to
own the action and evidence. Consumers derive future, pending, overdue,
completed, on-time, late, materialization-required, period-ended, and channel
integrity without writing those values back into either source.

Matching `verified` evidence completes an occurrence. `missing` or `failed`
evidence does not. Project resolutions are limited to `cancelled` and
`superseded`; neither is completion. Hermes acknowledgement remains a separate
deployment-private delivery record.

An unreadable projection is never an empty obligation list. Stateful
operational consumers retain the last valid projection with attribution;
stateless clients report channel failure instead of claiming that nothing is
pending. See `SPEC.md` *`operational_obligations[]`* and
`docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md` for the complete rules.

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

## Canonical Validation

The validator belongs to this protocol repository:

```bash
~/src/home-infra-protocol/scripts/validate-project-interface.py \
  --contract /path/to/project/infra.contract.yml \
  --status <job-id>=/path/to/status.json \
  --obligations-projection /path/to/operational-obligations.json \
  --previous-obligations-projection /path/to/previous-operational-obligations.json
```

`--status` is repeatable. Each job id must exist in either `sync_jobs[]` or
`telemetry_jobs[]`. Strict validation:

- rejects unresolved TODO values;
- validates the contract and snapshots against the canonical schemas;
- rejects duplicate job ids and duplicate stable check names;
- rejects duplicate capability declarations or observations;
- rejects duplicate obligation series and occurrence ids;
- validates absolute occurrence windows, horizons, declared runbooks, and
  non-executable action text;
- validates complete sanitized projections and exact project/evidence joins;
- optionally compares the previous accepted projection to reject stable series
  kind changes or occurrence-window mutation under an existing id;
- rejects evidence/resolution authority drift, invalid supersession, and
  verified evidence combined with cancellation or supersession;
- joins capability observations to the declared telemetry job and requires its
  complete declared set;
- rejects runtime evidence that repeats project capability policy;
- enforces `stale_after > cadence` for periodic jobs;
- rejects producer-authored `freshness`, `stale`, or `is_stale`;
- performs no network access and mutates no repository or runtime.

Use `--template` only to validate the canonical profile starter. It verifies
the profile-version marker, the presence of both removable job examples and
one removable capability example, and the deliberate absence of both legacy
private `operational_review` and optional `operational_obligations`. Normative
obligation examples live under `examples/`; the reusable starter does not add
date placeholders to projects that have no operational obligations.

Passing validation proves shape, not runtime truth. Home Infra accepts a
project interface only through its own explicit operator-controlled registry
change with project provenance. ForgeOS and adopters invoke this validator
across the repository boundary; they do not copy it.

## Example

See `examples/project/infra.contract.yml`.
