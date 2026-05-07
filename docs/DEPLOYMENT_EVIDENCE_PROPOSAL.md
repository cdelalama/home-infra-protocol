<!-- doc-version: 0.3.1 -->
# Proposal: Deployment Evidence Contract

> Status: **Draft — Ready for Implementation**
> Date: 2026-05-03
> Authors: Claude Opus 4.7 (proposer) + GPT-5 (critic) + Carlos (arbiter), via the
>          Consensus Protocol described in
>          `~/src/LLM-DocKit/docs/CONSENSUS_PROTOCOL_PROPOSAL.md`
> Triggers: `docs/DOWNSTREAM_FEEDBACK.md` DF-003 (this repo) +
>           `~/src/LLM-DocKit/docs/DOWNSTREAM_FEEDBACK.md` DF-029
> Implementer: a future session — this proposal is intentionally
>              self-contained so the next agent can read, decide, and ship
>              without needing the deliberation that produced it. The
>              causal trail is in `docs/llm/REVIEWS.md`.

---

## Problem statement

`home-infra-protocol` defines what services *should* exist (catalog), what
fields they *should* declare (schema), and what consumers *should* support
(SPEC). It says nothing about whether those declarations match what is
actually running.

This gap is not theoretical. On 2026-05-02 the protocol shipped
`Service.interface` in 0.2.0, the consumer (`infra-portal`) implemented
the rendering and TCP probe in repo at 0.8.0, the catalog
(`home-infra/catalog/services.yml`) declared `interface: web` /
`interface: mqtt` on three services. From the protocol's vantage,
"consumer support is implemented." From the operator's vantage, the
deployed portal at `https://infra.lamanoriega.com/api/health` returned
`{"version":"0.7.2"}`, did not read the new field, and Mosquitto stayed
in `state: unknown` because the deployed binary did not have the TCP
probe code. Both vantages were simultaneously true. The protocol had no
vocabulary to distinguish them.

DF-002 ("schema accepts X, consumer doesn't implement X") and DF-029
("repo VERSION advances but the deployment lags invisibly") name the
same modal failure at different layers. This proposal addresses the
underlying cause: the protocol conflates intent with evidence.

## Decision

Adopt three additions to `home-infra-protocol`:

1. **A typed vocabulary of six lifecycle states** that any infrastructure
   change passes through. Replaces the overloaded word "deployed".
2. **A normative rule separating intent from evidence.** Catalog declares
   intent. Evidence is read from the runtime, never edited into the
   catalog by hand.
3. **An optional `deployment` block on `Service`** that declares the
   intent precisely enough for a consumer to compare against runtime.
   Schema stays additive (`additionalProperties: true`).

No enforcement is added in this proposal. Consumers (the portal first,
the future `infra-agent` next) implement detection and surface the
result; this proposal defines the contract they consume.

### The six lifecycle states

```
declared    — the service is in the catalog or in a project contract.
implemented — the source code that delivers the service exists in repo.
built       — an artefact (image, binary) corresponding to `implemented`
              has been produced.
transferred — the artefact is available on the target host.
running     — the process / container is active on the target host.
serving     — the live endpoint confirms the expected version or
              capability set; for services without a version-bearing
              endpoint, the closest equivalent (image tag inspection,
              file fingerprint) confirms the expected artefact.
```

These six states are sequential but not synchronous. A patch can sit at
`implemented` for weeks before reaching `built`; an image can be `built`
on dev-vm before it is `transferred` to NAS; a container can be
`running` with the wrong image, in which case `running` is true and
`serving` is false. Each transition is verifiable independently.

### Normative rule on "operationally deployed"

> **"Operationally deployed" can be claimed only when `running` and
> `serving` are confirmed by runtime evidence. For services with a
> version-bearing endpoint, `serving` MUST confirm the expected
> version.**

Sessions (human or LLM) MUST NOT use the word "deployed" without
naming which of the six states they have evidence for. A `HISTORY.md`
entry that says "deployed v0.8.0" without a curl output, image hash, or
equivalent evidence is a violation of this rule. Linting this is out of
scope for the protocol; LLM-DocKit's own template can adopt a check.

### Normative rule on intent vs evidence

> **Catalog fields express intent. Evidence about runtime state never
> lives in the catalog. The catalog says "I expect 0.8.0 here";
> evidence is read by a consumer at probe time, never by editing a
> YAML file.**

This rule prevents the predictable rot of any `observed_*` field
maintained by hand. It also draws a clear architectural line: the
source-of-truth repo (`home-infra`) owns intent; consumers (`infra-portal`,
future `infra-agent`) own evidence; telemetry providers (future) measure
the world. This division of labour was already implicit in
`SPEC.md` *Required Behaviors* but not until now stated explicitly with
respect to deployment.

### Field shape

Add an optional top-level `deployment` block to `Service`:

