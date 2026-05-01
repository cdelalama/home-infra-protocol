<!-- doc-version: 0.1.4 -->
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

## Example

See `examples/project/infra.contract.yml`.
