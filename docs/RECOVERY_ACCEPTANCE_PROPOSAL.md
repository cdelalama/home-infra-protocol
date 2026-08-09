<!-- doc-version: 0.13.3 -->
# Recovery Acceptance Proposal

Status: accepted for protocol implementation design; not yet normative.

## Problem

A restored process is not necessarily a restored service. Two independent
proxied-service recoveries showed that target runtime, integrations, canonical
ingress, operator surfaces, observers, and publication can fail separately.
Declaring recovery complete from one healthy backend can hide a routing,
consumer, or transport-security regression.

## Evidence that survived both cases

The reusable unit is an acceptance surface with:

- stable `id` scoped to the operation;
- `class`: `target`, `integration`, `operator`, `observer`, or `publication`;
- `observation_point`: a neutral description of where evidence is collected;
- `check_kind`: the protocol-level check family, not an executable command;
- `expected`: the bounded result required for acceptance;
- `required`: whether failure blocks completion; and
- an observed result carrying timestamp, outcome, and a sanitized summary.

Addresses, host identities, products, paths, secret references, commands,
backup locations, and operator-specific policy did not survive both cases and
must remain outside a public shape.

## Candidate operation shape

An operation declares an id, operation type, start time, optional maintenance
deadline, acceptance surfaces, and one outcome:

- `complete`: every required surface passed in the same post-change acceptance
  window;
- `incomplete`: at least one required surface failed, was unreadable, or was
  not observed; or
- `rolled_back`: the intended change was reverted and the rollback surfaces
  passed their own acceptance gate.

Consumers must treat missing required observations as incomplete. They must
not infer completion from a producer aggregate, a dashboard state, elapsed
time, or successful execution of a deployment command.

## Security honesty

A security expectation is intent, not proof. Transport encryption and peer
verification are separate expectations. A timestamped observation records
whether each expectation held at the declared observation point. A declaration
alone must never be rendered as verified protection.

## Compatibility

The future contract should be optional and additive. Older consumers may ignore
it. Consumers that render it must preserve unknown surface classes, fail closed
on missing required observations, and identify the evidence owner. Producer
summaries remain display-only.

## Implementation gate

Before touching SPEC, schemas, examples, or validators:

1. choose the owning top-level contract section;
2. define bounded check kinds and observation result vocabulary;
3. add sanitized examples for both recovered-service patterns;
4. test that partial success cannot become `complete`;
5. test that declared security expectations are not treated as observations;
6. define how a consumer exposes incomplete and rolled-back outcomes without
   inventing deployment facts; and
7. obtain explicit maintainer acceptance for an additive minor release.
