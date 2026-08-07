<!-- doc-version: 0.13.0 -->
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
- Capability declarations and observations must not contain secret values,
  private identity material, message bodies, raw commands, raw exception text,
  or hidden policy detail.
- Runtime capability observations must not restate declaration policy.
  Browser-facing consumers should expose only a strict allowlisted projection.
- Operational-obligation actions are bounded explanatory text, never commands,
  requests, credentials, endpoints, or mutation payloads. Runbook execution
  keeps its own authorization gate.
- Accepted obligation projections use strict allowlisted egress. They exclude
  provider, recipient, token, endpoint, retry, private path, notification
  policy, and acknowledgement detail.
- An invalid, stale, partial, or unavailable obligation channel must not be
  converted into an empty list. Stateful operational consumers retain and
  attribute their last valid projection; stateless clients expose channel
  failure rather than manufacturing absence.

## Exposure

If a consumer exposes catalog data over HTTP, anything in the catalog should be
safe for that audience. LAN-only is not the same as public, but it is still
unauthenticated in many homelab deployments.
