<!-- doc-version: 0.1.0 -->
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

## LLM Rule

Any human or LLM-assisted infrastructure change must update the source-of-truth
repo in the same session before the change is considered complete.
