<!-- doc-version: 0.12.2 -->
# Operational Obligations Proposal

## Status

Proposed after the dated DF-015 evidence review on 2026-08-07. This document
is implementation-neutral and non-normative. It does not add protocol fields,
schemas, examples, validator behavior, consumer support, or compliance claims.
Normative work requires a separate explicit maintainer GO.

## Verdict

Proceed from private incubation to a sanitized proposal. Do not reject the
abstraction, and do not promote it directly into the protocol.

The first bounded backup trial demonstrated a safety-relevant obligation before
runtime telemetry existed, an honest overdue state, and explicit evidence-based
closure. A later private pilot supplies a second real project case and exposes
consumer wording coupled to the first trial. It is not a second independent
consumer stack, so the evidence supports proposal design and validation, not a
normative compatibility claim.

The reusable concept is an **operational obligation**: project-declared intent
that a human action must occur within an absolute time window and that only
project-verifiable evidence can satisfy. It is not service health, an incident,
a scheduler prediction, a notification acknowledgement, or an executable job.

## Evidence reviewed

The public conclusion is based on sanitized observations from the real adopter
chain. Private infrastructure identifiers, paths, addresses, recipients,
providers, and policy are intentionally omitted.

| Question | Sanitized result |
|----------|------------------|
| Visibility before telemetry | The portal showed a pending supervised action before the first producer snapshot without manufacturing runtime health. |
| Explicit phase change | Home Infra advanced the trial only after accepted producer evidence; the consumer did not infer success from time or delivery. |
| Coexistence | Runtime health and the operational review were rendered independently; an attention state did not override healthy telemetry. |
| Deadline and closure | The dated review became genuinely overdue. Closure required an explicit operator decision recorded by the project and removal of the accepted private review; time alone did not close it. |
| Validation | Producer, Home Infra, and Portal suites passed after closure. Invalid private phases, unsafe text, malformed timestamps, and reversed time ordering remained rejected. |
| Stable concepts | Stable identity, responsible role, human action, runbook reference, absolute window, evidence requirement, explicit resolution, and consumer-derived timing survived the trial. |
| Case-specific concepts | Trial phase labels, product decisions, backup policy, preview policy, notification routing, infrastructure coordinates, and commands did not generalize. |
| Second real case | A later private pilot uses the same operational-review path for a different project and longer window. It reveals first-case wording embedded in the consumer, but it is not an independent implementation. |

The original trial is explicitly resolved. Current accepted state no longer
contains its private `operational_review`, while its producer telemetry remains
independent and healthy. The current second case remains active and continues
to provide migration evidence. A development preview can also be expired while
its service remains healthy, confirming the value of a separate lifecycle
rail, but `preview.expires_at` has different ownership and closure semantics.

## Problem statement

A project may require a human action once or repeatedly:

- remain in a trial until a dated decision;
- perform a weekly, monthly, and quarterly verification for six months;
- inspect, rotate, rehearse, approve, or otherwise follow a runbook;
- prove the action through project-owned runtime evidence or a project-owned
  decision record.

The requirement must survive process restarts, agent sessions, dashboards, and
human memory. Infra Portal must be able to present future, next, pending, and
overdue work. Hermes must be able to deliver, deduplicate, repeat, and record
acknowledgement. Neither may claim completion without matching verified
project evidence.

## Authority model

The proposal keeps these authorities separate:

1. **Project declaration authority** defines the policy, required human action,
   runbook reference, absolute occurrence window, and evidence that may close
   the obligation.
2. **Home Infra acceptance authority** accepts and durably preserves that
   intent with source attribution. It does not invent or silently rewrite it.
3. **Project evidence authority** publishes real runtime evidence or a durable
   project decision record for the exact occurrence.
4. **Consumer clock authority** derives future, pending, overdue, or completed
   presentation from accepted intent, accepted evidence, and its own clock.
5. **Hermes delivery authority** delivers, deduplicates, reiterates, and records
   acknowledgements using deployment-private policy.
6. **Acknowledgement is not completion.** A Hermes acknowledgement changes only
   the delivery ledger and never the obligation or its evidence.
7. **Only verified project evidence may prove satisfaction.** Home Infra,
   Portal, Hermes, MCP consumers, and conversational agents cannot manufacture
   completion.

This extends the protocol's existing intent-versus-evidence rule. It does not
transfer project authority to Home Infra or consumer authority to Hermes.

## Recurrence decision

