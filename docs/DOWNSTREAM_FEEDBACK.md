<!-- doc-version: 0.9.1 -->
# Downstream Feedback

Living log of observations collected from real adopters of `home-infra-protocol`.
Each entry describes a concrete drift, gap, or friction point encountered by a
consumer (`home-infra` as source-of-truth, `infra-portal` as consumer, a project
contract such as `tomatic`'s `infra.contract.yml`) along with the implication
for the protocol itself. Use this file to prioritise protocol improvements.

This file is the maintainer's backlog of protocol-level work suggested by real
adoption. Pattern modelled on `LLM-DocKit:docs/DOWNSTREAM_FEEDBACK.md`.

## Why this exists

The protocol's `docs/GOVERNANCE.md` *Field Policy* says:

> A protocol field should be added only when it is required by a real
> implementation, a real consumer, or a documented recovery workflow.
> Speculative generality is rejected.

That rule rejects fields without a real motivation, but it does not describe
*how* a real motivation gets captured. Without a canonical channel, an adopter
who hits a gap has three bad options: edit the SPEC unilaterally, file an
issue and lose the operational context, or write a personal memory and let the
lesson stay invisible to the protocol. This file is the canonical channel:
adopters write `DF-NNN` entries here when they hit a gap; the protocol decides
whether and how to act on them; consumers learn from the audit trail.

## Status legend

- `open` — observed, no fix planned yet
- `accepted` — listed in a `*_PROPOSAL.md` and committed to the roadmap
- `partially implemented (<version>)` — the symptom-level fix is closed in a
  concrete release of the source project, but the protocol-level fix (schema,
  spec, validator) is still open
- `implemented` — a SPEC change, schema change, or example has landed that
  addresses both the symptom and the protocol-level issue
- `rejected` — intentionally out of scope; includes rationale
- `superseded-by: DF-NNN` — merged into another entry

## Category legend

- `field-gap` — the SPEC or schema lacks a field that adopters need
- `semantic-gap` — the schema accepts a value that no consumer implements
- `consumer-drift` — the schema and a real consumer have diverged
- `process` — the gap is in the workflow around the protocol, not in a file
- `usability` — the artifact is correct but easy to use wrong

## How to add an entry

Use the next free `DF-NNN` (zero-padded). One entry per distinct problem.
Cross-reference related entries via `Related: DF-AAA, DF-BBB`. Header format:

```
## DF-NNN — Short descriptive title
- Source: <project> (<version or date at time of observation>)
- Date observed: YYYY-MM-DD
- Category: field-gap | semantic-gap | consumer-drift | process | usability
- Status: open | accepted | partially implemented (<version>) | implemented | rejected | superseded-by: DF-NNN
- Related: DF-AAA, DF-BBB   (optional)

Observation: what concretely happened, with file:line references when
applicable. Keep it short — convey the failure mode, not retell the session.

Protocol implication: what the protocol should change (new field, schema
update, validator check, doc rule). Be specific. If multiple options exist,
list them with tradeoffs.

Implementation hints (when the recommended option is decided): an actionable
checklist that translates the chosen option into concrete changes, so a
fresh session can ship without bespoke prompting. Format:

  Files to touch:
    - <path>: <what changes>
    - <path>: <what changes>
  Version bump: <patch|minor|major> per docs/VERSIONING_RULES.md
  Cross-repo touches required: <none | list, read-only by default>

This block is OPTIONAL when the DF is filed but SHOULD be added before the
DF moves out of `open`. It is the difference between "DF describes a
problem" (open) and "DF is dispatchable as a closure session" (accepted).

Mitigation in source project (optional): how the downstream project worked
around the gap in the meantime, if relevant.
```

Keep entries in ascending order. Once an entry reaches `implemented` or
`rejected`, leave it in place as an audit trail — do not delete.

If a DF entry calls for a structural change (new field, new schema rule, new
contract section), the resolution path goes through a `docs/*_PROPOSAL.md`
document referenced from the DF entry. The proposal is what the next session
implements; the DF is the empirical record of why.

---

## DF-001 — `Service` records a single `url` but adopters need to declare whether the service has a navigable web UI

- Source: `tomatic` v0.1.3 + `home-infra/catalog/services.yml` (mosquitto entry, `infra-portal` rendering)
- Date observed: 2026-05-02
- Category: field-gap
- Status: implemented (0.2.0) — schema, SPEC, examples, and Consumer support matrix shipped per `docs/SERVICE_INTERFACE_PROPOSAL.md`. Consumer-side rendering tracked in `infra-portal` HANDOFF *Pending work* item 2.
- Related: DF-002

### Observation

Tomatic (an autonomous tomato grow project) decided as part of ADR-0011 to
reuse the existing shared Mosquitto on the `zigbee` RPi instead of running
its own broker. To make that decision visible operationally, the operator
added Mosquitto as a first-class service in `home-infra/catalog/services.yml`:

```yaml
- id: mosquitto
  name: Mosquitto MQTT
  category: infra
  url: mqtt://10.0.0.139:1883
  status:
    type: tcp
    host: 10.0.0.139
    port: 1883
```

The schema at `schemas/services.schema.json` accepts this — `url` is just
`z.string().min(1)`, no scheme constraint. But the consumer (`infra-portal`)
treats `url` as "openable in a browser tab": `App.tsx:149` calls
`window.open(svc.url, "_blank")` whenever the operator clicks the service
card. With `url: mqtt://...`, the click opens an empty tab or asks the OS for
a `mqtt://` protocol handler. The interaction silently fails.

The convention "every service in the catalog has a clickable web UI" is
**implicit**: the SPEC says a service is "a user-visible or operator-visible
capability" and lists `url` as required. It does not say "the URL must be
navigable in a browser". Adopters have so far filled the catalog only with
HTTP(S) services because that was the only consumer that mattered. The first
non-HTTP service exposes the gap.

### Protocol implication

The protocol needs a way to express what kind of interface a service offers
so consumers (the portal first; future MCP servers, agents, recovery
workflows next) can render and probe it correctly. Three options were
considered (full pros/cons in `docs/SERVICE_INTERFACE_PROPOSAL.md`):

1. **Infer from URL scheme** (`http://` / `https://` ⇒ web UI; otherwise
   not). Cheapest. Implicit and brittle for HTTP APIs without HTML.
2. **Add a binary field** `web_ui: bool` (default `true`). Explicit but
   limited.
3. **Add an enumerated field** `interface: web | mqtt | tcp | api | ssh | none`.
   Most expressive; sets up the future topology view in the portal to
   render different edge styles per interface kind.

The chosen direction is option 3, captured in
`docs/SERVICE_INTERFACE_PROPOSAL.md` for the next session to implement.

### Mitigation in source project

`tomatic`'s `infra.contract.yml` declares the broker via the existing
`mqtt:` block (project-side, not catalog-side). `home-infra/catalog/services.yml`
keeps the Mosquitto entry visible because the operator wants to *see* what
runs underneath, not hide it. The temporary UX cost (empty tab on click)
is accepted until the proposal lands.

---

## DF-002 — `status.type: "tcp"` is in the schema enum but no consumer implements it

- Source: `infra-portal` v0.7.2 (`src/server/health.ts:82-86`)
- Date observed: 2026-05-02
- Category: semantic-gap, consumer-drift
- Status: implemented — closed by `infra-portal` 0.8.0 (TCP probe + interface-aware render, deployed to NAS 2026-05-03); production reconciled to 0.8.1 the same day after a post-deploy audit surfaced the `expect_status` ground-truth bug (see DF-004 + `infra-portal` CHANGELOG 0.8.1). (b) protocol-side guardrail in protocol 0.2.0: SPEC.md *Consumer support for `interface`* matrix. (a) consumer-side cure in `infra-portal` 0.8.0 (`tcpProbe` via `node:net` `Socket`), extended in 0.8.1 (`decideHttpState` honors `expect_status` outside 2xx-3xx). Promoted to NAS production on 2026-05-03 per the six-step evidence plan in `~/src/home-infra/docs/SESSION_HANDOFF_2026-05-04_ECOSYSTEM_RECONCILIATION.md` §8. Runtime evidence at 0.8.1: `docker ps` reports `infra-portal:0.8.1` healthy; `/api/health` returns `0.8.1`; `mosquitto: up` (TCP probe); `unifi-mcp: up` (HTTP 406, expect_status honored); 10 services up + 1 disabled (pentagi by design) + 0 down. The "operationally deployed" rule from `DEPLOYMENT_EVIDENCE_PROPOSAL.md` is satisfied.
- Related: DF-001

### Observation

`schemas/services.schema.json` declares the status probe type as:

```json
"type": { "enum": ["http", "tcp", "none"] }
```

`tcp` is therefore a **valid** value any adopter is entitled to use. But
`infra-portal/src/server/health.ts` lines 82-86 contain:

```typescript
if (svc.status.type !== "http") {
  return { ..., message: `${svc.status.type} probes not implemented yet` };
}
```

In other words: the only consumer of the schema honours `http` and silently
no-ops on `tcp` and `none`. A service that declares
`status.type: tcp` (e.g. the Mosquitto entry from DF-001) passes catalog
validation, the YAML loads cleanly, but the service stays in
`unknown` state forever because nothing actually probes the port.

### Protocol implication

This is the modal failure pattern that
`LLM-DocKit:DOWNSTREAM_FEEDBACK.md` calls "schema accepts X, consumer does
not implement X". Three options, not mutually exclusive:

(a) **Implement TCP probes in `infra-portal`** (the natural cure; ~10 lines
   with `net.connect` + a timeout). This is a consumer-side change, tracked
   in `infra-portal`'s `docs/llm/HANDOFF.md` *Pending work* and noted here
   so the protocol records the empirical demand for the schema feature.

(b) **Document the gap explicitly in the SPEC.** Add a "Consumer support
   matrix" section in `SPEC.md` that names which schema values which
   consumer supports as of which version. Adopters reading the schema get
   to see "tcp: portal v0.7.2 = stub, planned v0.8.x" before they design
   around it. Modest authoring cost, eliminates one whole class of
   silent surprise.

(c) **Add a validator that warns when `home-infra/catalog/services.yml`
   uses a status type the active consumer doesn't implement.** Stretch:
   needs the consumer to declare its capability surface in a manifest, or
   the validator to know about specific consumers. Probably overkill until
   there are multiple consumers to disagree.

The recommended sequence is (a) first (implement TCP probe), then (b) as
a permanent guardrail; (c) is only worth designing once a second consumer
exists.

### Mitigation in source project

`tomatic` accepts the `unknown` state on the Mosquitto entry until
`infra-portal` ships TCP probes. The lesson is captured here so the
next time someone considers using a schema-allowed-but-unimplemented
value, they know to check.

---

## Meta-observation

DF-001 is a **field-gap** (the schema lacks a field adopters need).
DF-002 is a **semantic-gap** (the schema offers a value no consumer
implements). Both surfaced from the same adopter session (Tomatic v0.1.3
deciding its broker topology), and both expose the same root pattern:
*the protocol's contracts and its consumers' implementations drift in
the absence of a canonical channel for adopter feedback.*

This file is the canonical channel. Every future adopter is expected to
file `DF-NNN` entries here when they hit a gap, and every protocol
release should review the open DF list before deciding what to ship next.

---

## DF-003 — `Consumer support for interface` matrix conflates repo HEAD with deployed version

- Source: `infra-portal` v0.8.0 in repo / v0.7.2 in production + `tomatic` v0.1.5 audit
- Date observed: 2026-05-03
- Category: semantic-gap, usability
- Status: implemented (0.3.0) — Deployment Evidence Contract shipped: schema gains optional `deployment` block (`expected.image` + `expected.health` with `url`/`version_json_path`/`version`); SPEC.md *Service* gains the six-state vocabulary, the "operationally deployed" rule, the intent-vs-evidence rule, and a brief description of the `deployment` block; `examples/home-infra/catalog/services.yml` shows three of the five proposal scenarios on sanitized hostnames (own app + endpoint, third-party with HTTP UI, third-party TCP-only); `docs/PROJECT_CONTRACTS.md` notes the same `deployment` block applies to project-level service objects with the same semantics. DF-002 stays `implemented` (consumer-side TCP probe shipped in `infra-portal` 0.8.0/0.8.1 and is in production); the new contract gives that work a vocabulary and an extension path (e.g. wiring a `deployment.expected.health.version` comparison in the portal as a follow-up consumer-side patch).
- Related: DF-001, DF-002
- Resolution path: `docs/DEPLOYMENT_EVIDENCE_PROPOSAL.md` (Deployment Evidence Contract). The proposal goes beyond the matrix-only fix originally suggested here: it introduces a typed six-state vocabulary, an explicit intent-vs-evidence rule, and an optional `deployment` block on `Service`. The implementing session shipped those changes in protocol 0.3.0. The deliberation that produced the proposal is recorded in `docs/llm/REVIEWS.md` 2026-05-03.

### Observation

The `SPEC.md` *Service* section, after 0.2.0, contains a "Consumer
support for `interface`" matrix shaped like:

```
| Consumer     | Version | Renders | Probes | Notes |
|--------------|---------|---------|--------|-------|
| infra-portal | 0.8.0   | yes     | http+tcp | ... |
```

The intent was to give adopters one place to check what each consumer
supports. In practice the `Version` column is **ambiguous**: the only
reading that closes DF-002 (the modal failure "schema accepts X,
consumer doesn't implement X") is `Version = deployed version`,
because adopters experience consumers through their deployment, not
through repo HEAD. But every entry written so far has been populated
from repo HEAD because that is what the implementing session sees.

The audit on 2026-05-03 surfaced the gap concretely:

- `infra-portal` repo at `0.8.0` implements `Service.interface`
  rendering and `status.type: tcp` probing.
- `infra.lamanoriega.com/api/health` returns `{"version":"0.7.2"}`.
  The deployed portal does NOT yet read `interface` and still answers
  `tcp probes not implemented yet` for the `mosquitto` entry, which
  remains in `state: unknown`.
- A reader who declares `interface: mqtt` on a new catalog entry
  expects the portal to render a "copy connection string" button. They
  get the old `window.open` behaviour (silent failure on `mqtt://`
  URLs) until the operator rebuilds the image, transfers it to NAS,
  and restarts the compose.

The repo column tells one truth, the deployment tells another, and the
matrix names neither explicitly.

### Protocol implication

Three options, in increasing structural cost:

(a) **Doc-only fix (cheap, narrow).** Rename the `Version` column to
   `Repo Version` and add a sentence above the matrix: *"This matrix
   describes what each consumer's repo HEAD implements. Deployment
   lag is tracked separately in `home-infra/docs/INVENTORY.md`."*
   Closes the ambiguity for the reader without adding a field.

(b) **Add a `Deployed Version` column.** Each row gains a second
   version field, populated by the operator (or a script) reading the
   live `/api/health` of each consumer. Catches the `0.8.0 / 0.7.2`
   drift visibly. Cost: someone has to maintain it; without
   automation, the column will rot.

(c) **Add `expected_version` / `deployed_version` to `Service`.**
   Schema change. The catalog declares the version it expects;
   `infra-portal` (or another consumer) reads the live `image_tag`
   and warns when they diverge. Most powerful, most work. Probably
   premature — file as a follow-up DF if (a) and (b) prove
   insufficient.

Recommended sequence: (a) in the next SPEC.md patch (cheap, immediate
clarity), (b) when there is a second consumer with `interface`
support, (c) only if drift becomes a recurring incident worth
automating away.

### Cross-protocol relationship

This DF is the home-infra-protocol-side counterpart of an LLM-DocKit
DF filed in the same audit session
(`~/src/LLM-DocKit/docs/DOWNSTREAM_FEEDBACK.md` DF-029). LLM-DocKit's
DF describes the same "repo VERSION ≠ deployed version" class as a
generic validator gap; this DF describes the specific shape it takes
inside our matrix. LLM-DocKit could add an optional `deployed-version`
check any DocKit-scaffolded project opts into; home-infra-protocol
needs to fix the SPEC matrix regardless because it is a documentation
artifact that already exists.

### Mitigation in the audit session

The audit (tomatic v0.1.5) recorded the deploy lag in
`home-infra/docs/{INVENTORY,SERVICES}.md` and noted that `mosquitto`
status stays `unknown` and `interface`-aware rendering looks identical
to old `url` behaviour until `infra-portal:0.8.0` is promoted to
production. No code change in this session; the image promotion is a
separate operator-driven action.

## DF-004 — Default `interface: web` when omitted is unsafe for HTTP APIs without HTML

- Source: `home-infra/catalog/services.yml` (unifi-mcp entry) + `infra-portal` 0.8.1 in production, 2026-05-03
- Date observed: 2026-05-03 (surfaced by operator-auditor)
- Category: field-gap, semantic-gap
- Status: implemented (0.3.1) — option (a) shipped: SPEC.md *Service / interface* rule rewritten to fire on "service does not serve HTML at the listed `url`" (covers HTTPS APIs without HTML, the original gap), plus explicit guidance to declare `interface: api` for HTTP APIs without HTML; `schemas/services.schema.json` description updated to match; `examples/home-infra/catalog/services.yml` `example-api` entry gains an explanatory comment naming the new rule. Cross-repo read-only sweep of `~/src/home-infra/catalog/services.yml` performed in the same session: no drift — all 11 services either correctly declare a non-`web` interface (`mosquitto: mqtt`, `unifi-mcp: api`, `esphome-builder: web` explicit) or omit the field and genuinely serve HTML at the listed URL. Options (b) validator check and (c) schema-required remain queued (a)→(b)→(c) as originally sequenced.
- Related: DF-001 (where `interface` was introduced), DF-031 (ecosystem prior-art search)

### Observation

`SPEC.md` *Service / `interface`* states:

> When `interface` is omitted, consumers MUST treat the service as having a web UI (`interface: web`) for backward compatibility with v0.1.x catalogs. When `url` does not start with `http://` or `https://`, the service MUST declare `interface` explicitly.

The "MUST declare explicitly" rule only fires for non-HTTP URLs (e.g. `mqtt://`, `tcp://`, `ssh://`). For HTTP APIs **without HTML** — Model Context Protocol endpoints, REST APIs, GraphQL servers, JSON-RPC services — the URL is `https://...`, the rule does not fire, and the default `web` is silently inherited even though the service has no browser UI.

Concrete failure observed with `unifi-mcp` on 2026-05-03:

1. Catalog entry omitted `interface`. The "MUST declare" rule did not fire (URL is HTTPS).
2. `infra-portal` 0.8.1 read `svc.interface ?? "web"` per the SPEC.
3. Portal rendered an "↗ Open" button.
4. Clicking it called `window.open("https://unifi-mcp.lamanoriega.com/")` → tab opens at 404 "Not Found" (root returns 404 by design; actual MCP endpoint is `/mcp` and uses Streamable HTTP, no HTML).

Carlos, as operator-auditor, surfaced this: *"why does the unifi-mcp service show an open button and launch a web page when an MCP server has no web UI? Is our protocol failing?"*

The portal cumple the SPEC. The catalog cumple the SPEC. But the user expectation was violated, and the failure mode is invisible to a content-blind validator: every service with an HTTPS URL and an omitted `interface` is silently scored `web` regardless of whether the URL actually serves HTML. Same family as DF-002 inverted: there the schema accepted a value no consumer implemented; here the schema accepts a *missing* declaration and the consumer applies a permissive default that is wrong for a broad class of services.

### Protocol implication

Three options, increasing strictness:

(a) **SPEC clarification (cheap)**: rewrite the rule so it is broader. Replace *"when `url` does not start with `http(s)://`"* with *"when the service does not serve HTML at the listed `url`"*. Plus explicit guidance: "for HTTP APIs without HTML (MCP, REST, GraphQL, JSON-RPC), declare `interface: api`." Intent-friendly; unverifiable from catalog alone — adopters can still omit.

(b) **Validator check** (medium cost): a future `dockit-validate-catalog.sh` (or equivalent) that scans `services.yml`, finds any `https://` entry without `interface` declared, and warns. Mechanical, runnable in CI; forces adopters to be explicit on commit. Optional probe of the URL's `Content-Type` to suggest `web` vs `api` is nice-to-have but not required at protocol level.

(c) **Schema-level required** (highest cost): make `interface` REQUIRED on every service in a future major. Backward-compatible default goes away. Most explicit; needs coordinated release across consumers + migration window.

Recommended sequence: (a) immediately in the next SPEC patch as a clarification + adopter guidance; (b) when the second adopter trips on it; (c) reserved for v1.0 of the protocol.

### Implementation hints (option (a))

Files to touch:
  - `SPEC.md` *Service / interface*: rewrite the "MUST declare explicitly" rule from *"when `url` does not start with `http(s)://`"* to *"when the service does not serve HTML at the listed `url`"*. Add explicit guidance: *"for HTTP APIs without HTML (MCP, REST, GraphQL, JSON-RPC), declare `interface: api`."*
  - `schemas/services.schema.json`: update the `description` of the `interface` field to reflect the broader rule. Do **not** change `required`, do **not** close the enum, do **not** change the default.
  - `examples/home-infra/catalog/services.yml`: ensure `example-api` exists with `interface: api` and a brief comment naming the new rule (HTTP APIs without HTML must declare `interface: api`).
  - `docs/DOWNSTREAM_FEEDBACK.md`: this DF's status → `implemented (0.3.1)`.

Version bump: **patch (0.3.1)** per `docs/VERSIONING_RULES.md` — clarification + adopter guidance, no breaking change. Use `scripts/bump-version.sh 0.3.1`; do not edit `<!-- doc-version: -->` markers manually.

Cross-repo touches required: read-only sweep of `~/src/home-infra/catalog/services.yml` per `docs/LLM_WORKFLOW.md` *When Changing Field Semantics*. Halt and report drift to the operator; do **not** edit `home-infra` from the closing session.

### Mitigation in source projects

`home-infra/catalog/services.yml`: unifi-mcp now has `interface: api`, `url` points at `/mcp` directly. Portal renders "📋 Copy" instead of "↗ Open" — verified after sync.

Sweep of other catalog entries for the same class:
- `infra`, `zwave`, `ha`, `zigbee2mqtt`, `grafana`, `pgadmin`, `y2t`, `pentagi`: all serve HTML at their listed URL → default `web` is correct.
- `mosquitto`: already `interface: mqtt`.
- `esphome-builder`: already `interface: web`.
- `unifi-mcp`: now `interface: api` (this fix).

The lesson generalises: **when a new field with a permissive default lands, sweep the existing catalog for cases where the default is wrong in the same session as the field's introduction.** We did not pay this cost in 0.2.0 (the default fired silently for unifi-mcp from then until now). This DF closes the residual and proposes the SPEC clarification that prevents the recurrence.

## DF-005 — Homelab profile collides with LLM-DocKit on runbooks path AND `/new-homelab-project` does not populate new repo's HANDOFF *Open work* from brainstorm artefact

- Source: pi-fleet (0.1.1, 2026-05-08) — first homelab-profile project scaffolded via `integrations/dockit/new-homelab-project.sh` end-to-end. **Honesty note**: this DF was filed by an arbiter session in `home-infra` with multi-repo context, after a Codex audit of pi-fleet 0.1.1 surfaced both gaps in one pass. Both findings are anchored in `pi-fleet@a3eaf8d` + `home-infra-protocol/integrations/dockit/templates/infra.contract.yml` line 34 + `LLM-DocKit/docs/STRUCTURE.md` lines 23/51/53 (verifiable evidence).
- Date observed: 2026-05-08
- Category: process, usability
- Status: open
- Related: LLM-DocKit DF-035 (template-residue — same scaffold step leaves four other residue traces; the runbooks-path collision below is one specific instance of "scaffold and profile templates collide"), LLM-DocKit DF-034 (auto-orientation contract — a populated HANDOFF *Open work* is the foundation that contract assumes; gap (B) below means new homelab projects ship with that foundation as template stub).

### Observation

Two distinct gaps in `integrations/dockit/new-homelab-project.sh` and the homelab profile it applies, surfaced together by the same audit and sharing a single root cause: **the scaffold step does not propagate context from the project's brainstorm to the new repo's docs**.

**Gap (A) — runbooks path collision between homelab profile and LLM-DocKit scaffold.** The homelab profile's contract template at `integrations/dockit/templates/infra.contract.yml` line 34 declares a `runbooks:` block whose values resolve under `docs/runbooks/...`. LLM-DocKit's `docs/STRUCTURE.md` template (lines 23, 51, 53) documents `docs/operations/` as the runbooks directory and lists no `docs/runbooks/`. New homelab projects scaffolded via `/new-homelab-project` therefore inherit:

- A contract pointing at runbooks under `docs/runbooks/`.
- A `STRUCTURE.md` describing `docs/operations/` as where runbooks live.
- A scaffold that creates `docs/operations/` (DocKit default) but not `docs/runbooks/`.

The populate step in pi-fleet 0.1.1 created `docs/runbooks/` (per the contract) without removing `docs/operations/` or updating `STRUCTURE.md`. Result: pi-fleet 0.1.1 had both directories, two conflicting conventions in tree, and a `STRUCTURE.md` referencing the wrong one. The collision is silently inheritable; every new homelab project will hit the same fork in the road.

**Gap (B) — `/new-homelab-project` orchestrator does not populate the new repo's `docs/llm/HANDOFF.md` *Open work* block from the project's brainstorm artefact.** The orchestrator script (`integrations/dockit/new-homelab-project.sh`) currently:

1. Calls `LLM-DocKit/scripts/dockit-init-project.sh` (creates scaffold).
2. Calls `home-infra-protocol/integrations/dockit/apply-profile.sh` (applies homelab profile: AGENTS.md, CLAUDE.md symlink, `infra.contract.yml` template, PROJECT_CHECKLIST).
3. (Optional) Calls `gh repo create` + push.
4. Suggests a row for `home-infra/docs/PROJECTS.md` (the calling skill commits this).

**It does NOT touch the new repo's `docs/llm/HANDOFF.md` *Open work* block.** That block stays as LLM-DocKit's generic template stub (`Initial scaffold. No application code yet.` etc.) even when the project was born from a structured brainstorm artefact in ForgeOS — pi-fleet's brainstorm `forgeos/docs/brainstorms/2026-05-08-pi-fleet-multi-role-resilient-fleet.md` contains §6 (canonical content for HANDOFF *Open work*) and §11 (the 5 inputs the skill was already given). The orchestrator already had the inputs; it lacked a step.

Concrete failure observed in pi-fleet on 2026-05-08: a fresh Claude Code session opening pi-fleet ran `/brief` and correctly identified the inconsistency before any human did — the local HANDOFF *Open work* was a template stub while the concrete plan lived in `forgeos/docs/brainstorms/...md` §6 and `home-infra/docs/PROJECTS.md`. The `/brief` output flagged the staleness explicitly: *"Inconsistencia a señalar: docs/llm/HANDOFF.md dice 'Initial scaffold. No application code yet' con Next Steps genéricos de plantilla, mientras que home-infra/docs/PROJECTS.md ya tiene un plan concreto."* The first commit of the populate-docs session in pi-fleet was therefore "fix something the scaffold should have done" — a recurring tax that every new homelab project will pay until the orchestrator absorbs the step.

Both gaps share a common root cause and a common consumer impact: a fresh `/brief` in the new homelab project cannot orient locally on day one. For (A) the orientation lands at a path that does not exist or coexists with a stale alternative; for (B) the orientation sees a template stub instead of the project's actual next concrete step. The auto-orientation contract that LLM-DocKit DF-034's option (a) checks (HANDOFF *Open work* exists, names valid paths) **passes** in pi-fleet 0.1.1 only because pi-fleet's populate-docs session did the orchestrator's job by hand. A skill whose contract requires *its caller to fix its output before the contract is satisfied* is the gap this DF attacks.

### Protocol implication

(A) and (B) are independently shippable; the recommendation is to address both in the same `*_PROPOSAL.md` because they share scope (homelab profile + orchestrator) and a single coordinated change is cheaper than two scattered ones.

**For (A) — runbooks path collision.** Three options:

(A1) **Bump LLM-DocKit's STRUCTURE.md template to use `docs/runbooks/` instead of `docs/operations/`.** Cross-repo touch (LLM-DocKit minor). `runbooks` is more semantically specific than `operations` (a runbook is a procedure with verifiable steps; "operations" is a category that admits non-runbook content). After the DocKit bump, the homelab profile's contract template stays as-is and the collision dissolves. **Prerequisite**: read-only sweep of LLM-DocKit downstream adopters (`plaud-mirror`, `tomatic`, `infra-portal`, `forgeos`, `home-infra-protocol` itself) for `docs/operations/` content with runbooks. Many likely exist (plaud-mirror has runbooks under `docs/operations/`); each adopter would need to either rename or accept ongoing dual convention. Highest blast radius, cleanest outcome.

(A2) **Update homelab profile's `templates/infra.contract.yml` to use `docs/operations/` paths instead of `docs/runbooks/`.** Lower-blast-radius (only this repo's profile changes); loses the semantic specificity of "runbook" but follows DocKit's existing convention. New homelab projects then ship with `docs/operations/` per DocKit and the contract points there.

(A3) **Document the collision in homelab profile's `INTEGRATION.md`.** *"This profile uses `docs/runbooks/` instead of DocKit's default `docs/operations/`. After scaffold + profile apply, edit `docs/STRUCTURE.md` to match."* Cheapest, but pushes the burden to every new project — same failure mode as today, just documented. Reject as a sufficient fix; acceptable only as interim before (A1) or (A2) ships.

Recommend (A1). Cross-coordinate with LLM-DocKit DF-035's option (b) (template edits) — both involve STRUCTURE.md and could ship in a single LLM-DocKit minor. (A2) is the fallback if cross-repo coordination is undesirable.

**For (B) — orchestrator does not populate HANDOFF *Open work*.** Three options:

(B1) **Pass the brainstorm path as a new input to `/new-homelab-project`.** Skill currently asks 5 questions (name, description, host, exposes-ui, github); add a 6th `--brainstorm <path>` (or "Path to brainstorm artefact in ForgeOS, optional"). When provided, the orchestrator reads §6 (or operator-named-section equivalent) and §11 of the brainstorm and writes a HANDOFF *Open work* block in the new repo before the final commit. When omitted, the orchestrator keeps current behaviour (template stub). Most direct fix. Risk: brainstorm format not stable enough — §6 today is operator convention, not a specified contract; skill needs a documented section name or a fallback ("if §6 is not present, look for *Brainstorm summary*; if neither, prompt operator inline").

(B2) **Standalone skill `/handoff-from-brainstorm`** that the operator invokes manually after `/new-homelab-project` finishes, before the first development session. Decouples from `/new-homelab-project` (which stays narrow on scaffold + GitHub + registry). Slightly more friction (two skill invocations instead of one) but cleaner separation of concerns. Pairs well with future ForgeOS automation that orchestrates Stage A → Stage B (brainstorm → handoff) as a single operator-journey step.

(B3) **Document the gap in the skill's prompt and operator-facing output.** *"Post-scaffold, populate `docs/llm/HANDOFF.md` *Open work* manually from the brainstorm artefact before opening a new development session."* Cheapest, no code change. Same problem as today (depends on operator/LLM discipline, not enforcement).

Recommend (B1) if the brainstorm format stabilises into a contract this DF can name (e.g., a `## §6` anchor or a YAML frontmatter `handoff_open_work:` section). Recommend (B2) if the brainstorm format varies per project. Reject (B3) as sufficient; acceptable only as interim.

### Implementation hints (deferred to PROPOSAL)

This DF carries enough scope (cross-repo coordination for A1, skill input contract change for B1, brainstorm format contract decision) that a `docs/HOMELAB_PROFILE_COLLISION_AND_POPULATE_PROPOSAL.md` is the right next artefact before any implementation session. Ship the PROPOSAL first, ship the implementation after.

Files the PROPOSAL should touch when authored:
  - `docs/HOMELAB_PROFILE_COLLISION_AND_POPULATE_PROPOSAL.md` (new): scope decisions for (A) and (B), chosen options, cross-repo touches, version bumps.
  - `integrations/dockit/templates/infra.contract.yml` (line 34): updated path per (A1)/(A2) decision.
  - `integrations/dockit/new-homelab-project.sh`: new orchestrator step per (B1) or (B2) decision; if (B1), add input parsing and brainstorm-section reader.
  - `integrations/dockit/skills/new-homelab-project/SKILL.md`: update questions + plan template per (B1) decision.
  - `integrations/dockit/INTEGRATION.md`: document the now-aligned runbooks convention; document the new HANDOFF *Open work* population step.
  - Cross-repo for (A1): `LLM-DocKit/docs/STRUCTURE.md` template, `LLM-DocKit/scripts/dockit-init-project.sh` if it materialises the runbooks dir at init.

Version bump: at least patch for the homelab profile change; coordinated minor with LLM-DocKit if (A1) is chosen.

Cross-repo touches required: (A1) requires LLM-DocKit minor + downstream adopter sweep. (B1) requires test against pi-fleet 0.2.0 brainstorm to confirm the orchestrator extracts the right §6 content. Halt and report drift; do **not** edit cross-repo from the implementing session — file local follow-ups per project.

### Mitigation in source projects

pi-fleet 0.1.1 → 0.2.0 cleanup (in flight as of 2026-05-08) addresses both symptoms locally:

- Gap (A): `docs/operations/` removed; convention unified under `docs/runbooks/` per the contract; STRUCTURE.md and LLM_START_HERE.md updated to match.
- Gap (B): HANDOFF *Open work* populated by hand in the populate-docs session from `forgeos/docs/brainstorms/2026-05-08-pi-fleet-multi-role-resilient-fleet.md` §6.

Both fixes are one-off, by hand, after the residue had already shipped to GitHub. The protocol-level cure proposed here is the same idea structurally enforced for every future homelab project. Without it, every new homelab project will pay the same tax pi-fleet paid on 2026-05-08 — and the cleanup quality depends on whether that project's first session has the multi-repo context to recognise the gaps as systemic rather than local. (See companion DF in LLM-DocKit DF-035 *Mitigation* section + `forgeos/docs/llm/HANDOFF.md` *Open work* item #8 for the cross-LLM protocol gap that today's exercise surfaced.)

