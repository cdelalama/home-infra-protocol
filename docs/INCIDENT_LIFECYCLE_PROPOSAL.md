<!-- doc-version: 0.13.3 -->
# Incident Lifecycle Proposal

Status: accepted for private incubation; not yet normative.

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

## Adoption gate

Before a schema proposal:

1. run at least one real maintenance window through detection, suppression,
   deadline or explicit close, and all-surface recovery;
2. retain evidence that delivery, deduplication, and recovery notification work
   independently from the dashboard;
3. decide incident identity and recurrence semantics;
4. decide whether acknowledgement and closure belong in protocol scope or in a
   deployment-private extension; and
5. prove consumers do not present `detected` as `notified` or `closed`.