**Recurrence grammar does not belong in the public contract. The project owner
must materialize every occurrence with absolute UTC timestamps.**

The protocol may identify an obligation as `one_time` or `recurring`, but it
must not encode weekly/monthly/quarterly calendar rules, timezone behavior,
daylight-saving transitions, month-end policy, missed-run catch-up, or retry
cadence. Those choices belong to the project and its deployment.

Materialized timestamps have four advantages:

- every consumer reaches the same answer from the same occurrence and clock;
- the project remains the authority for calendar interpretation;
- deadline changes create auditable replacements instead of rewriting history;
- Portal, Hermes, MCP, and simple clients do not need equivalent schedulers.

A recurring project may materialize occurrences ahead of time or publish the
next one when the current occurrence closes. Every occurrence still carries
its own stable identity and absolute window. If a recurring series is within
its horizon, its latest occurrence is terminal, and no successor is available,
consumers surface `materialization_required`; they do not silently assume that
recurrence ended.

## Candidate declaration shape

The smallest reusable project declaration contains the following concepts.
Names and exact nesting remain proposal-level until schema work is authorized.

| Concept | Candidate field | Rule |
|---------|-----------------|------|
| Stable series identity | `id` | Stable within the project across recurring occurrences. |
| Stable occurrence identity | `occurrence_id` | Unique and immutable within the series; used by evidence, delivery, and acknowledgement joins. |
| Occurrence kind | `kind` | `one_time` or `recurring`; this is not recurrence grammar. |
| Responsible role | `responsible` | Sanitized stable role, not a notification destination or secret identity. |
| Human action | `action` | Bounded explanatory text describing what the operator must achieve; no executable command. |
| Runbook reference | `runbook_ref` | Stable key into the project's declared runbooks. |
| Action window | `starts_at`, `due_at` | Absolute UTC timestamps; `starts_at < due_at`. |
| Optional series horizon | `horizon_at` | Last boundary at which the project may materialize a new occurrence; it never closes an already-open occurrence. |
| Evidence contract | `evidence.ref`, `evidence.requirement` | Stable project-owned evidence selector plus bounded text explaining what valid evidence proves. |

An illustrative, non-normative declaration is:

```yaml
operational_obligations:
  - id: restore-readiness-weekly
    occurrence_id: 2026-period-01
    kind: recurring
    responsible: operator
    action: Complete the weekly restore-readiness verification.
    runbook_ref: restore-readiness
    starts_at: "2026-01-05T00:00:00Z"
    due_at: "2026-01-12T00:00:00Z"
    horizon_at: "2026-07-05T00:00:00Z"
    evidence:
      ref: restore-readiness-weekly
      requirement: A verified project result for this exact occurrence.
```

The action explains the desired human outcome and points to a runbook. It must
not contain shell commands, API requests, credentials, or mutation payloads.
Following the runbook or executing any mutation retains its own authorization
gate outside this contract.

## Evidence and resolution

The project evidence projection joins by project, obligation `id`, and
`occurrence_id`. Its minimal reusable concepts are:

- evidence result: `missing`, `verified`, or `failed`;
- evidence `observed_at`, sanitized `ref`, and bounded `summary` when present;
- resolution: `open`, `satisfied`, `cancelled`, or `superseded`;
- `resolved_at` for terminal resolution;
- `replacement_occurrence_id` when resolution is `superseded`.

The following invariants are load-bearing:

- `satisfied` requires matching `verified` evidence for the exact occurrence;
- matching completion evidence and `satisfied` resolution are published
  together; disagreement is invalid rather than a consumer choice;
- `failed` evidence leaves the occurrence open and visible;
- `cancelled` and `superseded` are explicit project resolutions but never mean
  that the action was completed;
- changing a due date does not mutate an accepted occurrence: the project
  supersedes it and publishes a new occurrence identity;
- a decision can satisfy an obligation only when the declared action was to
  make that decision and the project publishes a verifiable decision record;
- absence of the required evidence projection, staleness, parse failure, or
  join failure is `unknown` evidence, never successful evidence. An explicit
  evidence result of `missing` is valid and leaves timing derivation intact.

## Sanitized machine projection

Home Infra should expose an accepted, sanitized projection without requiring
consumers to read private project repositories. The exact envelope remains for
the normative slice, but it must contain:

- projection `generated_at`;
- project id and accepted declaration revision;
- declaration authority and Home Infra `accepted_at` attribution;
- the neutral declaration fields above;
- matching project evidence attribution, evidence result, and resolution;
- enough retained terminal state to detect a missing recurring successor.