## DF-006 — Operator-visible web service accepted a loopback URL and hid deployment/secrets intent

- Source: `home-infra` Hermes NAS activation (2026-05-09)
- Date observed: 2026-05-09
- Category: semantic-gap, process, security
- Status: implemented (0.4.0) — additive schema fields `exposure`, `secrets_source`, and `deployment.pattern` / `deployment.deviations` shipped; SPEC guidance now defines the literal-host validator rule. Adopter-side enforcement is implemented in `home-infra` as a local catalog auditor.
- Related: DF-001, DF-003, DF-004

### Observation

Hermes Agent was corrected on the NAS from a custom broken two-container
deployment to the official upstream Docker pattern. The follow-up catalog entry
then exposed a second bug class: `hermes-dashboard` was cataloged as
`interface: web` with `url: http://127.0.0.1:9119/`.

That value is true as an implementation backend on the NAS, but false as the
operator-visible portal URL. `infra-portal` correctly rendered what the catalog
declared; the protocol had no semantic field distinguishing "operator
canonical URL" from "proxy backend / host-local URL".

The same incident exposed two adjacent gaps:

- The earlier custom image + entrypoint override + split dashboard container
  was a deviation from upstream intent, but no catalog field forced that
  decision to be named.
- Hermes' runtime `.env` existed as a local file generated by the official
  entrypoint, but the catalog had no place to declare the intended external
  secret source. The protocol said "secrets are references", but not "secret
  bearing services should declare where those references live".

