<!-- doc-version: 0.7.2 -->
# Development Environment Proposal

## Status

Implemented in Home Infra Protocol 0.5.0.

## Motivation

`msgvault-panel` v0.4.0 needed an operator-visible dev-vm preview before its
NAS production deployment existed. The downstream catalog and portal needed to
show that preview without converting a stopped manual process into a production
incident and without claiming that the project was operationally deployed.

The previous stopgap used display text (`DEV - ...`) and a free-form
`development` tag. That made the intent visible to humans, but it left the
protocol unable to validate typos or tell consumers what behavior to apply.

## Contract

Add optional `Service.environment`:

```yaml
environment: development
```

Allowed values:

- `production`
- `development`

Omitted field means `production`. The vocabulary is deliberately closed in the
schema. New values such as `staging`, `preview`, or `experimental` require a
future real adopter and a protocol release.

## Semantics

`environment` is a lifecycle axis, not a service taxonomy:

- `category` still describes the service domain (`data`, `network`, `tools`).
- `interface` still describes how a consumer opens or copies the endpoint.
- `exposure.visibility` still describes who should be able to reach the URL.
- `deployment` still describes production deployment intent and evidence.

For `environment: development`:

- The entry remains private/operator-side.
- The entry is not production deployment evidence.
- The entry does not satisfy the "operationally deployed" rule.
- A stopped preview should be dormant or informational, not a production
  incident.
- A live preview may show healthy status, but only for the preview itself.

## Consumer Behavior

Consumers that render service catalogs should make development entries
explicit. A neutral `DEV` badge, grouping, or equivalent treatment is enough.
The treatment must not imply that the preview is production.

Health consumers should preserve production semantics for omitted or
`production` values. For development entries, failed or unavailable probes
should not create production incidents. The first recorded consumer is
`infra-portal` 0.11.0, which maps unavailable development previews to
`dormant` and excludes them from active incidents.

## Security Boundary

`environment: development` is not a security relaxation. It does not make a
preview public, bypass authentication, or authorize exposing local development
tools to the internet. Profiles may add stricter rules, such as requiring
development previews to use operator-only DNS names or private network access.

## Anti-Rot

Home Infra Protocol 0.7.0 implements the DF-009 follow-up in
`docs/PARALLEL_ENVIRONMENTS_PROPOSAL.md`.

The follow-up does not require every project to have a development runtime. It
adds optional fields for the runtimes that do exist:

- `project_id` to group production and development records for the same
  project;
- `preview.purpose` and `preview.expires_at` to declare why the development
  runtime exists and when it should be renewed or retired;
- `state_policy` to declare whether the runtime has no effects, read-only
  access, isolated development writes, or production-impacting writes;
- `preview_of` as a rare override when pairing cannot be derived from
  `project_id + environment`.

The accepted mechanism explicitly rejects a hand-maintained `last_confirmed`
field. Consumers derive freshness from live probes or status snapshots, while
the catalog declares intent.

## Acceptance Evidence

- `schemas/services.schema.json` declares `environment` as a closed enum.
- `SPEC.md` documents the field, orthogonality, no-evidence rule, and consumer
  support matrix.
- `examples/home-infra/catalog/services.yml` includes a sanitized development
  preview.
- `docs/DOWNSTREAM_FEEDBACK.md` marks DF-008 implemented in 0.5.0.
- `infra-portal` 0.11.0 consumes the field in production.
- `docs/PARALLEL_ENVIRONMENTS_PROPOSAL.md` and protocol 0.7.0 close the
  anti-rot follow-up filed as DF-009.
