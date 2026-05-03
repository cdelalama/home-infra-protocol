<!-- doc-version: 0.2.2 -->
# Proposal: `Service.interface` field for non-web services

> Status: **Draft — Ready for Implementation**
> Date: 2026-05-02
> Author: Claude Opus 4.7 (1M context) — drafted in a session with Carlos
>          while real-adopter (`tomatic`) work surfaced the gap
> Triggers: `docs/DOWNSTREAM_FEEDBACK.md` DF-001
> Implementer: a future session — this proposal is intentionally
>              self-contained so the next agent can read, decide, and ship
>              without needing the original conversation

---

## Problem statement

The protocol's `Service` record currently treats `url` as required and
unconstrained:

```json
"id": "...",
"name": "...",
"category": "...",
"url": "string, minLength 1"
```

Every service in `home-infra/catalog/services.yml` so far has been a service
with a navigable web UI (`https://grafana.lamanoriega.com/`,
`https://infra.lamanoriega.com/`, etc.). The single consumer
(`infra-portal`) hard-codes the assumption that `url` is openable in a
browser tab — `App.tsx:149` calls `window.open(svc.url, "_blank")` on every
service click.

When the first non-web service joined the catalog (`mosquitto` on
`zigbee.home.arpa:1883` for the Tomatic project, see
`docs/DOWNSTREAM_FEEDBACK.md` DF-001), the gap surfaced:

- `url: mqtt://10.0.0.139:1883` is schema-valid but not browser-navigable.
- The portal renders the service identically to a web service and offers a
  "open" button that fails silently when clicked.
- The category (`infra`) is not enough to distinguish: the portal itself
  is `category: infra` and *does* have a web UI.

The protocol needs an explicit way to express **what kind of interface a
service offers** so consumers can render and probe it correctly.

## Decision

Add a new optional field `interface` to `Service` with an open enum of values.

### Why this option (and not the alternatives)

DF-001 considered three options:

