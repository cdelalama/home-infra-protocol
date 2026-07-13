<!-- doc-version: 0.9.0 -->
# Authentication Placement Proposal

Status: implemented in protocol 0.8.0. The proposal was accepted separately in
0.7.2 before schema or SPEC changes shipped.

## Problem

Operator-facing services need a provider-neutral way to declare where
authentication is intended to be enforced. Without a shared field, producers
either omit the fact or encode a specific library or identity provider that
portable consumers cannot interpret.

Home Infra 0.3.0 incubated the declaration in its private catalog. Infra Portal
0.15.0 became the first consumer and renders the declaration without claiming
that protection was verified. Home Infra 0.4.0 and Infra Portal 0.16.x then
demonstrated that private policy can coexist with a smaller public declaration:
expectations and waivers stay in the control plane, while strict browser DTOs
expose only the neutral mode plus a consumer-derived assessment.

Evidence anchors at proposal time:

- `home-infra` 0.4.3, commit
  `3f6b6ad78b15d851e5466222b88d1d534cd69c39`: producer declarations,
  ADR-0027/ADR-0028 policy, and catalog validation.
- `infra-portal` 0.16.4, commit
  `481569bee11b3fe298127043926050057f0701a1`: permissive ingestion,
  strict browser egress, neutral rendering, and derived private-policy state.

## Proposed Declaration

Add an optional object below an existing service `exposure` block:

```yaml
exposure:
  authentication:
    mode: application
```

`mode` is required when `authentication` is present and has exactly three
portable values:

- `none`: the service declares no authentication requirement at this surface.
- `application`: authentication is implemented by the application, whether by
  project code or by upstream software shipped with the application.
- `proxy`: authentication is enforced by the ingress or reverse proxy.

The distinction describes placement, not vendor provenance. An upstream
product with built-in login still uses `application`.

## Semantics And Honesty Boundary

This field declares intent. It is not runtime evidence that authentication is
configured correctly, reachable, or effective.

Consumers MAY:

- render the declared placement neutrally;
- compare it with adopter-owned policy supplied through a separate private
  channel;
- surface a contradiction when independent evidence proves the declaration
  false.

Consumers MUST NOT:

- label a service "protected" solely because the mode is `application` or
  `proxy`;
- infer a provider, identity protocol, account policy, or authorization model;
- promote an observation into catalog truth.

## Deliberate Non-Goals

The public protocol does not define:

- authentication providers or libraries such as Better Auth;
- OIDC, forward-auth, credential, signup, or session policy;
- Home Infra `expectation`, `due_by`, or `waiver` metadata;
- consumer-derived `assessment` states or presentation copy;
- negative authentication probes or claims that protection was verified;
- action-plane authorization.

Those concerns have different owners. Home Infra owns private operator policy
and provider selection. ForgeOS may automate stack-aware implementation. Infra
Portal owns strict egress and rendering. A future action broker owns its own
strong authentication and server-side authorization.

## Compatibility

The future implementation is additive:

- `exposure` remains optional;
- `authentication` remains optional;
- existing catalogs remain valid;
- older consumers may ignore the object;
- unknown members inside `authentication` remain adopter extensions and carry
  no protocol semantics unless promoted through a later evidence-backed DF.

## Implementation Hints

Files to touch in the later implementation release:

- `schemas/services.schema.json`: add optional
  `exposure.authentication.mode` with the three-value enum and intent-only
  description; keep additive extension behavior.
- `SPEC.md`: define placement semantics, honesty boundary, and consumer rules.
- `examples/home-infra/catalog/services.yml`: add sanitized `none`,
  `application`, and `proxy` examples without providers or private policy.
- `docs/DOWNSTREAM_FEEDBACK.md`: move DF-011 to implemented and record the
  release.
- `CHANGELOG.md`, orientation docs, and version markers: record the additive
  contract release.

Version bump: minor (`0.8.0`) per `docs/VERSIONING_RULES.md` because this adds
an optional contract section.

Cross-repo touches required: read-only conformance checks against the pinned
producer and consumer evidence. Do not edit Home Infra, Infra Portal, ForgeOS,
or provider configuration from the protocol implementation session.

## Acceptance Criteria For The Later Release

1. Existing examples still validate unchanged.
2. Sanitized examples for all three modes validate.
3. Any other mode is rejected when `authentication` is present.
4. SPEC states explicitly that placement is intent, not proof.
5. The protocol does not acquire expectation, waiver, provider, assessment, or
   action-plane policy.
6. Downstream producer and consumer fixtures remain conformant.
