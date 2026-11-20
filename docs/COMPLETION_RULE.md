<!-- doc-version: 0.18.1 -->
# Completion Rule

An infrastructure change is not complete until the durable source-of-truth repo
reflects the current observed state.

This rule applies to infrastructure changes, not to protocol-only or
consumer-only changes.

## Required Checklist

Project intake follows the adopter workflow even for source preparation, tests,
reviews, betas and temporary VM/NAS previews. A planning lifecycle defers runtime
evidence; it does not waive admission, documentation, identity or consumer plans.
An agent cannot create an ecosystem exclusion by labeling work "source-only".
Any exclusion requires recorded operator authority in the adopter's policy.

Every runtime resolves the adopter-designated monitoring consumer. Delivery
requires the specific service's fresh observation and reviewed tests for observer
loss, outage, expected stop and recovery. Monitor self-health or a catalog row
alone cannot prove service coverage. Source-only planning does not invent health.
Missing/stale evidence stays unknown; intentional stops are distinct from outages.

Authentication implementation, placement, login method and identity topology
are separate owner decisions. A selected application library does not imply a
common identity provider, Portal SSO or migration of existing applications.
Resolve the current attributed owner policy at creation, runtime and delivery;
never turn a generic continuation or reviewer advice into a provider selection.
New applications must implement the owner's selected authentication library;
unsupported stacks remain an explicit implementation gap, not permission for a
custom substitute. Individually declared read-only machine health/status paths
may be unauthenticated without exempting operator interfaces or private APIs.

Verify real login, a protected operation, anonymous denial and logout/session
revocation for application sessions. If the owner explicitly chooses OAuth/OIDC,
verify issuer-bound login and discovery; local credentials cannot substitute.
Application-local credentials do not depend on a common OIDC issuer. Preserve
existing deployed access through exact attributed owner dispositions, separately
from requirements for new applications. Existing HTTP Basic has no server-side
logout; record that limit rather than fabricate revocation evidence.
The adopter names its implementation, method, topology, authority and executable
checks. This neutral contract neither chooses a vendor nor claims runtime proof.

1. The live system was changed and verified, if applicable.
2. Human-readable source-of-truth docs reflect the new observed state.
3. Machine-readable catalogs reflect any tool-visible change.
4. The change is committed in the source-of-truth repo.
5. Relevant consumers were refreshed or verified.
6. Any warning, drift, or deferred gap is explicitly recorded.

If verification fails, the change is incomplete. Fix forward or roll back.
Leaving source-of-truth data and deployed consumers in disagreement is not an
acceptable end state.

## Operator first access

Every protected operator surface requires a usable first-access handoff before
claiming delivery, including preserved existing access and independently protected
components. Agent login/use/logout proves the service works for the agent; it
does not prove the operator knows how to enter it.

The handoff, in the operator's language, must give the canonical URL, the exact
account or account-selection instruction, an owner-approved route for retrieving
or activating the credential, and a usable recovery route. It must match the
account and non-secret credential identity used by the verified login. Explain
where to click or what to open, which entry to select, and any first-use step or
expiry. An agent-only CLI, a secret-store name without an exact locator, or
"log in" alone is insufficient. Verify operator access to the route; do not infer
it from the agent's service token. Existing known credentials may be reused;
never reset an account merely to create a new handoff.

Present the handoff to the operator before closure and repeat it or link to its
approved private location in the final response. Record source-bound, non-secret
evidence of delivery and independently review the actual instructions. The
adopter's current delivery check must reject missing or mismatched handoff
coverage. Mechanical checks do not prove comprehension or personal acceptance;
operator confirmation may strengthen evidence but is not a mandatory chore.

Keep passwords, API keys, activation tokens and secret values out of Git,
catalogs, Portal, Dossier, review packets and logs. Only approved non-secret
locators and receipts belong in evidence. This requirement authorizes no new
sharing channel, permission, credential rotation or weaker authentication.
Preserve historical receipts. Rechecking an older delivery exposes missing
handoff evidence as pending migration; it neither stops the running service nor
rewrites previous acceptance. Source planning may record the intended route without
claiming delivery. Changing a login URL, account, credential or retrieval route
requires a new verified handoff before the changed access is called complete.

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

## Intentionally omitted scheduled work

A request to skip an occurrence includes reconciling its expected monitoring
outcome. Follow [Execution Exceptions](EXECUTION_EXCEPTIONS.md): verify the
scheduler receipt and all affected notification consumers together. Preserve
actual observations, unrelated incidents, expiry and the next normal execution.
A scheduler-only omission with continuing false alarms is incomplete delivery.