It must not contain:

- provider names, recipients, tokens, endpoints, delivery retries, or private
  notification policy;
- private infrastructure addresses, data paths, secret locations, or commands;
- consumer-derived future/pending/overdue state as if it were producer truth;
- Hermes acknowledgement state as if it were project evidence;
- a recurrence expression that consumers must interpret.

Portal, Hermes, MCP, and other consumers derive time state from the accepted
absolute timestamps using their own clocks. `generated_at` and attribution let
them reject stale or ambiguous projections without pretending an obligation
was satisfied.

## Consumer derivation

For each occurrence, a consumer applies this order:

1. Matching `satisfied` plus matching `verified` evidence -> `completed`.
2. `cancelled` or `superseded` -> terminal but not completed.
3. Missing, stale, invalid, or mismatched declaration/projection input ->
   `unknown`. An explicit evidence result of `missing` or `failed` does not
   prevent time-state derivation.
4. `now < starts_at` -> `future`.
5. `starts_at <= now <= due_at` -> `pending`.
6. `now > due_at` -> `overdue`.

`next` is a consumer view, not a producer state: it selects the earliest
unresolved occurrence by window and due time. Overdue occurrences remain in a
separate higher-priority list and must not be hidden merely because a future
occurrence exists. A consumer may use private thresholds to call a pending
item "upcoming", but that wording does not change protocol state.

For a recurring series, consumers also derive:

- `materialization_required` when the horizon remains open, the latest
  occurrence is terminal, and no successor has been accepted;
- `period_ended` only when the horizon has passed, no occurrence remains open,
  and the last materialized occurrence has an explicit terminal resolution.

An open occurrence remains pending or overdue even after `horizon_at`. The
horizon stops creation of later occurrences; it does not waive unfinished
work.

## Hermes delivery and acknowledgement

Hermes consumes the sanitized projection and keeps a deployment-private
delivery ledger. A deterministic delivery key includes project id, obligation
id, occurrence id, and relevant derived-state transition. The deployment owns
providers, destinations, retry and escalation timing, quiet hours, and message
policy.

Hermes may explain the action, current timing, evidence status, and runbook
reference. It may record that the operator saw or acknowledged a message. It
must not:

- mark the occurrence satisfied;
- turn acknowledgement into project evidence;
- infer completion from delivery success or silence;
- embed or execute a command from the obligation;
- mutate the project, Home Infra, Portal, or runtime without a separate
  authorization path.

Repeated notifications join the same occurrence instead of creating new
obligations. A new materialized occurrence receives a new delivery identity.

## Separation from adjacent contracts

- **Service health:** an overdue obligation never changes status-snapshot
  `condition`, `severity`, `observed_at`, freshness, or deployment evidence.
  Portal should render obligations on a separate operational-work rail.
- **`next_run_at`:** remains producer-owned scheduler evidence. It describes a
  machine's planned next execution, not a human obligation or its deadline.
- **`preview.expires_at`:** remains development-runtime lifecycle metadata.
  A consumer may reuse presentation components, but preview expiry must not be
  migrated automatically into a project-declared obligation.
- **Capability `review_at`:** remains a policy-review hint unless the project
  deliberately materializes a separate operational obligation.
- **DF-016 incidents:** detection, notification delivery, acknowledgement,
  recovery, and incident closure remain a distinct lifecycle. An incident may
  create a later obligation, but neither record satisfies the other.

This separation prevents an overdue human action from appearing as a broken
service. A healthy service plus an overdue obligation is a valid and expected
combination. Evidence publication failure is an obligation-evidence problem
unless independent health evidence also reports a service failure.

## Acceptance scenarios

### Future obligation

Given an accepted open occurrence whose `starts_at` is later than the consumer
clock, Portal and Hermes derive `future`. It may be selected as the next future
action, but no consumer claims it is pending or complete.

### Pending and next obligation

Given `starts_at <= now <= due_at`, the occurrence is `pending`. The earliest
unresolved occurrence is eligible for the `next` view. Presentation thresholds
and delivery cadence remain private consumer policy.

### Overdue obligation

Given `now > due_at` and no terminal resolution, every consumer derives
`overdue` from its own clock. Runtime health is unchanged and no incident is
manufactured.

### Acknowledged but not completed

Given an overdue occurrence and a successful Hermes acknowledgement, Hermes
records the acknowledgement against its delivery key. Portal and other
consumers continue to show the occurrence as overdue until matching verified
project evidence produces `satisfied` resolution.