### Protocol implication

This is not a request to hardcode one homelab's stack into the public protocol.
The universal gap is intent/provenance:

1. A service needs an optional `exposure` block:
   - `visibility: operator | local | hidden`
   - `canonical: boolean`
   - `backend_url: optional string`
2. A service needs an optional `secrets_source` reference block. The protocol
   should require only `kind`; adopters may constrain the shape to Doppler,
   SOPS, 1Password, Vault, etc.
3. `deployment` should carry optional `pattern` and `deviations[]` so a service
   can say "this follows upstream Docker with no deviations" or document an
   intentional override.

Validator guidance:

- For `interface: web` and `exposure.visibility: operator`, validators SHOULD
  flag a literal loopback or private-IP host in `url` (`127.0.0.1`,
  `localhost`, `0.0.0.0`, RFC1918 literals).
- The predicate applies to the literal `url` host, not DNS resolution. A
  hostname like `service.example.internal` that resolves to a private LAN IP is
  a valid split-horizon pattern. A literal `10.0.0.220` in the operator-facing
  URL bypasses the naming/proxy contract and should fail.
- `backend_url` may be loopback/private; that is where implementation-local
  addresses belong.

Rejected overreach:

- Do not require Doppler universally.
- Do not require Caddy, UniFi, Cloudflare, or public DNS.
- Do not forbid entrypoint overrides or multi-container topologies
  universally; require deviations to be intentional and documented.

