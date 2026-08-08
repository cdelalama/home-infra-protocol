<!-- doc-version: 0.13.1 -->
# Capability Transparency Contract

## Purpose

Capability transparency prevents an intentional restriction from becoming an
invisible product limitation. An operator, agent, or portal must be able to
distinguish:

1. whether a product supports a capability;
2. whether project policy enables it;
3. what scope the policy grants;
4. whether runtime evidence proves that it is available; and
5. what explicit path can change a restriction.

The project contract owns capability intent. A project-owned telemetry
snapshot may publish runtime evidence. Consumers join both inputs, but they do
not author either one.

## Declaration

Projects declare `capabilities[]` in `infra.contract.yml`.

Required fields:

- `id`: stable machine identifier;
- `label`: concise operator-facing name;
- `category`: stable grouping key;
- `support`: `supported | unsupported | unknown`;
- `policy`: `enabled | approval_required | sandbox_only | disabled |
  not_evaluated`;
- `risk`: `low | medium | high | critical`.

Optional fields:

- `scope.mode`: `all | allowlist | sandbox | none`;
- `scope.targets[]`: sanitized, operator-readable target labels;
- `reason_code`: stable machine reason for a restriction;
- `summary`: display-only explanation;
- `enablement`: explicit path for changing the current policy;
- `review_at`: optional UTC review time;
- `observation_job_id`: telemetry job that publishes runtime evidence.

Every policy other than `enabled` requires both `reason_code` and
`enablement`. A permanent boundary remains explicit by using
`enablement.mode: not_planned`; it must not disappear from the declaration.

`enablement.mode` values:

- `automatic`: the project can advance the policy after a deterministic gate;
- `operator_approval`: the operator must explicitly authorize the transition;
- `planned`: the transition is accepted future work but is not yet actionable;
- `not_planned`: no transition is currently intended.

`enablement.runbook`, when present, is a key in the contract's `runbooks` map.
It is not an arbitrary URL or filesystem path.

## Runtime evidence

A declared `telemetry_jobs[]` publisher may add `capabilities[]` to its normal
status snapshot. Each observation contains:

- `id`: exact declaration id;
- `availability`: `available | unavailable | degraded | unknown`;
- `verification`: optional highest evidenced deployment lifecycle state;
- `summary`: optional sanitized display-only explanation.

Runtime evidence must not repeat support, policy, risk, scope, enablement,
review, or restriction reason. Those remain project intent. A validator joins
the snapshot to the declared `observation_job_id`, rejects unknown or duplicate
capabilities, and requires a complete observation set for that job.

Example:

```json
{
  "observed_at": "2030-01-01T12:00:00Z",
  "condition": "ok",
  "severity": "none",
  "summary": "Capability verification completed.",
  "capabilities": [
    {
      "id": "workflows.execute",
      "availability": "available",
      "verification": "serving",
      "summary": "The isolated workflow runner accepted its canary."
    }
  ]
}
```

## Consumer join

Consumers must keep three concepts separate:

| Concept | Authority | Example |
|---|---|---|
| Capability declaration | Project contract | Workflow execution is supported and sandbox-only. |
| Runtime evidence | Project telemetry | The isolated runner is currently serving. |
| Product roadmap | Owning product documentation | Production runner approval is planned later. |

A restriction is not an incident. A consumer may derive attention when:

- policy is `not_evaluated` beyond an adopter-owned review threshold;
- declared `enabled` capability is observed unavailable or unknown;
- an expected observation is missing or stale;
- the declaration and runtime evidence refer to different capability sets.

Consumers must not infer runtime availability from `support: supported`, and
must not infer operator permission from `availability: available`.

## Security and privacy

Capability declarations and observations are operator metadata, not a place
for:

- secret values or credential material;
- raw commands, logs, prompts, messages, or event bodies;
- private identity keys or channel/member identifiers;
- private host paths or implementation exception text;
- unrestricted policy prose that consumers later parse.

Adopters may keep private policy overlays in their source-of-truth repository.
Browser-facing consumers should project an allowlisted subset and use bounded
messages for failures.

## Adoption

This contract is additive. Consumers that do not understand `capabilities`
ignore the field. A project must not claim that a capability is operationally
available until runtime evidence reaches the appropriate deployment lifecycle
state.

Initial protocol publication defines the producer contract and validator.
Consumer support is recorded only after a real consumer ships and passes
positive, negative, stale, and strict-egress tests.
