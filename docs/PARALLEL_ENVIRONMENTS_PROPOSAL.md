<!-- doc-version: 0.7.1 -->
# Parallel Environments and Side-Effect Ownership Proposal

## Status

Implemented in Home Infra Protocol 0.7.0.

## Motivation

`Service.environment` solved the first development-preview problem: a consumer
can distinguish a private development preview from production and avoid turning
a stopped preview into a production incident.

Real adopters then exposed the next problem. A project can have a production
runtime and a development runtime alive at the same time. That can be harmless
when the development runtime is only a temporary UI/API surface, but dangerous
when it also owns production state through schedulers, backups, imports, syncs,
or writes using production credentials.

The protocol must model the runtime that exists. It must not require every
project under active development to keep a development runtime alive.

## Guiding Rule

Development runtimes are optional. When present, they must be intentional,
temporary, grouped with production when applicable, and explicit about side
effects.

Short form:

> Development previews may duplicate surfaces, not ownership of production
> state, unless an explicit reviewed exception says otherwise.

## Contract

The extension is additive to `Service`.

### `project_id`

`project_id` groups multiple service records that represent the same project
across environments.

Rules:

- A production-only project does not need `project_id`; its `id` is enough.
- When two or more runtimes of the same project exist, all related records
  SHOULD declare the same `project_id`.
- Consumers derive default pairing from `project_id + environment`.
- `preview_of` exists only as an override for rare cross-project or multi-prod
  cases. It is not mandatory.

### `preview`

`preview` declares human intent for a development runtime.

Shape:

```yaml
environment: development
preview:
  purpose: Validate redesigned settings UI before the next production release.
  expires_at: "2026-07-15T00:00:00Z"
```

Rules:

- Development runtimes SHOULD declare `preview.purpose` and
  `preview.expires_at`.
- `expires_at` is a static intent timestamp in RFC3339 UTC.
- Consumers compute lifecycle verdicts from `expires_at` and live status
  freshness. Do not add hand-edited `last_confirmed` fields.
- A missing `preview.expires_at` is an unbounded-preview warning, not proof of
  failure.

### `state_policy`

`state_policy` declares whether the runtime may affect state outside itself.

Recommended values:

| Value | Meaning |
|-------|---------|
| `none` | No state effects. Static/demo surface or inert process. |
| `read_only` | May read external or production state; does not write. |
| `isolated` | May write only to isolated development state. |
| `production_write` | May write production state or run production-impacting jobs. |

Rules:

- Development runtimes SHOULD declare `state_policy`.
- Missing `state_policy` on a development runtime is a warning: effects are
  not declared.
- `production_write` on a development runtime is a strong warning and requires
  explicit reviewed justification, such as `state_policy_justification` or an
  adopter ADR/runbook reference.
- `state_policy` is a declaration, not the only evidence. Validators SHOULD
  cross-check other fields, such as `secrets_source`, where possible.

## Consumer Semantics

Consumers compute lifecycle and risk; catalogs declare intent.

Suggested lifecycle signals:

- `expired`: `now > preview.expires_at`.
- `stale-data`: the runtime's status snapshot or probe is stale.
- `unbounded-preview`: development runtime without `preview.expires_at`.

Suggested side-effect signals:

- `undeclared-effects`: development runtime without `state_policy`.
- `production-write-preview`: development runtime with
  `state_policy: production_write`.
- `secret-overlap-risk`: development runtime appears to use the same
  production secret source as its production pair.

Strong health colors should remain reserved for real runtime health. Parallel
environment relationships and preview lifecycle should render through grouping,
badges, or soft warning treatment.

## Shadow Runtimes

A shadow runtime observes production-like state without taking ownership. It
may read, publish telemetry, and compare outputs, but it does not run external
side effects.

Do not add `shadow` as a third `environment` value in this release. Model a
shadow runtime as a runtime with an appropriate `state_policy` (usually
`read_only`) and document its purpose in the project contract or service
description.

## Version Comparison

Consumers MAY show that a development runtime is behind production when both
records expose comparable versions. Version comparison is not the load-bearing
anti-rot signal because many previews use moving tags or local builds.

The mandatory anti-rot signals are preview lifecycle and status freshness.

## Validation Guidance

Because `Service.environment` was already valid in 0.5.x and 0.6.x, the 0.7.0
schema adds fields but does not make existing development entries invalid.

Profile validators SHOULD warn when:

- a development runtime lacks `preview.expires_at`;
- a development runtime lacks `preview.purpose`;
- a development runtime lacks `state_policy`;
- a development runtime uses `state_policy: production_write` without
  justification;
- production and development records look like the same project but cannot be
  paired because `project_id` is missing;
- a development runtime appears to share the production `secrets_source`.

Future major versions may promote some warnings into schema-enforced
requirements if adopter evidence shows that is worth the migration cost.

## Acceptance Evidence

- `schemas/services.schema.json` adds optional `project_id`, `preview`,
  `preview_of`, `state_policy`, and `state_policy_justification`.
- `SPEC.md` documents the runtime-only scope, pairing rule, lifecycle signals,
  and side-effect ownership policy.
- `examples/home-infra/catalog/services.yml` includes a sanitized production
  service plus a development runtime using the new fields.
- `docs/DOWNSTREAM_FEEDBACK.md` marks DF-009 implemented in 0.7.0.
