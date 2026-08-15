<!-- doc-version: 0.13.5 -->
# Operational Obligations Proposal

## Status

Implemented in Home Infra Protocol 0.13.0 after explicit maintainer acceptance
on 2026-08-07, with canonical ordering clarified in protocol 0.13.1. This
document preserves the evidence and design rationale; the normative contract
now lives in `SPEC.md`,
`schemas/project-contract.schema.json`, and
`schemas/operational-obligations-projection.schema.json`.

The separately authorized first recurring adoption now has two deployed
consumers. NAS Backup declares three recovery series and 34 absolute
occurrences, Home Infra accepts and continuously publishes their complete
sanitized projection, Infra Portal consumes it with restart-durable last-valid
continuity, and Hermes Lab 0.10.3 consumes it deterministically with a private
ledger while delivery transport remains disabled. Home Infra independently
monitors the Hermes status contract. ForgeOS, MCP, project evidence deployment
and notification transport remain separately authorized gates.

## Verdict

The abstraction was accepted and published as one additive, backward-
compatible contract slice. Recurrence remains included because the documented
recovery workflow requires weekly, monthly, and quarterly proof, while the
optional six-month horizon is an explicit maintainer scenario. Real recurring
adoption is now evidenced by one real multi-frequency chain and two independent
consumer implementations. This supports cross-consumer interoperability for
that private chain; it does not establish universal or multi-adopter
compatibility.

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

## Published declaration shape

The published project contract nests occurrences under a stable series so
series metadata is not repeated and cardinality is unambiguous:

| Concept | Published field | Rule |
|---------|-----------------|------|
| Stable series identity | `id` | Unique within the project. |
| Occurrence kind | `kind` | `one_time` or `recurring`; never calendar grammar. |
| Responsible role | `responsible` | Sanitized stable role, not a notification destination. |
| Human action | `action` | Bounded single-line outcome; no executable material. |
| Runbook reference | `runbook_ref` | Key in the declared `runbooks` map. |
| Optional horizon | `horizon_at` | Recurring series only; stops later materialization, not open work. |
| Evidence contract | `evidence.ref`, `evidence.requirement` | Stable selector and the proof that may complete an occurrence. |
| Materialized occurrences | `occurrences[].id`, `starts_at`, `due_at` | Unique immutable id and absolute UTC window. |

`one_time` has exactly one occurrence and no horizon. `recurring` may have
multiple, including overlapping windows. Every join uses
`(project id, series id, occurrence id)`. The normative sanitized example is
`examples/project/infra.contract.yml`.

The action explains the human outcome and points to a runbook. It cannot carry
commands, requests, credentials, endpoints, or mutation payloads. Execution
retains its own authorization gate.

## Evidence and administrative resolution

Each projected occurrence carries evidence `result: missing | verified |
failed`. Verified and failed results require project authority, sanitized
`ref`, and bounded summary; a strict UTC `observed_at` is optional when the
evidence source can attest the event time. Missing evidence carries no
observation fields.

Completion is derived exclusively from matching `verified` evidence. Neither
`satisfied` nor `completed` is published as a project-maintained mirror.
Missing or failed evidence leaves the occurrence open.

Administrative resolution is optional and limited to `cancelled` or
`superseded`. Both require project attribution and a decision reference;
supersession also requires a distinct replacement occurrence in the same
series. Neither means the action completed, and neither may coexist with
verified completion evidence.

## Sanitized machine projection

The accepted egress conforms to
`schemas/operational-obligations-projection.schema.json`. Its publisher block
contains Home Infra's `generated_at` and publisher-owned `stale_after`; its
complete scope names the exact projects covered. Each project carries accepted
declaration revision and `accepted_at` attribution plus matching project-owned
evidence.

Only a fresh, valid, complete projection may withdraw an omitted obligation. A
stale, invalid, partial, or unavailable channel never proves an empty list,
withdrawal, or completion. Stateful operational consumers retain their last
valid projection with original attribution. Stateless consumers report channel
failure rather than saying no action is pending.