### Implementation

0.4.0 implements the additive protocol surface:

- `schemas/services.schema.json`: adds `exposure`, `secrets_source`,
  `deployment.pattern`, and `deployment.deviations`.
- `SPEC.md`: adds prose contracts for `exposure`, literal-host validation,
  `secrets_source`, and deployment deviations.
- `examples/home-infra/catalog/services.yml`: shows operator-visible
  `exposure` blocks, backend URLs, deployment patterns, and a generic
  `secrets_source` reference.

The real adopter profile remains in `home-infra`: canonical web URLs use
`https://*.lamanoriega.com/`, UniFi provides split-horizon DNS, edge-caddy
proxies backend URLs, and Doppler is the approved secret store.

## DF-007 — Homelab deploy checklist still assumes save/load instead of registry-first image transfer

- Source: `msgvault-lab` pre-F2 NAS deploy hardening (`f0ca20e`,
  `00cf145`, 2026-05-18)
- Date observed: 2026-05-18
- Category: process, usability
- Status: open
- Related: DF-005

### Observation

The homelab profile installs
`.claude/checklists/homelab-project.md` from
`integrations/dockit/checklists/PROJECT_CHECKLIST.md`. Its build and
image-transfer section still treats `docker save <image> | ssh <host>
docker load` as the normal path for moving first-party images to the
NAS.

