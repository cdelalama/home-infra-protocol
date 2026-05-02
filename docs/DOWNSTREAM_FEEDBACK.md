<!-- doc-version: 0.2.0 -->
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
- Status: partially implemented (protocol 0.2.0) — protocol-side guardrail (b) shipped: SPEC.md *Consumer support for `interface`* matrix exposes which schema values which consumer supports per version, so adopters can no longer hit a silent stub. Consumer-side cure (a, TCP probe in `infra-portal`) tracked in that repo's HANDOFF *Pending work* item 1.
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
