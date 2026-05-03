<!-- doc-version: 0.2.5 -->
# Security Model

Home Infra Protocol assumes catalogs may be consumed by internal tools and LLM
agents. Treat them as sensitive operational metadata even when they contain no
secret values.

## Rules

- Do not put secret values in catalogs, examples, or project contracts.
- Use secret references: variable names, project names, secret store names.
- Public examples must be sanitized.
- Consumers must not infer authority to mutate infrastructure from read access.
- Telemetry endpoints are not automatically trusted sources of inventory.

## Exposure

If a consumer exposes catalog data over HTTP, anything in the catalog should be
safe for that audience. LAN-only is not the same as public, but it is still
unauthenticated in many homelab deployments.