### Completed with evidence

Given matching project evidence with result `verified` and resolution
`satisfied`, consumers derive `completed` regardless of prior delivery or
acknowledgement history. The evidence remains attributed to the project.

### Evidence failure

Given missing, invalid, stale, failed, or mismatched evidence, consumers never
derive `completed`. The occurrence remains future, pending, overdue, or unknown
according to accepted input. A consumer exposes the evidence problem without
changing the service's health state.

### Weekly, monthly, and quarterly work together

The project publishes three stable series, each with independently identified
absolute occurrences and the same optional horizon. Consumers can sort and
deduplicate them without implementing three calendar algorithms. Completing
one frequency has no effect on either of the others.

### End of a six-month period

The project materializes no occurrence starting beyond `horizon_at`. At the
horizon, any open occurrence remains actionable and may become overdue. The
series becomes `period_ended` only after the horizon passes and every
materialized occurrence has an explicit terminal resolution. If the horizon
has not passed and a terminal recurring occurrence has no successor,
`materialization_required` prevents a silent memory gap.

## Compatibility and migration plan

1. **Protocol normative slice:** after explicit acceptance, add an optional
   additive declaration and sanitized projection in a minor release. Existing
   contracts and consumers continue to work unchanged.
2. **Project ownership:** project repositories publish obligation declarations
   and matching evidence. Home Infra explicitly accepts, attributes, and
   preserves them; it does not author project policy on their behalf.
3. **Portal dual read:** Infra Portal reads the new accepted projection while
   temporarily retaining its private `operational_review` adapter. It uses
   generic obligation wording and keeps the health rail separate.
4. **First migration:** migrate the current active private pilot because it is
   live and exposes the legacy consumer coupling. Use the resolved backup trial
   only as a historical regression fixture; do not recreate it as open work.
5. **Recurring adoption:** materialize the real weekly, monthly, and quarterly
   verification program as three project-owned series once that program and
   horizon are approved in its own repository.
6. **Hermes adoption:** add read-only projection consumption, deterministic
   delivery, reiteration, and a private acknowledgement ledger under a separate
   deployment authorization. No execution capability follows from adoption.
7. **ForgeOS adoption:** scaffold and validate declarations through the
   canonical protocol validator. ForgeOS does not copy validation logic or
   automatically execute obligations.
8. **New projects:** use only the protocol declaration after the normative
   release and explicit Home Infra acceptance.
9. **Legacy removal:** remove private `operational_review` only after project,
   Home Infra, Portal, and Hermes acceptance evidence is complete. Keep
   `preview.expires_at`, `next_run_at`, capability reviews, and incidents in
   their existing domains.

## Validation plan for a normative slice

The normative implementation must add positive and negative coverage for:

- optional additive compatibility with existing project contracts;
- stable and unique obligation and occurrence ids;
- strict UTC timestamps and `starts_at < due_at` ordering;
- horizon ordering and the rule that a horizon never closes open work;
- declared runbook references and bounded, non-executable display text;
- exact declaration/evidence joins and authority attribution;
- `satisfied` and verified completion evidence agreeing for the exact
  occurrence;
- failed, stale, missing, and mismatched evidence never completing work;
- supersession requiring a replacement occurrence identity;
- independent consumer-clock derivation at before/start/due/after boundaries;
- missing successor detection for recurring work within its horizon;
- three simultaneous frequency series and six-month horizon completion;
- sanitized strict egress with no provider, recipient, endpoint, credential,
  command, private path, retry, or notification-policy leakage;
- Portal separation of obligation and service-health presentation;
- Hermes deterministic deduplication and acknowledgement non-equivalence;
- old consumers safely ignoring the optional new declaration.

The validation evidence must include one current single-action adopter and one
real recurring multi-frequency adopter before claiming broad consumer support.

## Explicit non-goals

This proposal does not define a scheduler, cron expression, calendar language,
notification provider, recipient model, retry algorithm, executable action,
remote mutation interface, incident workflow, health severity, or private
deployment policy. It does not authorize edits to SPEC, schemas, normative
examples, validators, templates, sibling repositories, or runtimes.

## Promotion gate

The maintainer must explicitly accept this proposal before a normative slice.
That slice should be a single additive minor implementing only the declaration,
sanitized projection, canonical validation, examples, and compatibility tests.
Adopter and runtime changes remain separately authorized follow-up gates.
