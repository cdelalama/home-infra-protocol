<!-- doc-version: 0.4.0 -->
# Reviews

Audit trail of consensus runs that produced load-bearing artefacts in this
repo. Each entry captures the **causal reasoning** that produced a decision,
not the transcript of the deliberation. The format is normative — see
`~/src/LLM-DocKit/docs/CONSENSUS_PROTOCOL_PROPOSAL.md` *Recording mechanism*.

A consensus run is invoked when a decision crosses one of the thresholds
named in the Consensus Protocol Proposal (contract changes, multi-repo
spans, security/persistence, multi-week reversibility, precedent-setting).
Routine work does not produce REVIEWS entries.

---

## 2026-05-03 — Deployment Evidence Contract

- **Decision**: Adopt a typed six-state lifecycle vocabulary, an explicit
  intent-vs-evidence rule, and an optional `deployment` block on `Service`,
  shipped together as the Deployment Evidence Contract in
  `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md`. Schema implementation is deferred
  to a future session.
- **Proposer**: Claude Opus 4.7 (1M context)
- **Critic**: GPT-5
- **Arbiter**: Carlos
- **Rounds**: 4
- **Outcome**: closed-accepted
- **Triggered by**: DF-002 + DF-003 (this repo) + DF-029 (LLM-DocKit) all
  pointing at the same modal failure: protocol declarations and the
  deployed reality drift apart with no canonical channel for the protocol
  to detect or even name the divergence.

### Decisions accepted

- **The standard is "not in silence", not "never happens"**: drift will
  occur (DNS, permissions, mis-implemented health endpoints, races during
  deploy); the protocol's job is to make any drift visible at session
  close, not to promise its erasure.
  - **Proposed by**: GPT-5 (against an earlier framing by Claude that
    aimed at full prevention).
  - **Objection considered**: Carlos pushed back that with capable agents
    we can be more ambitious than "detect promptly"; the formulation
    should not assume human-only vigilance.
  - **Why this resolution**: the two framings collapse on the same
    operational rule — *if drift exists, it must be visible at the
    closing handshake of any session*. Detection-not-prevention is a
    falsifiable bar; total prevention is not. A capable agent (future
    `infra-agent`) raises detection from manual to continuous, but the
    contract being detection-based stays the same.
  - **Risk accepted**: the contract does not block drift from happening,
    only from going unnamed.
  - **Implementing artefact**: `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md`
    *Problem statement* and *Decision* sections.

- **Six-state vocabulary (declared / implemented / built / transferred
  / running / serving)**: replaces the overloaded word "deployed" with
  six independently-verifiable states.
  - **Proposed by**: Claude.
  - **Objection considered**: GPT-5 confirmed the six states are
    sufficient and the names are good; suggested only minor naming
    polish on `transferred` (was "transferred to host"). Carlos
    accepted the six unchanged.
  - **Why this resolution**: each state corresponds to a distinct
    verification action (git log, repo HEAD, image inspection, host
    inspection, container inspection, health endpoint). Conflating any
    two is what produced the audit failure that triggered this run.
  - **Risk accepted**: six is one more state than most adopters will
    want to track in prose; the trade is that "operationally deployed"
    becomes falsifiable.
  - **Implementing artefact**: proposal *Decision → six lifecycle states*.

- **Intent vs evidence as a normative rule, not a recommendation**:
  catalog fields express intent; observation never lives in the catalog.
  - **Proposed by**: GPT-5 (contradicting an earlier Claude proposal to
    add hand-maintained `deployed_version` to the catalog).
  - **Objection considered**: Claude had argued the field would let
    consumers report drift visibly in the UI without extra plumbing;
    GPT-5 pointed out that any hand-maintained observation field rots
    predictably (DF-021/-022 territory in LLM-DocKit). Claude conceded.
  - **Why this resolution**: the architectural cost of mixing intent
    and evidence in the same artefact is permanent rot; the cost of
    keeping them separate is one extra layer of plumbing in consumers,
    which is small.
  - **Risk accepted**: until a consumer actually reads evidence (the
    `--check deployed-version` validator, or `infra-agent`), the
    evidence side stays manual.
  - **Implementing artefact**: proposal *Decision → Normative rule on
    intent vs evidence* and the *Anti-patterns* section.

- **Field shape: `deployment.expected` block with nested `health:`,
  not flat fields**: image and app version may diverge legitimately;
  flat fields cannot model that without forcing asymmetric simplifications.
  - **Proposed by**: GPT-5 (contradicting an earlier Claude proposal of
    flat `expected_image_tag` + `expected_version` fields).
  - **Objection considered**: GPT-5 produced a list of cases where the
    fields are not symmetric: `latest` tags, third-party images without
    health endpoints, app versions decoupled from image tags, services
    with no version-bearing endpoint at all (mosquitto). Claude
    accepted the structural improvement.
  - **Why this resolution**: the block lets each service opt in only
    to what it can express. Flat fields would force every service to
    fill or omit them; a block lets sub-blocks be omitted independently.
  - **Risk accepted**: slightly more verbose YAML for services that
    use both image and health.
  - **Implementing artefact**: proposal *Decision → Field shape*.

