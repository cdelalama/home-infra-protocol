<!-- doc-version: 0.19.0 -->
# Progress: first usable delivery record

Status: first source increment under review. This does not implement a Portal
view, a ForgeOS hook, a fleet migration, or actual delivery acceptance.

Progress lets a project explain its first usable outcome, outstanding criteria,
next actor/action, blockers and evidence-review date. Projects without a record
remain visible as undefined in an inventory-backed consumer. A first usable
release may be version 0.x; release numbers, commit counts and uptime are not
completion measures. Later releases do not extend the accepted first-release
scope or erase its historical delivery.

## Ownership and authority

Protocol owns this optional shape and its canonical validator. The project owns
its record and evidence. The infrastructure owner accepts adoption and the
published source binding, and applies its existing delivery rules. ForgeOS will
own creation/adoption orchestration; DocKit will link routine session upkeep.
Portal will render the owner's accepted, provenance-bound published projection.
These consumer integrations are subsequent increments, not delivered here.

The conventional project file is `infra.progress.json`. Its enclosing Git
revision and content digest belong to the acquisition envelope: do not put the
file's own commit hash inside itself. A collector must acquire a published
revision from an owner-approved source and keep that provenance alongside the
record. It must not treat a dirty local checkout as published state or infer
unpublished work from a remote-only observation.

References are non-executable data: project identity, repository-relative path,
full Git revision and exact anchor. They do not authorize fetching arbitrary
repositories, opening files, following URLs or running commands. The caller
resolves only approved project identities and verifies the referenced content.
Reference syntax does not prove that the source exists, says what the author
claims, or carries authentic operator authority.

## Record

`schemas/progress-record.schema.json` is a closed draft-2020-12 JSON Schema.
Unknown fields and contract/schema versions fail. Lists are bounded at 100
criteria/blockers and 20 evidence references per criterion. The canonical CLI
reads at most 262144 UTF-8 bytes and rejects duplicate keys/non-finite numbers.
All timestamps use UTC seconds: `YYYY-MM-DDTHH:MM:SSZ`.

| Field | Meaning |
| --- | --- |
| `project_id` | Existing project identity; never a branch, task or study identity. |
| `target` | `first-usable`, scope version, undefined/proposed/accepted state, outcome summary, pinned definition and attributed acceptance reference. |
| `criteria` | Stable IDs, display labels, pinned requirements, pending/verified project claims and dated evidence references. |
| `next_action` | One concrete action and actor, optionally joined to a criterion. |
| `blockers` | Independent operator-decision/input, external or technical dependencies. |
| `pause` | An explicitly declared pause with its source and date; never inferred from inactivity. |
| `reviewed_at` | Last meaningful check of evidence against this scoped outcome; not an arbitrary session or commit timestamp. |
| `last_activity_at` | Last relevant work observation, separately dated; not inferred from commits. |
| `delivery_claim` | Optional project declaration, requiring an actual source revision and receipt reference. It is not owner verification. |
| `effort` | Optional dated, attributed estimate for details; unknown is allowed and it is not a ranking score. |

Undefined scope has no invented outcome, acceptance, or criteria. Proposed scope
needs an outcome but cannot claim acceptance. Accepted scope requires at least
one criterion, pinned scope/requirement definitions and an attributed operator
decision addressing that exact first-use scope. Existing exact decisions may be
reused; loosely related conversation fragments do not manufacture acceptance.

All listed criteria are required for this target. Extra suggestions belong
outside the accepted first-release criteria. Labels and the outcome sentence are
operator-language summaries of the pinned definitions, not alternative scope
authority. They must remain faithful to those definitions. Wording/translation
clarifications are visible in Git and do not require repeated operator approval;
changing the actual accepted requirement does. Validators cannot prove that a
summary is faithful or distinguish semantic weakening from a wording edit.

A verified criterion claim needs its verification date and evidence references.
A pending criterion has no current verified result. Corrections may replace
current claims; source history and immutable owner delivery receipts survive.
A blocker or explicit pause can coexist with delivery history. A next action by
an agent does not mean every project dependency is resolved.

## Accepted-scope transitions