```yaml
- id: infra-portal
  name: Infra Portal
  category: infra
  url: https://infra.lamanoriega.com/
  interface: web
  # ...
  deployment:
    expected:
      image: infra-portal:0.8.0
      health:
        url: https://infra.lamanoriega.com/api/health
        version_json_path: $.version
        version: 0.8.0
```

- `deployment.expected.image` — image tag the operator expects to be
  running. String. Optional. Omit for services without a controllable
  image (Cloudflare tunnels, third-party SaaS).
- `deployment.expected.health` — sub-block describing how a consumer
  reaches a version-bearing endpoint. Omit for services without one
  (`mosquitto`, `vaultwarden`).
  - `url` — endpoint URL.
  - `version_json_path` — JSONPath into the response that yields the
    version string.
  - `version` — expected value at that JSONPath.

The block is optional at every level. A service that omits it
gracefully falls out of any `deployment-evidence` consumer logic.

This is the recommended shape; the implementing session may adjust the
naming if validation against real catalogs surfaces an issue, but MUST
NOT replace the bloque-anidado approach with flat fields. Flat fields
were considered and rejected because they conflate independent facts
(image tag, app version, endpoint coordinates) into a single namespace
where every service ends up either over- or under-specified. See
`docs/llm/REVIEWS.md` 2026-05-03 for the deliberation that produced
this choice.

### Drift severity (semantic, not enforcement)

When a consumer compares `deployment.expected` to runtime evidence, it
classifies the result as one of:

```
INFO   — no drift, or drift only in patch level under a configurable
         tolerance.
WARN   — minor version mismatch; or drift older than a configurable
         age threshold without an explicit deploy event.
FAIL   — major version mismatch; or the catalog declares a feature
         (such as a non-default interface or status type) that the
         deployed binary cannot serve.
```

These names are normative for inter-consumer compatibility (so
`infra-portal` and a future `infra-agent` use the same vocabulary) but
the action each level triggers is **left to the consumer**. The portal
might paint the service red; the agent might publish to a Telegram
channel; a CI pipeline might gate a release. This proposal does not
prescribe which.

`FAIL` on a feature mismatch (DF-002 territory) is the tightest case
the protocol can detect today. It requires the catalog to declare what
feature it expects (e.g. `interface: mqtt`) and the consumer to report
which features it implements; both already exist in 0.2.0. Wiring the
comparison is a small consumer-side change, not a protocol change.

### Anti-patterns explicitly prohibited

The following patterns are violations of this contract and MUST be
flagged in any review:

1. **Editing the catalog to match observed reality.** If the catalog
   says `expected.image: 0.8.0` and the runtime is at `0.7.2`, the
   correct response is to redeploy or to change the expectation
   intentionally — not to silently lower the catalog to `0.7.2`. The
   point of the catalog is to express what we *want*; making it match
   reality erases the drift signal.
2. **Declaring "deployed" without serving evidence.** No HISTORY entry,
   ADR, or PR description may use the word "deployed" without naming
   the verification step that produced the claim (curl response, image
   hash, container inspection, etc.).
3. **Trusting validator PASS as proof of deployment.** The
   `dockit-validate-session.sh` family checks the repo. It cannot
   reach outside the repo to verify the runtime. PASS is necessary,
   not sufficient.
4. **Adding any `observed_*` or `actual_*` field maintained by hand.**
   Hand-maintained observation fields rot predictably (DF-021/-022
   territory in LLM-DocKit). Evidence is read fresh by a consumer or
   it is not trusted.
5. **Promoting a single-version field (`expected_image_tag` alone, or
   `expected_version` alone) instead of the `deployment` block.**
   Singletons cannot represent the full set of facts (image, app
   version, endpoint coordinates, JSON path) coherently.

## Concrete scenarios — how the contract behaves on the homelab

The proposal is validated by walking five real cases from the current
catalog. The implementing session MUST verify the proposal handles all
five before claiming completion.

| Scenario | Service | What `deployment` declares | What evidence comes from | Likely drift class |
|---|---|---|---|---|
| Own app + endpoint | `infra-portal` | `expected.image: infra-portal:0.8.0` + `expected.health.version: 0.8.0` | image inspection + `/api/health` | image tag drift, version drift |
| Own image, no version endpoint | `tomatic-bridge` (planned, H1) | `expected.image: tomatic-bridge:vX.Y.Z` | image inspection only | image tag drift |
| Third-party with HTTP UI | `esphome-builder` | `expected.image: ghcr.io/esphome/esphome:latest` | image digest inspection (tag is `latest`); HTTP `/` reachability | digest drift over time |
| Third-party, TCP only | `mosquitto` | `expected.image: eclipse-mosquitto:2.0` | image inspection + TCP probe (presence) | image tag drift |
| External SaaS / tunnel | Cloudflare tunnel, future SaaS | `deployment` omitted entirely | not measured | n/a — opt-out documented |

Each row corresponds to a catalog entry that exists today (or is named
in a project contract). The contract handles all five without forcing
asymmetric simplifications.

## Cross-protocol relationship

