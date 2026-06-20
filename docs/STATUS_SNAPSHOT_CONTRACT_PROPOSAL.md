<!-- doc-version: 0.6.2 -->
# Status Snapshot Contract Proposal

## Status

Implemented in protocol 0.6.0.

## Problem

Several real adopters publish or need to publish machine-readable runtime
state:

- `msgvault-lab` publishes a sanitized `status.json` for archive, sync, backup,
  and MCP status.
- `forumvault-lab` publishes archive/viewer status and has scheduler freshness
  concerns.
- `plaud-mirror` publishes health and sync state for a mirror of Plaud data.
- `home-infra` host-capacity monitoring needs to publish disk-pressure state.
- Future Telegram archive work will need the same sync-status pattern.

Those producers should not invent incompatible JSON shapes. Infra Portal,
Hermes, future MCP servers, and validators need one small contract they can
read consistently.

## Decision

Define `schemas/status-snapshot.schema.json` as the canonical output shape for
Telemetry Sources.

The snapshot is measurement, not intent. It records what the producer observed
at a point in time. Consumers may display it, store it, derive freshness from
it, or alert on it, but they do not rewrite source-of-truth inventory from it.

## Shape

```json
{
  "observed_at": "2026-06-18T10:30:00Z",
  "condition": "ok",
  "severity": "none",
  "summary": "Gmail archive sync completed cleanly",
  "checks": [
    {
      "name": "account:operator@example.invalid",
      "condition": "ok",
      "severity": "none",
      "summary": "0 errors"
    }
  ]
}
```

Required top-level fields:

- `observed_at`: UTC RFC3339 timestamp ending in `Z`.
- `condition`: producer-emitted aggregate condition, `ok | degraded`.
- `severity`: producer-recommended ordered severity.
- `summary`: display-only human summary.

Optional fields:

- `checks[]`: shaped sub-checks. If present, each check has `name` and
  `condition`; `severity` and `summary` are optional.

## Condition

Top-level producer condition:

| Value | Meaning |
|-------|---------|
| `ok` | The producer observed the job or telemetry source doing its expected work without reportable problems. |
| `degraded` | The producer is still functioning, but it observed a problem the operator should eventually see. |

Producers do not emit top-level `down` or `unknown`. A producer that is down
cannot publish an honest snapshot saying it is down. Consumers derive
`down` or `unknown` from absence, unreadability, or staleness.

Sub-check condition:

| Value | Meaning |
|-------|---------|
| `ok` | This sub-check is healthy. |
| `degraded` | This sub-check still works but has a reportable problem. |
| `down` | This sub-check failed or is unavailable while the aggregate producer remains able to publish. |

This distinction allows a producer to publish aggregate `degraded` while a
specific account, upstream, or subsystem is `down`.

## Severity

`severity` is an ordered producer recommendation:

| Value | Ordinal | Meaning |
|-------|---------|---------|
| `none` | 0 | No operator-visible issue. |
| `info` | 1 | Informational state worth displaying but not alerting. |
| `watch` | 2 | Visible in operator surfaces, not pushed by default. |
| `warning` | 3 | Alertable by default after consumer policy gates. |
| `critical` | 4 | Urgent alertable condition after consumer policy gates. |

The producer proposes severity because it knows local magnitude. For example,
disk 92 percent used may be `critical` even though the producer is still
running and the snapshot is fresh.

Consumers apply policy on top of producer severity: dedupe, suppression,
environment gates, disabled-service gates, and escalation are consumer policy,
not producer authority.

## Freshness

Snapshots do not contain `freshness`.

Reason: if a cron or loop dies after publishing `freshness: fresh`, the stale
file would keep lying forever. The producer writes `observed_at`; the job
declaration writes `stale_after`; the consumer derives freshness by joining
both:

```text
freshness = now - snapshot.observed_at <= declaration.stale_after ? fresh : stale
```

If the snapshot has never been observed, is unreadable, or is stale, the
consumer derives the appropriate display state. The protocol recommends:

- `never_observed`: no usable snapshot has ever been read.
- `stale`: the latest usable snapshot is older than `stale_after`.
- `unknown`: the consumer cannot decide because declaration or time data is
  missing.

Those derived values do not get written back into the snapshot.

Freshness derivation assumes NTP-synchronized hosts and tolerates small clock
skew. If real adopters need an explicit tolerance, a future optional field can
be added to the declaration.

## Summary Is Display-Only

`summary` exists for humans. Consumers MUST NOT parse it for status, severity,
alert routing, entity identity, freshness, or ownership. Machine logic uses
typed fields.

## Consumer Alert Gate

The default alert predicate is:

```text
alertable =
  service_or_job_is_expected_to_run_now
  AND (
    producer_severity >= warning
    OR derived_freshness == stale
  )
```

Known gates:

- A disabled production service is not expected to run.
- `environment: development` is informational and should not page as a
  production incident.
- A dormant development preview may be stale or stopped without being an
  alertable production failure.

Hermes and Infra Portal can use the same snapshot but make different policy
choices: Infra Portal may show `watch`; Hermes may only push `warning` and
above after dedupe.

## Acceptance Criteria

- `schemas/status-snapshot.schema.json` exists and parses as JSON Schema.
- The schema requires `observed_at`, `condition`, `severity`, and `summary`.
- Top-level `condition` is restricted to `ok | degraded`.
- `checks[].condition` permits `ok | degraded | down`.
- `severity` uses the ordered `none | info | watch | warning | critical`
  vocabulary.
- The SPEC and project-contract docs state that freshness is derived by the
  consumer, not self-declared by the producer.
