# Explicit scheduled-execution exceptions

An operator may intentionally omit one scheduled occurrence without claiming a
new successful result. The owner records this decision separately from producer
telemetry. Consumers may suppress only the resulting, specifically identified
expected absence. This optional alert-policy overlay does not change inventory,
producer status, freshness, incident ownership or evidence of completion.

## Authority and custody

The owner MUST attribute the decision, project, environment and target, the exact
omitted occurrence, the next expected occurrence and a finite expiry. Bind the
record to the scheduler's applied receipt and a known successful baseline using
SHA-256 and its observation time; include the consumer projection binding when the wire view is sanitized.
The record MUST be installed once with exclusive creation, never edited or
extended in place. Reject overlapping records for the same target and occurrence.
A cancellation revokes the exception; a different occurrence needs a new explicit
operator decision and receipt. Producer `next_run_at` never authorizes suppression.

The deployment MUST protect policy from the service it supervises. Dedicated
service readers use an administrator-owned read-only file, with an administrator-
controlled parent. An attended owner process may use its private owner-only
record. Reject symlinks, unsafe owners/permissions, malformed/oversized documents
and untrusted writable ancestors. A private single-user group may be accepted
only after verifying its complete membership. This is local owner policy, not
an unauthenticated write API or a producer-authored status field.

## Consumer behavior

- Keep the actual observed result, timestamps and existing incidents unchanged.
  Show `expected_skip`, its attribution, target and expiry separately. Do not
  report a recovery, a fresh backup or a delivered notification for suppression.
- Apply only to the declared reason and unchanged known-success baseline. Each
  adopter documents its exact reason mapping. A strictly validated next run may
  also be treated as expected work: its start MUST fall in the next occurrence
  window and remain within the normal execution timeout. A new failure, unknown
  state, invalid input, missing observer or timeout MUST continue alerting.
- Suppression requires a trusted synchronized clock. A missing, invalid, expired
  or unverifiable policy MUST behave as absent. Failure of the overlay MUST NOT
  abort unrelated checks. Observations and histories continue during the window.
- Include execution timeout, consumer cadences and a bounded ingest margin in
  the expiry. At expiry, evaluate immediately on the next ordinary check, without
  waiting for an old reminder cooldown. Failed delivery remains retryable.
- A fresh successful result ends the match naturally. An unchanged stale result
  after expiry remains an incident. Do not rewrite an incident's prior cause or
  clear an unrelated incident as a side effect.
- If suppression needs another observer's attestation, require fresh bounded
  input, exact policy digest, baseline and occurrence binding. A stale, missing
  or changed attestation never authorizes suppression. Preserve the independent
  health/notification path; an optional policy projection failure must not
  redefine the underlying observer's health.

The optional neutral record shape is
[`execution-exception.schema.json`](../schemas/execution-exception.schema.json).
Adopters MUST additionally validate timestamp relationships, their own period and
runtime budgets, reason mappings, scheduler receipt, baseline and local custody.
A shape-valid example is not authority to omit work or suppress alerts.

## Completion transaction

1. Apply the exact scheduling exception and retain its verified rollback/receipt.
2. Install the attributed policy bound to that receipt and known successful state.
3. Enumerate all actual notification consumers, including legacy, independent
   and aggregated routes; qualify the exception, failure, running, expiry and
   recovery cases for each. A product name alone does not identify the sender.
4. Verify the operator view and each live consumer with preserved incident and
   delivery state. Use offline transport stubs for fault tests; test messages
   require their own authorization. Record any non-adopter explicitly.
5. Independently verify the next normal execution and subsequent genuine recovery.

If step 2 or 3 fails, restore the schedule when safe and authorized or report the
partial state and continuing alerts explicitly. Never call the omission complete
on scheduler evidence alone. A consumer that has not adopted this overlay keeps
normal alerting. UI adoption, transport acceptance and human receipt are separate.

This contract is separate from the proposal-only incident lifecycle in D-009.
It neither promotes that proposal nor assigns incident closure to a consumer.

## Independent observation cadence

Consumers may observe the baseline, next running state and next valid success at
different times. Validate each source independently against the authorized state
set and its freshness bound; do not require simultaneous phase/reason transitions.
A next success must start in the authorized next occurrence and pass normal
identity/integrity checks. A failed/invalid state is never an allowed lag state.
A transient expected-skip label during ingest is not fabricated completion.