The strict egress excludes providers, recipients, tokens, endpoints, retries,
private notification policy, private paths, commands, Hermes acknowledgement,
recurrence expressions, and consumer-derived state presented as producer
truth. The normative sanitized example is
`examples/home-infra/operational-obligations.json`.

## Consumer derivation

Consumers keep independent axes for open-occurrence time
(`future | pending | overdue`), result
(`open | completed | cancelled | superseded`), evidence
(`missing | verified | failed`), channel integrity
(`fresh | stale | invalid | unavailable`), and completed timeliness
(`on_time | late | indeterminate`). There is no temporal `unknown`.

Only `open` receives a temporal state. Completion comes from verified evidence;
cancellation and supersession come from the separately attributed project
resolution object and never mean completion.

Completed timeliness is derived from `evidence.observed_at` against `due_at`,
so `on_time` and `late` remain stable regardless of when a consumer reads the
record. If `observed_at` is absent, timeliness is `indeterminate`, never
implicitly `on_time`. Failed evidence does not stop future, pending, or
overdue derivation.

`next` uses the total order `due_at`, `starts_at`, series id, occurrence id.
Ids are opaque tie-breakers. Overdue work remains separately visible.

Within one recurring series, the last materialized occurrence is the maximum
by `due_at`, then `starts_at`, then occurrence id. This remains deterministic
for overlapping windows and tied timestamps. Materialization is required only
after every accepted occurrence, including that last occurrence, is terminal.

A recurring series is `active` while any occurrence is open,
`materialization_required` when every occurrence is terminal and the optional
horizon has not been reached, and `period_ended` only after a declared horizon
passes with every occurrence terminal. Open work survives the horizon.

## Hermes delivery and acknowledgement

Hermes consumes the sanitized projection and keeps a deployment-private
delivery ledger. A deterministic delivery key includes project id, obligation
id, occurrence id, and relevant derived-state transition. The deployment owns
providers, destinations, retry and escalation timing, quiet hours, and message
policy.

Hermes may explain the action, current timing, evidence status, and runbook
reference. It may record that the operator saw or acknowledged a message. It
must not:

- mark the occurrence completed;
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
project evidence derives `completed`.

### Completed with evidence

Given matching project evidence with result `verified`, consumers derive
`completed` regardless of prior delivery or acknowledgement history. They also
derive `on_time` or `late` from evidence `observed_at` against `due_at`. The
evidence remains attributed to the project.

### Evidence failure

Given missing, failed, invalid, or mismatched evidence, consumers never derive
`completed`. Explicit missing or failed evidence leaves the occurrence future,
pending, or overdue; invalid or mismatched evidence is rejected. Stale,
invalid, or unavailable projection input is a separate channel-integrity
problem and can never become an empty obligation list. A consumer exposes
either problem without changing service health.

### Weekly, monthly, and quarterly work together

The project publishes three stable series, each with independently identified
absolute occurrences and the same optional horizon. Consumers can sort and
deduplicate them without implementing three calendar algorithms. Completing
one frequency has no effect on either of the others.

### End of a six-month period

The project materializes no occurrence starting beyond `horizon_at`. At the
horizon, any open occurrence remains actionable and may become overdue. The
series becomes `period_ended` only after the horizon passes and every
materialized occurrence has a terminal result. If the horizon
has not passed and a terminal recurring occurrence has no successor,
`materialization_required` prevents a silent memory gap.

## Compatibility and migration plan

1. **Protocol normative slice:** protocol 0.13.0 publishes the optional
   additive declaration, complete sanitized projection, canonical validation,
   examples, and derivation rules. Existing contracts remain valid.
2. **Project ownership:** project repositories publish obligation declarations
   and matching evidence. Home Infra explicitly accepts, attributes, and
   preserves them; it does not author project policy on their behalf.
3. **Portal dual read (complete):** Infra Portal reads the new accepted projection while
   temporarily retaining its private `operational_review` adapter. It uses
   generic obligation wording and keeps the health rail separate.
4. **First migration:** migrate the current active private pilot because it is
   live and exposes the legacy consumer coupling. Use the resolved backup trial
   only as a historical regression fixture; do not recreate it as open work.