That no longer matches the current homelab convention. `home-infra`
`docs/CONVENTIONS.md` *Docker Image Management* was updated on
2026-05-14 to prefer `registry.lamanoriega.com/<image>:<tag>` for
first-party images that have adopted the private-registry flow. The
save/load path is now fallback for services not yet migrated.

`msgvault-lab` F2 exposed the drift before deploy: its brief had to
instruct the operator to mark the save/load checklist item N/A and use
registry push/pull instead. That local mitigation is correct for
`msgvault-lab`, but it does not fix the reusable profile. Every new
homelab project that receives this checklist can inherit stale transfer
instructions.

### Protocol implication

The reusable homelab profile should delegate image-transfer policy to
the current `home-infra` convention and express registry-first as the
primary path for first-party images. `docker save | ssh docker load`
should remain available as an explicit fallback for services not yet
migrated to the private registry.

Because the profile checklist is copied into downstream projects at
scaffold/profile-apply time, stale operational instructions propagate
silently. This is a profile-maintenance issue, not a `msgvault-lab`
runtime issue.

### Implementation hints (when accepted)

Files to touch:
  - `integrations/dockit/checklists/PROJECT_CHECKLIST.md`: rewrite the
    build/image-transfer section so registry push/pull is primary for
    first-party images and save/load is explicitly fallback.
  - `integrations/dockit/INTEGRATION.md`: state that the profile
    checklist follows `home-infra/docs/CONVENTIONS.md` for current
    image-transfer policy.
  - `docs/DOWNSTREAM_FEEDBACK.md`: update DF-007 status when the
    profile checklist change ships.

