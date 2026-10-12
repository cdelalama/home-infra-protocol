<!-- doc-version: 0.15.3 -->
# Completion Rule

An infrastructure change is not complete until the durable source-of-truth repo
reflects the current observed state.

This rule applies to infrastructure changes, not to protocol-only or
consumer-only changes.

## Required Checklist

1. The live system was changed and verified, if applicable.
2. Human-readable source-of-truth docs reflect the new observed state.
3. Machine-readable catalogs reflect any tool-visible change.
4. The change is committed in the source-of-truth repo.
5. Relevant consumers were refreshed or verified.
6. Any warning, drift, or deferred gap is explicitly recorded.

If verification fails, the change is incomplete. Fix forward or roll back.
Leaving source-of-truth data and deployed consumers in disagreement is not an
acceptable end state.

## Service retirement

Retirement removes a service from current operation and discovery. A missing
health observation, a disabled flag or an unknown state is not retirement.

1. Record explicit operator authority, exact service identities, exclusive
   resources and the shared resources that must survive. Stopping a service does
   not by itself authorize deleting its data, credentials or recovery copies.
2. Reconcile applicable active surfaces: runtime objects and deployment
   manifests; access/DNS/proxy routes; exclusive credentials; scheduled producers
   and monitors; inventory, catalog and dependency references; project candidate
   membership; and current consumer lists, topology, search, counts and details.
   Record each surface's owner and observed result; do not infer completeness
   from a container list or one fresh page.
3. Apply the explicitly authorized data/backup disposition. Preserve shared
   originals and immutable audit/history. Historical evidence must be identified
   as historical rather than presented as an active service. No global pruning
   or destruction of shared snapshots follows from one service retirement.
4. Publish the source-of-truth correction and refresh the required consumers.
   Only a successfully validated authoritative inventory can withdraw a service
   by omission. Unavailable or malformed input must not appear as successful
   removal; retain the last valid inventory with an explicit stale/error signal.
5. Verify fresh sessions and a session opened before the inventory change.
   Current views and actions must stop exposing the retired identity, while
   unrelated services and their user state remain intact. Record the consumer's
   refresh bound or explicit reload requirement. A page opened only after the
   change does not test long-lived client reconciliation. Old application code
   can require one upgrade reload; state that boundary explicitly.
6. Record remaining gaps and complete the existing owner publication/Dossier
   obligations. Retirement remains incomplete while a required current consumer
   still presents the service as operational inventory.

## LLM Rule

Any human or LLM-assisted infrastructure change must update the source-of-truth
repo in the same session before the change is considered complete.
