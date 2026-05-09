<!-- doc-version: 0.4.0 -->
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

## Example

See `examples/project/infra.contract.yml`.