Version bump: patch.

Cross-repo touches required: read-only check of
`~/src/home-infra/docs/CONVENTIONS.md`; no `home-infra` edit unless the
convention itself changes.

### Mitigation in source project

`msgvault-lab@f0ca20e` and `msgvault-lab@00cf145` document the F2
workaround: mark the stale save/load checklist item N/A and use the
registry-first flow for the NAS image.

## DF-008 — Development previews need typed catalog semantics distinct from production services

- Source: `msgvault-panel` v0.4.0 dev preview +
  `home-infra/catalog/services.yml` `msgvault-panel-dev` +
  `infra-portal` 0.10.0
- Date observed: 2026-05-24
- Category: field-gap, semantic-gap, usability
- Status: implemented (0.5.0) - schema, SPEC, proposal, sanitized example,
  and consumer support matrix shipped. `Service.environment` is now a closed
  `production | development` enum in `schemas/services.schema.json`; SPEC.md
  defines the default, orthogonality, private-boundary rule, no-evidence rule,
  and dormant-not-down consumer semantics. `infra-portal` 0.11.0 is the first
  recorded consumer.
- Related: DF-003, DF-006

### Observation

`msgvault-panel` needed to be opened from infra-portal while still running
manually on `dev-vm`, before NAS deployment. The current catalog can express
that the service is operator-visible (`exposure.visibility: operator`) and that
its category is `data`, but it cannot express that the entry is a development
preview rather than deployed production reality.

The initial stopgap used a free-form `development` tag and an HTTP health probe
against `http://dev.lamanoriega.com:8788/api/health`. That made the tile
visible, but it overloaded conventions and produced a false incident whenever
the manual preview was stopped. For a development preview, "down" often means
"dormant"; for a production service, "down" means degraded runtime. Those are
different states, but the protocol has no typed field for the difference.

Using `category: development` would be the wrong cure: `category` is the
service's domain taxonomy (`data`, `network`, `media`, etc.), not lifecycle or
environment. `visibility` is also the wrong axis: a development preview can
still be operator-visible while remaining non-production.

### Protocol implication

Add an optional `Service.environment` field with the initial recommended values
`production | development`, defaulting to `production` for backward
compatibility. Do not add `staging`, `preview`, `experimental`, or other values
until a real adopter needs them. The field is orthogonal to:

