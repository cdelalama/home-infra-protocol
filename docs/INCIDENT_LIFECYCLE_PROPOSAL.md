<!-- doc-version: 0.13.7 -->
# Incident Lifecycle Proposal

Status: accepted for private incubation; second private case observed; not yet
normative.

## Problem

An active health banner proves only that a consumer currently observes a bad
state. It does not prove that a notification was delivered, a human
acknowledged it, recovery passed, or the incident was closed.

## Candidate lifecycle

The candidate separates five facts:

1. `detected`: a consumer recorded a qualifying observation and its timestamp;
2. `notified`: an independent delivery adapter recorded successful delivery;
3. `acknowledged`: an operator explicitly accepted ownership;
4. `recovered`: all required recovery-acceptance surfaces passed; and
5. `closed`: closure was explicitly recorded after recovery.

These are monotonic lifecycle facts for one incident identity. A repeated
probe, UI dismissal, process restart, or dashboard reload must not manufacture
acknowledgement or closure.

## Maintenance windows

A maintenance window has an owner, start, UTC deadline, and recovery gate.
While active it may suppress notification delivery, but observations and state
transitions continue to be recorded. If the deadline expires while the
incident remains active, notification becomes due immediately. A window cannot
close itself merely because time elapsed.

## Ownership and privacy

Probe consumers own detection evidence. Delivery adapters own notification
evidence. Operators own acknowledgement and closure actions. Recovery workflows
own all-surface acceptance evidence.

Provider names, endpoints, recipients, credentials, message bodies, retry
policy, and escalation routing remain private deployment policy. Any future
public shape should carry only provider-neutral outcome, timestamp, and
evidence-owner references.

Raw kernel logs, crash dumps, support bundles, application payloads, and
container environments also remain deployment-private. A public incident
record may state evidence class, custody owner, digest verification, exclusions,
and missing evidence without publishing the artifact or its private location.

## Second private case - sanitized evidence

A private source-of-truth repository opened one stable incident identity after
a shared container runtime was automatically disabled following a host-wide
memory failure. The event affected many services at once, so one recovered
container or route could not prove recovery of the incident.

The record separates facts that the first case could not exercise cleanly:

- detection and explicit operator acknowledgement are recorded;
- independent notification delivery is not evidenced;
- recovery and closure remain false while the shared runtime is stopped;
- the immediate allocation failure is distinguished from the unknown owner of
  the retained memory and from the small victim selected by the kernel;
- a minimal allowlisted evidence bundle is retained privately with restrictive
  permissions and a verified digest manifest; and
- two older matching messages remain candidate prior occurrences because their
  detailed signatures were not retained.

The incident ID was assigned when the record opened. The date in the filename
is the opening date, not an occurrence identity. Under that private record's
own rule, any later qualifying event appends under a prospectively declared
identity rule or opens a new identity; similar symptoms alone cannot merge
incidents retrospectively.

This case validates the need for stable identity, evidence custody, recurrence
rules, and independent lifecycle facts. It does not validate notification,
all-surface recovery, closure, maintenance-window expiry, or a public schema.

## Candidate record semantics

Private adopters should test the following semantics before promotion:

1. one stable incident identity survives recurrence and dashboard reloads;
2. `detected`, `notified`, `acknowledged`, `recovered`, and `closed` each name
   their evidence owner and observation time;
3. recurrence classification is prospective and evidence-backed;
4. facts, inferences, and unknowns remain separate, especially when a victim is
   not the root owner;
5. raw evidence custody is private and independent from sanitized consumer
   output; and
6. recovery enumerates every required surface and closure remains an explicit
   later action.

## Adoption gate

Before a schema proposal, all of these falsifiable conditions must pass:

1. one real incident progresses from detection through independent delivery,
   explicit acknowledgement, all-surface recovery, and explicit closure, with
   retained evidence for every transition;
2. at least one incident identity is assigned prospectively before a later
   qualifying observation, and the adopter demonstrates whether the observation
   appends as a recurrence or opens a new identity under written rules;
3. one real maintenance window exercises suppression, its UTC deadline or
   explicit end, and post-window delivery without suppressing observation;
4. delivery, deduplication, and recovery notification work independently from
   the dashboard;
5. a second independent consumer or implementation exercises the candidate
   lifecycle; if a documented safety or recovery constraint prevents that path,
   the adopter instead produces and retains equivalent evidence;
6. the incubation decides whether acknowledgement and closure belong in public
   protocol scope or a deployment-private extension; and
7. consumers retain rendered output for every exercised transition showing
   that `detected` was not presented as `notified`, `recovered`, or `closed`.

Until every condition passes, DF-016 remains proposal-only. No private field,
provider, endpoint, recipient, credential, raw evidence pointer, or runtime
action belongs in SPEC, schemas, examples, or reusable templates.