1. **Infer from URL scheme** (`http://`/`https://` ⇒ web; otherwise not).
   Rejected: implicit, brittle, fails for HTTP APIs without HTML
   (e.g. `unifi-mcp`'s `/mcp` endpoint).
2. **Binary `web_ui: bool` flag.** Rejected: not expressive enough for the
   topology view planned for `infra-portal` Phase 4+, where MQTT vs HTTP
   matters semantically (different edge styles, different probes).
3. **Enumerated `interface` field.** **Selected.** Most expressive,
   future-proof for the topology view, additive (does not break any
   existing consumer because the field is optional with a sensible default).

### Field shape

```yaml
interface: web        # one of: web | api | mqtt | tcp | ssh | none | other
```

- **Type:** string, with the protocol RECOMMENDING the enum
  `web | api | mqtt | tcp | ssh | none | other`. Schema does NOT enforce a
  closed enum at v0 — adopters and consumers can extend it. (See "Schema
  evolution rules" below.)
- **Optional:** field is OPTIONAL in the JSON Schema and project contract.
  Default value (when omitted) is `web` to preserve backward compatibility
  with the existing catalog.
- **Required:** if a service's `url` does NOT start with `http://` or
  `https://`, the SPEC MUST require `interface` to be set explicitly. This
  prevents the silent default from masking non-web services.

### Recommended values and their meaning

| Value | When to use | Consumer behaviour expectation |
|-------|-------------|--------------------------------|
| `web` | Service has a navigable HTML UI | Portal renders an "open" button → `window.open(url)` |
| `api` | HTTP/HTTPS but no HTML UI (REST/GraphQL/MCP/etc.) | Portal renders a "copy URL" button + endpoint label; status probe still works |
| `mqtt` | MQTT broker | Portal renders a connection-string copy + topology edge to clients |
| `tcp` | Raw TCP service (database, custom protocol) | Portal renders connection info; no clickable open |
| `ssh` | Operator-only SSH endpoint | Portal renders `ssh user@host` copy; no clickable open |
| `none` | Service has no operator interface (background daemon, sync agent) | Portal lists it but offers no interaction |
| `other` | Anything not in the recommended list | Portal renders connection info; specific behaviour undefined; future closed-enum candidates start here |

The list is recommended, not closed, because the GOVERNANCE rule says
fields are added only from real demand. Future values should be added by
filing a new DF entry that names the adopter and use case.

## Concrete changes required

A future session implementing this proposal should make exactly these edits.

### 1. `schemas/services.schema.json`

Add `interface` to the `properties` object of each service item:

```json
"interface": {
  "type": "string",
  "minLength": 1,
  "description": "Kind of interface the service exposes. Recommended values: web, api, mqtt, tcp, ssh, none, other. Optional; defaults to 'web' for backward compatibility. SHOULD be set explicitly when url does not start with http:// or https://."
}
```

The schema stays additive — `additionalProperties: true` already allows any
field, so consumers built against the older schema continue to work
without modification (they just ignore the new field).

### 2. `SPEC.md` — "Service" section

Update the Recommended fields list to include `interface`. Add a brief
paragraph after the field list:

> When `interface` is omitted, consumers MUST treat the service as having
> a web UI (`interface: web`) for backward compatibility with v0.1.5
> catalogs. When `url` does not start with `http://` or `https://`, the
> service MUST declare `interface` explicitly so consumers can render and
> probe it correctly.

Add a "Consumer support matrix" sub-section noting the current state of
support across known consumers:

```markdown
### Consumer support for `interface`

| Consumer | Version | Renders | Probes | Notes |
|----------|---------|---------|--------|-------|
| infra-portal | (pending) | (pending) | (pending) | See infra-portal HANDOFF for implementation |
```

This matrix is the cure for the class of bug in `DOWNSTREAM_FEEDBACK.md`
DF-002 (the schema accepts a value no consumer implements). Adopters
reading the SPEC see exactly what each consumer supports.

### 3. `examples/home-infra/catalog/services.yml`

Add one example per recommended value, sanitized:

```yaml
- id: example-web
  name: Example Web App
  category: tools
  url: https://example.test/
  interface: web

- id: example-api
  name: Example API
  category: tools
  url: https://example.test/api
  interface: api

- id: example-mqtt
  name: Example MQTT Broker
  category: infra
  url: mqtt://example.test:1883
  interface: mqtt
```

### 4. `examples/project/infra.contract.yml`

The project-contract example currently does not list `services` as objects
(it lists them as id strings). No change required here unless future
proposals expand the contract format.

### 5. `docs/PROJECT_CONTRACTS.md`

No structural change needed. Add a sentence in the "Suggested Fields" list
noting that a project's `services[].interface` follows the same enum as
the catalog's services, when the project lists service objects rather than
just ids.

### 6. `CHANGELOG.md`

Bump to `0.2.0` (NOT a patch) per `docs/VERSIONING_RULES.md`:

> ### Minor: Additive schema fields. New optional contract sections.

The version goes from `0.1.x` to `0.2.0` because this is the first additive
field added since the schema drafts in `0.1.0`.

## Migration path for existing catalogs

`home-infra/catalog/services.yml` (the single in-tree real adopter) needs
no change for backward compatibility — every existing entry has an
`http(s)://` URL, so the implicit default `interface: web` is correct.
The adopter is encouraged to add `interface` explicitly anyway as the
catalog grows, but it is NOT required for the migration to land.

The Mosquitto entry that triggered this proposal MUST be updated in the
same commit that lands this change in `home-infra` (not in this protocol
repo, since `home-infra` is private):

```yaml
- id: mosquitto
  name: Mosquitto MQTT
  category: infra
  url: mqtt://10.0.0.139:1883
  interface: mqtt              # <-- new
  ...
```

## Consumer (`infra-portal`) responsibilities

After this proposal lands:

1. **Read `interface`** from each service. If missing, treat as `web` for
   backward compatibility.
2. **Render the "open" affordance only when `interface == "web"`.** For
   `api`, `mqtt`, `tcp`, `ssh`, `other`, render a "copy connection string"
   button instead. For `none`, render the service in the list with no
   interaction at all.
3. **Use `interface` to drive the future topology view** in Phase 4+. MQTT
   edges look different from HTTP edges; SSH edges only render in the
   admin layer; etc.

These are tracked in `infra-portal`'s own HANDOFF as part of the
implementation work for this proposal, NOT in this repo.

## Schema evolution rules respected

- ✅ Additive: new optional field, no removals.
- ✅ Backward compatible: existing catalogs work unchanged because the
  default is `web` and every existing entry is web.
- ✅ Default behaviour is the safe one: a missing `interface` cannot
  break a consumer that doesn't read the field; a consumer that does
  read the field gets a sensible default.
- ⚠️ Naming: `interface` is a reserved word in TypeScript. Consumers
  that codegen types may need a synonym (`serviceInterface`, `iface`).
  The protocol uses `interface` as the wire name; consumers may alias
  it locally.

## Open questions for the implementing session

1. **Closed vs open enum at the schema level.** This proposal recommends
   keeping the schema string-typed (open) and listing recommended values
   in prose. Alternative: enforce the enum in the JSON Schema. The
   tradeoff is rigidity (closed) vs evolution friction (open). The
   GOVERNANCE rule "Schema evolution should be additive until a major
   version" leans open; lock at the major.

2. **Whether to also rename or alias `url`.** `url` is misleading for
   `interface: ssh` (where the value is `user@host:port`, not a URL). One
   option: keep `url` as the field name but loosen its semantic meaning
   to "primary endpoint string". Another option: add a sibling `endpoint`
   field. Resolving this is OUT OF SCOPE for this proposal — file a
   separate DF if it becomes a real problem.

3. **Whether `ServiceLinkKind` (in `infra-portal`'s Zod schema) should
   converge with `interface`.** Today the portal has
   `ServiceLinkKind = z.enum(["integration", "fallback", "docs", "admin", "other"])`
   which is *almost* the same idea but for `links[]`, not for the
   service itself. Worth a separate DF after this lands.

## Acceptance criteria for the implementation

- [ ] `schemas/services.schema.json` updated with `interface` (additive).
- [ ] `SPEC.md` Service section updated, Consumer support matrix added.
- [ ] `examples/home-infra/catalog/services.yml` shows three values.
- [ ] `docs/PROJECT_CONTRACTS.md` mentions the field once.
- [ ] `CHANGELOG.md` bumped to `0.2.0` with rationale.
- [ ] `docs/llm/HANDOFF.md` and `docs/llm/HISTORY.md` updated.
- [ ] `docs/DOWNSTREAM_FEEDBACK.md` DF-001 status moved to
      `implemented (0.2.0)`.
- [ ] All 25+ doc-version markers synced via `scripts/bump-version.sh 0.2.0`.
- [ ] `scripts/check-version-sync.sh` exits 0.
- [ ] Coordinated downstream change in `home-infra/catalog/services.yml`
      (Mosquitto entry gets `interface: mqtt`) lands in the same operator
      session, not in this repo. The protocol-side commit can land first;
      the home-infra commit follows.
- [ ] `infra-portal` issue/HANDOFF entry created so the consumer-side
      work (render and probe by interface kind) is tracked. The portal
      change is its own session, not bundled with this commit.

## Why this proposal is self-contained

The next session implementing this should not need the conversation that
produced it. Everything required is here:

- The motivation is in DF-001.
- The decision (option 3) is recorded above.
- The exact files to change are listed.
- The acceptance checklist is concrete.
- The migration path for the existing real catalog is named.
- The consumer-side responsibilities are listed but explicitly out of
  scope for this commit.

If anything is unclear, the next session should pause and ask — per the
protocol's existing "if unsure, ask" rule.