- `category`: what kind of service this is.
- `interface`: how a consumer opens or copies it.
- `exposure.visibility`: who should be able to reach it.
- deployment lifecycle states: how far a production deployment has progressed.

Semantics for `environment: development`:

- It is not operational deployment evidence and MUST NOT be used as a claim
  that the project is deployed to its target host.
- It does not update `PROJECTS.md` as production reality, though it may be
  documented as temporary development visibility.
- It does not support a protocol compliance claim until a real consumer reads
  and renders the field.
- It MUST remain inside the operator/private boundary. A portal link to a
  development preview must not imply public internet exposure.

Consumer contract for infra-portal:

- Render development entries with an explicit DEV treatment (badge, grouping,
  or equivalent), not just a free-form tag.
- Treat development health as informational. A live preview may show healthy,
  but a stopped preview should render neutral/dormant rather than production
  down.
- Keep production service health semantics unchanged.

Anti-rot must have an enforcer, not just passive YAML. A future proposal should
choose one of:

- Add `owner`, `last_confirmed`, and optionally `expires_at` metadata, then
  have infra-portal grey or warn on stale development entries.
- Add a `home-infra` catalog audit/check that warns or fails when development
  entries pass their freshness window.

Follow-up: DF-009 implemented the anti-rot mechanism in 0.7.0. The accepted
shape rejects manual `last_confirmed` and uses `preview.purpose`,
`preview.expires_at`, `project_id`, and `state_policy`.

### Implementation hints (when accepted)

Files to touch:
  - `docs/DEVELOPMENT_ENVIRONMENT_PROPOSAL.md` (new): specify
    `Service.environment`, no-evidence semantics, security boundary,
    infra-portal render/health contract, and anti-rot enforcement choice.
  - `schemas/services.schema.json`: add optional `environment` with recommended
    values `production | development` and default `production`.
  - `SPEC.md`: document `environment`, its orthogonality to `category`,
    `visibility`, and deployment lifecycle, and the no-evidence rule.
  - `examples/home-infra/catalog/services.yml`: include one sanitized
    development preview example.
  - `docs/DOWNSTREAM_FEEDBACK.md`: update DF-008 status when the proposal or
    implementation ships.

Version bump: minor for the schema/SPEC implementation. A proposal-only filing
is patch.

Cross-repo touches required: coordinate with `infra-portal` for render and
health semantics before claiming support; migrate `home-infra` catalog entries
from the stopgap convention to `environment: development` only after the
consumer supports the field.

### Mitigation in source project

`home-infra` originally used an explicit stopgap for `msgvault-panel-dev`:
`name: DEV - msgvault-panel`, `category: data`, `tags: [development, ...]`,
`exposure.canonical: false`, and `status.type: none`. After
`infra-portal` 0.11.0 shipped consumer support, `home-infra` migrated the entry
to `name: msgvault-panel` plus `environment: development` in commit `1c2d276`.

## DF-009 — Development previews need anti-rot metadata and checks

- Source: `msgvault-panel` dev preview after DF-008 implementation +
  `home-infra/catalog/services.yml` `msgvault-panel-dev` +
  `home-infra/scripts/audit-catalog.py`
- Date observed: 2026-05-25
- Category: drift-control, validator-gap, lifecycle-hygiene
- Status: implemented (0.7.0)
- Related: DF-006, DF-008

### Observation

DF-008 correctly added typed `Service.environment` semantics and the first
consumer implementation maps unavailable development previews to `dormant`
instead of production `down`. The first real adopter then exposed the follow-up
gap that DF-008 intentionally deferred: nothing in the protocol gives a
development preview an owner, a freshness window, or an expiry rule.

The private `home-infra` profile now has a local stopgap: its catalog auditor
loads this protocol's `schemas/services.schema.json`, rejects invalid
`environment` values, and warns when an operator-visible development preview
uses an HTTP URL marked by the structured `http-stopgap` tag. That is useful
profile enforcement, but it is not a reusable protocol field. A future protocol
extension should define the portable anti-rot shape instead of letting each
profile invent incompatible tags or prose conventions.

### Protocol implication

Home Infra Protocol 0.7.0 implements the anti-rot extension without changing
the meaning of `Service.environment` and without requiring every project to
keep a development runtime alive.

Accepted shape:

```yaml
project_id: example-panel
environment: development
preview:
  purpose: Validate UI changes before the next production release.
  expires_at: "2026-07-15T00:00:00Z"
state_policy: isolated
```

Key decisions:

- `project_id` groups multiple runtimes of the same project. It is optional for
  production-only projects and expected when production and development
  runtimes coexist.
- `preview` is the metadata block. `preview.purpose` and
  `preview.expires_at` express human intent. `expires_at` is RFC3339 UTC.
- `last_confirmed` is rejected. Freshness comes from live probes or status
  snapshots, not hand-maintained dates.
- `state_policy` declares side-effect ownership:
  `none | read_only | isolated | production_write`.
- `production_write` in development is a strong warning and should require
  reviewed justification.
- Transport exceptions such as temporary HTTP previews remain adopter-profile
  policy unless a future real adopter needs a portable field.
- In 0.7.x these checks are warnings, not schema failures, because
  `environment: development` was already valid in 0.5.x and 0.6.x.

Cross-repo touches required: coordinate with `home-infra` so
`scripts/audit-catalog.py` can consume the accepted metadata, then coordinate
with `infra-portal` if the portal should render stale/expired development
previews differently.

## DF-010 — Project-owned sync and telemetry loops need a shared status contract

- Source: `msgvault-lab` 0.22.0 status publisher and verify-cache loop,
  `forumvault-lab` 0.13.1 scheduler/status snapshot, `plaud-mirror` 0.9.3
  sync state, `home-infra` host-capacity proposal, future Telegram archive work
- Date observed: 2026-06-18
- Category: field-gap, semantic-gap
- Status: implemented (0.6.0)
- Related: DF-003, DF-008, DF-009

### Observation

Multiple projects now need the same pattern:

1. A project-owned loop synchronizes or observes runtime state.
2. The project publishes a sanitized machine-readable status snapshot.
3. Infra Portal displays that state.
4. Hermes or another agent may alert when the state is stale or severe.

Without a protocol contract, each project invents its own status shape and
freshness semantics. That creates the same consumer-drift risk that earlier
DFs exposed for `interface`, TCP probes, deployment evidence, and development
previews.

Two distinct loop families appeared during the design discussion:

- Source sync: local state should keep up with an external authority such as
  Gmail, Telegram, Plaud, or a forum.
- Telemetry publishing: local state is observed and published, such as host
  disk pressure. There is no external source of truth; stale means the
  collector stopped publishing.

Collapsing both into one loose "job" concept would lose the distinction. A
sync job needs `source`; a telemetry job must not declare one.

### Protocol implication

Protocol 0.6.0 implements the shared contract:

- `schemas/status-snapshot.schema.json`: canonical Telemetry Source output.
- `docs/STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md`: prose contract for condition,
  severity, checks, display-only summary, and consumer-derived freshness.