5. **Recurring adoption (complete through Portal):** the project materializes
   weekly, monthly, and quarterly recovery programs as three project-owned
   series containing 34 occurrences; Home Infra accepts them and Portal reads
   the complete projection. Evidence production remains separate.
6. **Hermes consumption (complete):** deployed Hermes Lab 0.10.3 reads the
   projection, derives deterministic notices and retains private state with
   transport disabled. Home Infra independently monitors its status. Real
   delivery, acknowledgement and proactive transport remain separate evidence
   gates, and no execution capability follows from consumption.
7. **ForgeOS adoption:** scaffold and validate declarations through the
   canonical protocol validator. ForgeOS does not copy validation logic or
   automatically execute obligations.
8. **New projects:** use only the protocol declaration after the normative
   release and explicit Home Infra acceptance.
9. **Legacy removal:** project, Home Infra, Portal and Hermes consumption now
   provide the prerequisite adoption evidence, but private
   `operational_review` removal still requires its own authorized migration.
   Keep `preview.expires_at`, `next_run_at`, capability reviews, and incidents
   in their existing domains.

## Normative validation coverage

Protocol 0.13.0 adds positive and negative coverage for:

- optional additive compatibility with existing project contracts;
- stable and unique obligation and occurrence ids;
- strict UTC timestamps and `starts_at < due_at` ordering;
- horizon ordering and the rule that a horizon never closes open work;
- declared runbook references and bounded, non-executable display text;
- exact declaration/evidence joins and authority attribution;
- completion derived only from verified evidence for the exact occurrence;
- failed, stale, missing, and mismatched evidence never completing work;
- supersession requiring a replacement occurrence identity;
- independent consumer-clock derivation at before/start/due/after boundaries;
- on-time and late completion derived from evidence time, not read time;
- missing successor detection for recurring work within its horizon;
- three simultaneous frequency series and six-month horizon completion;
- sanitized strict egress with no provider, recipient, endpoint, credential,
  command, private path, retry, or notification-policy leakage;
- channel failure never manufacturing an empty obligation list;
- strict complete-scope withdrawal and last-valid retention semantics;
- Portal separation of obligation and service-health presentation rules;
- Hermes deterministic deduplication and acknowledgement non-equivalence rules;
- old consumers safely ignoring the optional new declaration.

The validation evidence now includes one real recurring multi-frequency
adopter through project declaration, Home Infra publication and two independent
consumer implementations: Portal and Hermes. This closes the second-consumer
implementation gate for the private chain, but does not justify a universal
compatibility claim across unrelated adopters.

## Explicit non-goals

This proposal does not define a scheduler, cron expression, calendar language,
notification provider, recipient model, retry algorithm, executable action,
remote mutation interface, incident workflow, health severity, or private
deployment policy. Its accepted implementation authorization covered this
protocol's SPEC, schemas, normative examples, validator, and documentation
only; it does not authorize edits to sibling repositories or runtimes.

## Adoption gate

### Open evidence-timing question

Recurring adoption must record whether a project may publish `verified`
evidence whose `observed_at` precedes the occurrence `starts_at` when its
`evidence.requirement` explicitly permits early satisfaction. Protocol 0.13.1
does not decide or change that producer-owned semantic; the first real
recurring adopter must supply the evidence needed to resolve it.

The normative slice was published in protocol 0.13.0 and its canonical
timestamp ordering was corrected in 0.13.1. NAS Backup, Home Infra, Infra
Portal and Hermes have since completed declaration, acceptance, publication
and two distinct read-only consumer paths. Home Infra 0.18.1 revision
`0a41f54a64c0880bcec8363d7e0af5177381cd48` records all 34 occurrences open
with missing evidence; that count is attributed source evidence rather than a
permanent expectation.
The next real evidence gate is project-owned NAS Backup evidence acceptance and
deployment followed by an observed `missing -> verified -> completed`
transition. Real delivery/acknowledgement and proactive Buzz transport remain
independent deployment decisions.