This proposal has a sibling proposal in LLM-DocKit
(`~/src/LLM-DocKit/docs/CONSENSUS_PROTOCOL_PROPOSAL.md`) that defines
the deliberation mechanism by which both proposals were produced. The
two proposals are independent at the implementation layer but share
provenance: the same audit trail in `docs/llm/REVIEWS.md` of both
repos records the deliberation that produced both.

LLM-DocKit may, in a follow-up patch, ship an optional
`--check deployed-version` validator check that any project can opt
into via `.dockit-config.yml`. That check is a *consumer* of this
contract; it is not part of this proposal. Conversely, this contract
is independent of LLM-DocKit — a project that does not use the
DocKit scaffold can still adopt the `deployment` block in its own
catalog.

`infra-portal` is a separate consumer. It already implements the
plumbing in repo at 0.8.0; the next portal patch can read
`deployment.expected.health` and report drift in the existing service
card UI. No protocol change is needed for that work.

A future `infra-agent` (planned, listed in this repo's README
"Ecosystem map" as not-yet-created) is the consumer of last resort:
the daemon that compares declared expectations against the runtime
on a schedule and writes findings somewhere readable (SQLite, a
Telegram channel, a portal endpoint).

## Acceptance criteria

The implementing session has shipped this proposal when ALL of the
following are true:

- [ ] `schemas/services.schema.json` adds the `deployment` block on
      each service item (additive, optional, `additionalProperties:
      true` preserved).
- [ ] `SPEC.md` *Service* section gains:
      - the six-state vocabulary as a normative subsection;
      - the "operationally deployed" rule;
      - the intent-vs-evidence rule;
      - a brief description of the `deployment` block, pointing at
        the JSON schema for the formal contract.
- [ ] `examples/home-infra/catalog/services.yml` shows three of the
      five scenarios above on sanitized hostnames.
- [ ] `docs/PROJECT_CONTRACTS.md` notes that project-level service
      objects, when used, may include the same `deployment` block
      with the same semantics.
- [ ] `docs/DOWNSTREAM_FEEDBACK.md` DF-003 status moves from `open`
      (or whatever it is at implementation time) to `implemented
      (X.Y.0)`. DF-002 stays `partially implemented` until a
      consumer ships the actual probing.
- [ ] `CHANGELOG.md` documents the change as a minor bump (additive
      schema field).
- [ ] `scripts/bump-version.sh` synced; `scripts/check-version-sync.sh`
      passes.

## Migration path

`home-infra/catalog/services.yml` (the only in-tree real adopter)
needs no immediate change. Existing entries without a `deployment`
block continue to validate against the new schema and consumers fall
back to today's behaviour (no drift detection for those services).

The first deliberate use of the new block is planned for `infra-portal`
itself in a follow-up commit on `home-infra`: declare
`deployment.expected.image` and `deployment.expected.health` so the
portal can report its own drift against itself. That self-test is the
cheapest way to validate the contract end-to-end before extending to
other services.

## Out of scope (intentionally)

- **Enforcement actions** (which drift level blocks what) belong to
  consumers, not the protocol. A consumer may ship a strict mode that
  refuses to render a service in `FAIL`; another consumer may stay
  in info-only mode. The contract defines vocabulary, not policy.
- **The TCP probe in `infra-portal`** that closes DF-002 lives in the
  portal repo. This proposal references it but does not implement it.
- **`infra-agent`** as a project. This proposal makes the agent's
  future job easier (well-defined contract, scenarios documented, no
  schema invention required) but does not create the project.
- **A check in LLM-DocKit** (`--check deployed-version`) is the
  natural follow-up but lives in that protocol's proposal, not this
  one.

## Future consumer / precedent (ForgeOS)

ForgeOS — the operator's planned system for agentic management of
real infrastructure — is expected to inherit this contract as one of
its primitives. The six-state vocabulary, the intent/evidence
separation, and the `deployment` block shape are candidates for
ForgeOS's deployment subsystem.

This is mentioned as **precedent**, not as **requirement**. The
proposal must stand on its own as useful for the current homelab; if
ForgeOS later picks up the pattern, that is a downstream consequence,
not a constraint on this design. Sessions implementing this proposal
SHOULD NOT add fields or rules motivated only by ForgeOS speculation
— that is a known anti-pattern of premature generalisation. The rule
is: solve the homelab first, let ForgeOS ratify.

## How to use this proposal in a fresh session

A future session that has not seen the deliberation that produced this
document can ship the proposal by reading, in order:

1. This file end to end.
2. `docs/DOWNSTREAM_FEEDBACK.md` DF-002 and DF-003 for context.
3. `docs/SERVICE_INTERFACE_PROPOSAL.md` as the structural template that
   inspired the present proposal (same shape).
4. `docs/llm/REVIEWS.md` entry dated 2026-05-03 for the causal trail
   if any decision below seems arbitrary.
5. Then execute the Acceptance criteria checklist above.

If anything is unclear, the session SHOULD pause and ask — per the
protocol's existing "if unsure, ask" rule.
