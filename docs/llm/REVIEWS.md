<!-- doc-version: 0.13.10 -->

## 2026-09-23 - DocKit fleet source update

Review: exact claude-opus-5-5, requested high effort, read-only Read/Glob/Grep.
Session: e06df549-3d43-4283-90a3-4f1833f7af04; modelUsage verified.
Command selected --model claude-opus-5-5 --effort high --restricted
--permission-mode dontAsk --tools Read,Glob,Grep --allowedTools Read,Glob,Grep
--strict-mcp-config --mcp-config empty; resumed the same session for findings.
Reviewed candidate tree (non-commit object): f0785c88093d3c3b2bbe35d6074efd08513099a1.
Status: SOURCE/ROLLOUT GO after three same-session rounds. Publication is source-only.
Validation: project version/session checks pass; identical delivery helpers use
the central 84-case suite; DocKit source validator suite passes 96 cases.
Evidence is executor-supplied. Receipt-only metadata does not change delivery
inputs. See LLM-DocKit/docs/FLEET_ROLLOUT_2026-09-23.md for final verdict,
publication and project-specific exceptions. No runtime authority is added.

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

## 2026-10-01 - Mandatory Portal and Dossier integration controls

Exact `claude-opus-5-5` with `--effort high`; actual modelUsage and
canonicalModel verified. Separate advisory and independent tool-free packet
reviews. SOURCE_GO covers reviewed source and bounded DEV pilot only; it does
not establish installed, Windows, fleet or broader Portal roadmap acceptance.
The author supplied source, real rendered operator text, tests and private
probe receipts; the auditor did not run host commands. Earlier blocking rounds
remain in private custody and were reconciled in subsequent exact-source packets.

Validation: 52 integration tests (including 12 owner routes), 8 ship tests,
birth/reentry, selective installer, 3 Protocol profile tests and live catalog
CLI pass. Full Home suite: 301 run, 297 pass, 2 failures and 2 errors. The stale
Plaud expectation and registry count (37 versus current38) reproduce on the
published base. The archive fixture conflicts with managed TMPDIR nesting; a
private rerun used the actual managed top-level staging root, retaining original
assertions. The unrelated ingress executable mode was normalized from775 to755;
its bytes were unchanged. Both environment cases passed their reruns. Four Home
shell suites and final owner closeout pass. This is not a fully green raw suite.
The verification review explicitly reconciles these results and preserves the
source GO; reviewed source hashes remained unchanged. No automated executable
caller of audit-catalog.py was found in scripts/.github/.agents (two tests only).

Raw prompts/results, logs and captures remain outside Git/Dossier. Exact metadata:

- advisor: session `1e2b6f07-d68f-41a6-bd56-60b729901c37`; prompt SHA256 `db965b1e8ef1ed25559efff1cb1bcdf1d5673341f0dd65a52d8487d3413c1f6f`; result SHA256 `4efde42000a4311f6bcf615a1f664017246f9f21566a3cf1888016901933f27e`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- auditor: session `9885db25-68d8-48ab-8c5b-ac41a90e0bbc`; prompt SHA256 `fe30991d66cdaf0cf394d261de123b4962d436e581a2ba7aed9da63c7c9d025b`; result SHA256 `aa41ad9e38dda21c9c0188408fc353aa5c0fc08bec529950ffbf08535f80e470`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- auditor-followup: session `d590094d-54e0-45d9-8d90-76350e8e7e4c`; prompt SHA256 `eaeb320ac5ab94d8a83378c2264d3b45bf715c68f0ec40ccfd88fc7f021ddd93`; result SHA256 `1084ff4e214e44461c2e5530b733bf85cadb6656de63870a87727c1f0b6b503c`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- auditor-round3: session `97830343-c724-431b-a9d1-e0faaf5a3034`; prompt SHA256 `80fe4acd1a4476d43f690cd861ae3ccaab8ead7d6805461c404778e004f6a40a`; result SHA256 `c416c186aa98d0647847b9350ef055ecefdb90d43b5f6de15602c553c6a04757`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- auditor-verification: session `56b6f3b5-8ea1-408d-9f80-7895440c0f34`; prompt SHA256 `e3c0b858f534f58c79c3dc479e30986632130567c355f46f3f30e2193628a4c0`; result SHA256 `02ba191669466a11726175aaa402f3aff94a1bfc1223d9bf35b00ab53cbbf787`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.

Publication and installed/runtime results receive separate observed receipts;
Windows SSH publickey denial leaves Windows acceptance open.

## 2026-10-01 - Integration closure and coordinator receipt

DOCUMENTATION_GO for neutral published profile guidance and source-slice closure.
Adopters own installed host acceptance and retain their evidence separately.
Protocol owns future report-only profile drift; Home Infra/ForgeOS own adopter
inventory and migration; Infra Portal coordinates.
Exact claude-opus-5-5/high; actual canonicalModel verified. Independent
tool-free supplied-evidence review; no reviewer host execution. Earlier withheld
documentation verdict and all raw packets remain private, outside Git/Dossier.
Validation binds the final candidate manifest and includes exact run timestamps.
Full Home suite remains non-green with recorded baseline/environment deviations.

- auditor-closure: session `f12642f6-3efa-49f2-b7dd-547e196b6d2e`; prompt SHA256 `4b9e1ff7c5e062d3346fbaee8c57559ae57347b1033239369f8b3e53b09ddedc`; result JSON SHA256 `48b4f75ab721033437940d31d4b55bc2c1b6731f52a95549e737a30dc799d019`; response text SHA256 `816cb4f3ca73fed021d239227cba33acb6b9a50838eab48c9937851dfd2b5689`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- auditor-closure-followup: session `3d32a8b0-7797-4e86-b353-d97c71efc0af`; prompt SHA256 `4613025618ba9e10b5305318c218cd112060b867463fb498db560d41fa905596`; result JSON SHA256 `0ed1c2f84f923da7f50e07470ec146707d5cc944387e065b5836e09b28d43b45`; response text SHA256 `76b6ce4c892b56ef502f4a34039c5f15cb3fc4ab60c951b5b5d2d35b52b59f2f`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- auditor-closure-final: session `6530c13d-3fab-498f-936f-d4dbbb93cc00`; prompt SHA256 `fb001afe862cb635417daed2e7bcd78a4dd7f431457b1d50558c998f6d1e5583`; result JSON SHA256 `db847b8279fa9804013c2046ec5a7369d9c335e990d7b1ad9733ec7987672f19`; response text SHA256 `de42ce94ccbdd4e8de62b80a5adadb2f32e830c8b54087acacff23c2029424d8`; command SHA256 `8c5867491bf4a1cc665d978814365d12d1c01ac4ac7c079be33f57343786b2c8`.
- Final validation receipt SHA256 `4655947ed863b5bef31e8bc182cb0a1f1ac49092e8cb6c5d98b455796e15c375`.