- **Severity levels (INFO/WARN/FAIL) as semantics, not as enforcement**:
  the protocol names the levels so consumers share vocabulary; the
  consumers (portal, agent) decide what action each level triggers.
  - **Proposed by**: GPT-5 (refining an earlier Claude formulation that
    coupled FAIL with "block session close").
  - **Objection considered**: Claude had argued for enforcement so that
    feature mismatches (catalog declares `interface: mqtt`, portal
    cannot serve it) become hard failures. GPT-5 pointed out that
    bundling enforcement into the contract is premature — measurement
    fidelity must come first.
  - **Why this resolution**: the discipline "first codify, then automate"
    that GPT had imposed earlier in the run applies here too. Codifying
    the levels gives consumers a shared language; enforcement is a
    consumer choice.
  - **Risk accepted**: a strict consumer and a permissive consumer may
    disagree about the same drift; that is the price of decoupling.
  - **Implementing artefact**: proposal *Decision → Drift severity*.

- **Five concrete scenarios MUST be in the proposal**: `infra-portal`,
  `tomatic-bridge` (planned), `esphome-builder`, `mosquitto`, external
  SaaS / tunnel.
  - **Proposed by**: Claude.
  - **Objection considered**: GPT-5 expanded the list slightly to make
    the third-party cases explicit (`vaultwarden`, Caddy as variants of
    third-party with different observability). Carlos arbitrated to
    keep five canonical scenarios with the variants mentioned in the
    `mosquitto` row.
  - **Why this resolution**: an abstract contract that has not been
    walked through real cases will fail at implementation; documenting
    the cases inline removes that risk and serves as an acceptance
    test for the schema.
  - **Risk accepted**: the listed cases will age and may need revising
    when the homelab evolves.
  - **Implementing artefact**: proposal *Concrete scenarios* table.

- **Anti-patterns section is normative, not advisory**: five forbidden
  patterns named explicitly so reviewers can flag violations.
  - **Proposed by**: Claude.
  - **Objection considered**: none material; GPT-5 endorsed without
    amendment.
  - **Why this resolution**: naming the antipatterns is half the work
    of preventing them — a future session reading the proposal sees
    the trap before stepping into it.
  - **Risk accepted**: the list is finite and a sixth antipattern will
    eventually surface; it gets added in a follow-up patch when it
    does.
  - **Implementing artefact**: proposal *Anti-patterns explicitly
    prohibited*.

- **ForgeOS as precedent, not as requirement**: the proposal mentions
  ForgeOS in a single section ("Future consumer / precedent") and does
  not let ForgeOS speculation drive any field, rule, or scenario.
  - **Proposed by**: GPT-5.
  - **Objection considered**: Carlos confirmed that Tomatic is being
    used as a proving ground for the patterns ForgeOS will inherit;
    Claude argued this raised the importance of getting the proposal
    right. GPT-5 pushed back that "raising the importance" must not
    become "letting future product drive present design".
  - **Why this resolution**: a proposal that solves the homelab well
    is the best precedent for ForgeOS; a proposal that solves a
    speculative ForgeOS would over-fit and likely fail both audiences.
  - **Risk accepted**: ForgeOS may later need to extend the contract;
    that extension goes through its own proposal at that time.
  - **Implementing artefact**: proposal *Future consumer / precedent*.

### Decisions rejected

- **Earlier Claude proposal to add a hand-maintained `deployed_version`
  field to the catalog**: rejected per the intent-vs-evidence rule
  above. Hand-maintained observation fields rot.

- **Earlier Claude proposal to make `infra-agent` v1 a precondition for
  Tomatic H0**: rejected by GPT-5 on grounds that infra-agent touches
  Docker socket, SSH, NAS, and alerts — security-sensitive territory
  that should not be rushed for a Tomatic dependency. Tomatic H0 is
  local and does not need infra-agent. Carlos agreed.

- **Promising "drift will not happen again"**: rejected as marketing
  framing that is not falsifiable. Replaced with the "not in silence"
  framing above.

### Open follow-ups

- The implementing session reads this proposal cold and ships the
  schema, SPEC, examples, and CHANGELOG entry. No deliberation
  needed; the proposal is self-contained.
- DF-002 stays `partially implemented` until a consumer (the portal)
  ships the actual probing.
- The optional `--check deployed-version` validator check in
  LLM-DocKit is a follow-up patch, not part of either current
  proposal.
- A `home-infra-protocol` patch may later promote the canonical name
  for the "consumed services" project-level extension that Tomatic's
  `infra.contract.yml` introduced informally on 2026-05-03.

---