Use `--previous` with the **actual previously published record**, acquired by the
trusted caller. The validator cannot prove which file is that predecessor.

- Project/release identity must match; scope version cannot decrease.
- Keep accepted scope accepted; draft alternatives outside that accepted record.
- Adding/removing required criterion IDs or changing pinned requirement/scope
  definitions requires a greater scope version and a different attributed
  acceptance reference. A new reference's authenticity still needs owner review.
- Routine evidence/status changes, ordering and faithful display-copy updates
  do not require another operator click. Pure wording clarifications can retain
  the existing immutable accepted definition references.

Passing a transition check proves these mechanical conditions only. A caller
must always supply the previous published record when updating an adopted
record; omitting it yields shape-only validation, not transition acceptance.
No previous record exists for a genuine first adoption.

## Delivery and presentation

There is deliberately no `percent`, `score`, `ready`, `delivered`, health, or
consumer freshness field. A consumer must join delivery declarations to the
existing infrastructure-owner acceptance ledger and applicable real use evidence
at the delivered source revision. A declaration alone is shown as unverified.
A CLI/library needs its real use proof, not a fictional web deployment.
An all-verified criteria list does not itself certify delivery.

Preserve verified historical delivery even if current input is missing, stale,
invalid, paused or blocked. Current usability and readiness are separate facts.
Until the owner has set a freshness rule, show review dates/unknown rather than
inventing an expiry threshold. If publication fails, expose the failure and
retain attributed prior knowledge; do not replace projects with an empty list.

The first Portal view will show outcome, next missing criterion, next actor/action,
main blocker and review date. Full criteria/evidence and optional effort belong
in details. Display groups help browsing; they do not assign priorities. An
operator-dependent step cannot be labeled unblocked. Agents exhaust existing
applicable authorized routes before declaring an operator-only dependency.
Tasks/studies remain linked separately and never inflate the project count.

## Canonical validation

Use Python with the same `jsonschema` dependency as the existing protocol
validator. Do not copy this validator to ForgeOS or adopter repositories.

```sh
python3 scripts/validate-progress.py --record examples/progress/undefined.json
python3 scripts/validate-progress.py --record examples/progress/claimed.json \
  --previous examples/progress/pending.json
python3 -m unittest discover -s tests -p 'test_progress.py'
```

Exit 0 means valid shape/optional mechanical transition; exit 1 means invalid;
exit 2 means unavailable/malformed input. Output always reports authority and
delivery as `not_assessed`. The tool performs no network, evidence resolution,
record mutation or project execution. No fixture is real project acceptance.
The three example records use fictional identities, decisions, revisions and
receipts. They demonstrate undefined, pending and declared delivery only.

## Next implementation increments

1. Qualify this record and transition contract against real owner-scoped pilot
   projects. Missing scope remains undefined; no automatic acceptance backfill.
2. Add owner-approved acquisition/projection and a read-only Portal view with
   all inventory identities, error states and actual desktop/mobile checks.
3. Add ForgeOS creation/safe-adoption output and generic DocKit session upkeep.
4. Qualify the complete consumer matrix and actual access before shared delivery;
   roll out existing-project adoption separately. No authentication change,
   automatic prioritization, idle-project alert or fleet migration is implied.

## Transition review boundaries

An unchanged accepted scope retains both its scope version and its exact
acceptance reference. A changed scope needs a greater version and a different
acceptance decision identity (`project_id`, `path`, `anchor`); re-pinning the same
decision at another commit is insufficient. Pending accepted work must have a
next action, an explicit blocker or a pause. A delivery claim requires accepted
scope, but remains a claim.

Only owner-verified delivery freezes the historical first-usable scope in the
owner projection. An unverified project claim must not acquire that authority or
prevent its own correction. The collector must preserve the verified release
snapshot separately and refuse to reinterpret it as a later release. This
validator does not receive owner acceptance state and cannot enforce that gate.
Collectors must restrict reference resolution to allowed repository content;
syntactic validity does not authorize reading `.git` or private files.

Every delivery claim includes `scope_version`, equal to the current target.
A scope change must remove an obsolete claim or declare a claim for the new
scope; the owner independently checks the receipt and exact scope binding.