- `schemas/project-contract.schema.json`: additive `sync_jobs[]` and
  `telemetry_jobs[]`.
- `docs/SYNC_JOB_CONTRACT_PROPOSAL.md`: schedule modes, `stale_after`
  semantics, sync-vs-telemetry split, and consumer responsibilities.
- `examples/project/infra.contract.yml`: sanitized sync and telemetry examples.

Key invariant: the producer writes `observed_at`; the declaration owns
`stale_after`; consumers derive freshness by joining both. A dead producer must
not keep claiming `fresh`.

### Mitigation in source projects

Before 0.6.0, `msgvault-lab` and `forumvault-lab` already published local
status snapshots with project-specific shapes. Those remain valid project
implementations, but future adoption should converge on the shared snapshot
shape and project-contract declarations.

## DF-011 — Operator services need provider-neutral authentication placement

- Source: `home-infra` 0.4.3 + deployed `infra-portal` 0.16.3
- Date observed: 2026-07-12
- Category: field-gap
- Status: implemented (0.8.0) — additive schema, SPEC semantics, sanitized
  examples, and focused regression tests shipped from the separately accepted
  `docs/AUTHENTICATION_PLACEMENT_PROPOSAL.md`
- Related: DF-006, DF-009

### Observation

Home Infra needs to record whether an operator-facing service places
authentication in the application, at the reverse proxy, or nowhere. The first
real producer incubated `exposure.authentication.mode` across its catalog, and
Infra Portal became a real consumer that renders the mode while stripping
private policy before browser egress.

The incubation also established a necessary boundary. Home Infra owns
expectations, deadlines, waivers, provider choice, and catalog gates. Infra
Portal may derive a browser-safe assessment, but that state is consumer output.
Neither belongs in the portable declaration. The protocol currently has no
field for the smaller neutral fact shared by both systems.

Evidence at filing:

- `home-infra` 0.4.3 commit
  `3f6b6ad78b15d851e5466222b88d1d534cd69c39` declares and validates the
  placement mode.
- `infra-portal` 0.16.4 commit
  `481569bee11b3fe298127043926050057f0701a1` ingests it and uses strict
  browser DTOs; production 0.16.3 proves the consumer path live.

### Protocol implication

Accept the provider-neutral optional declaration:

```yaml
exposure:
  authentication:
    mode: none | application | proxy
```

The field declares intended placement, not evidence that authentication works.
The protocol must not absorb Home Infra expectations/waivers, provider names,
consumer assessments, or action-plane policy.

### Implementation hints

Files to touch:

- `schemas/services.schema.json`: additive optional object and closed mode enum.
- `SPEC.md`: placement semantics and intent-not-proof boundary.
- `examples/home-infra/catalog/services.yml`: sanitized examples for all modes.
- `docs/AUTHENTICATION_PLACEMENT_PROPOSAL.md`: verify acceptance criteria.
- `docs/DOWNSTREAM_FEEDBACK.md`: mark DF-011 implemented after those changes.

Version bump: minor (`0.8.0`).

Cross-repo touches required: read-only validation against `home-infra` and
`infra-portal`; no downstream writes from the protocol implementation session.

## DF-012 — Stable check identifiers need optional operator-facing labels

- Source: `infra-portal` 0.17.0 design review + `forumvault-lab` 0.15.8
- Date observed: 2026-07-13
- Category: usability
- Status: implemented (0.9.0) — optional `checks[].label`, identity/display
  semantics, producer adoption, consumer support, and regression tests
- Related: DF-010

### Observation

The first project-card consumer rendered stable status check names such as
`last-sync` and `mcp.tools_list` directly. Those identifiers are useful for
machine joins but poor operator copy. ForumVault also published the display
summary `Last run error_class=none`, exposing an implementation field even
though the protocol already described summary as human-facing text.

The portal could maintain project-specific label maps, but that would couple a
generic consumer to producer ids. Parsing or rewriting summaries would violate
the display-only contract.

### Protocol implication

Keep required `checks[].name` as stable machine identity and add optional
`checks[].label` for concise human-facing copy. Clarify that label and summary
are never parsed for logic and that summaries should avoid internal field names
or `key=value` expressions as primary UI copy.

### Implementation evidence

- Protocol 0.9.0 schema, SPEC, D-004, and tests define the additive field.
- ForumVault 0.15.9 publishes labels and plain-language result summaries.
- Infra Portal 0.17.0 preserves the label through strict egress, displays it,
  and uses a cosmetic humanized-name fallback for older producers.

## DF-013 — Host recovery can restore the backend while required service surfaces remain broken

- Source: `home-infra` 0.6.0 (`51d1bbd590ae`) + `pi-fleet` 0.4.0
  (`1dc56e67d628`) + deployed Infra Portal 0.19.2
- Date observed: 2026-07-15
- Category: field-gap, process, usability
- Status: open
- Related: DF-003, DF-006

### Observation

A replacement host restored the application backend, physical controller,
persistent state, and its primary machine consumer. The canonical operator URL
and Infra Portal nevertheless remained down because a local TLS proxy from the
previous topology had not been restored. The upstream ingress still expected
HTTPS and a specific TLS server name, so the canonical route returned 502.

Checking only the host-local backend would have declared a partial recovery
complete. Changing the Portal probe to the direct HTTP backend would have made
the dashboard green while hiding both the broken canonical route and a
transport-security regression. Completion required restoring the local TLS
hop, configuring the ingress TLS name, verifying the machine consumer, testing
the canonical URL, reconciling published source of truth, and observing the
service as healthy from the Portal.

### Protocol implication

The existing completion rule correctly requires source-of-truth and relevant
consumers to agree, but it does not provide a neutral machine-readable way to
declare all required acceptance surfaces or their observation points. One
private adopter now incubates:

- required acceptance surfaces with stable ids, check kinds, observation
  points, expected results, and required/optional status;
- explicit `complete`, `incomplete`, and `rolled_back` operation outcomes;
- security-parity checks that distinguish transport encryption from peer
  verification;
- a closure rule that fails when any required target, integration, operator,
  observer, or publication surface fails.

Do not promote that private shape yet. A second real proxied-service recovery
must exercise it first so the protocol can distinguish reusable concepts from
host-specific workflow. Any future proposal must remain implementation-neutral
and sanitized. Private addresses, MACs, backup locations, secret references,
proxy products, role commands, and operator policy do not belong in the public
contract.

### Promotion gate

Before moving DF-013 to `accepted`:

1. Run the same all-surface closure model for one other service with canonical
   ingress and at least one independent consumer.
2. Record which acceptance fields and observation-point names survive both
   cases unchanged.
3. Define how security regression is represented without claiming that an
   acceptance declaration proves runtime protection.
4. Produce a separate sanitized proposal with compatibility and consumer
   honesty rules; schema, SPEC, examples, and validators remain untouched until
   that proposal is accepted.

### Mitigation in source projects

Home Infra 0.6.0 owns the private recovery graph, declarative ingress, pinned
role dependency, preflight, and all-surface closure. pi-fleet 0.4.0 owns target
deploy, encrypted backup, exact-host restore, rollback, and physical-device
gates. The canonical HTTPS probe remains authoritative; Infra Portal required
no recovery-specific code.
