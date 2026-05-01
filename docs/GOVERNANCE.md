<!-- doc-version: 0.1.3 -->
# Governance

Home Infra Protocol should stay grounded in real implementations. The protocol
exists to name contracts already needed by source-of-truth repos, consumers,
telemetry providers, and recovery workflows.

## Field Policy

A protocol field should be added only when it is required by a real
implementation, a real consumer, or a documented recovery workflow. Speculative
generality is rejected.

When the ecosystem has multiple mature implementations, this rule should become
stricter: prefer adding fields only after at least two implementations or
consumers need them, unless the field closes a concrete safety or recovery gap.

## Ownership

- `home-infra-protocol` decides shape: schemas, vocabulary, contract semantics.
- A source-of-truth repo decides facts: hosts, services, URLs, runbooks,
  dependencies, and current observed state.
- A portal decides rendering: layout, filters, visual state, and interaction.
- A telemetry provider decides measurements: CPU, memory, probe results, and
  timestamps.
- No consumer promotes observations into facts without a source-of-truth change.
  Consumers may surface drift as warnings; closing the drift always requires
  editing the source-of-truth repo.

## Project Bootstrap Rule

New projects in this ecosystem should start from the LLM-DocKit template unless
the user explicitly approves a waiver.

The default expectation is:

- create the project from `cdelalama/LLM-DocKit`;
- keep LLM handoff/history/decision docs;
- keep version-sync validation where applicable;
- document any deviation from the scaffold in the new project's decisions.

This rule applies to new protocol consumers, telemetry providers, MCP servers,
and supporting tools such as a future `infra-agent`.

## Compliance Claims

Do not claim formal protocol compliance until the relevant protocol version has
stabilized and the implementation has been audited.

A future `COMPLIANCE.md` should include:

- protocol version;
- supported entities;
- supported required behavior;
- deviations;
- ignored or unknown field behavior;
- last audited date.

If `last audited date` is older than six months, the compliance statement is
stale and must be re-audited before being used as a public claim.
