# Map contract

The manifest is a portable index of claims and pointers, with one record per independently understood thing.

`registry.json` contains `schema_version: 1`, `demo` (boolean), `revision` (integer), `records`
(array), and `events` (array). No external service or package is required. Keep this directory in
Git if versioned history or cross-machine sharing is needed. Resolve relative evidence references
against the registry directory. JSON is canonical; generated files are disposable views.

## Record

| Field | Meaning |
| --- | --- |
| `id` | Immutable `k-` plus six hex digits; helper assigns on capture |
| `title`, `summary`, `why`, `owner` | Human-readable subject, answer, reason, accountable curator |
| `kind` | `service`, `repository`, `host`, or `document` |
| `state` | `draft`, `curated`, or `retired`; independent of runtime health |
| `locations` | Array of `{label, uri}`; first entry is the primary location |
| `runtime` | Service chain object; empty object for other kinds |
| `tags` | Searchable strings |
| `evidence` | Array of observation objects described below |
| `uncertainties` | Concrete unresolved questions; blocks promotion |
| `verified_at` | Oldest required observation used on promotion, or null |
| `review_after_days` | Positive integer defining when observations become stale |
| `relations` | Array of `{type, to}`; `to` is an existing record id |
| `history` | Prior snapshots and mutation reasons; helper maintains |

Service runtime fields: `address`, `host`, `deployment`, `repo`, `subdirectory`, `revision`,
`root`, `entrypoint`, and `environment`. Use a host/platform project identifier in `host` and an
immutable deployment/release id in `deployment`. Use `/` or `.` explicitly where appropriate.
The sample stores these in one record to make a serving chain easy to read; host/repo records add
shared context through relations. Local checkout paths belong in locations, with a machine label.

## Evidence

An observation contains `scope`, `observed_at` (ISO 8601 with timezone), `ref`, `summary`,
`deployment` (service evidence only), and `sample` (boolean).

Service promotion requires three scopes: `route`, `source`, `runtime`. Every required observation
must name the record's current immutable deployment. Other records require `identity` evidence.
All required scopes must have evidence no older than the record's review period. Promotion uses
the latest observation for each scope and then the oldest timestamp across those scopes. Future
timestamps fail validation. Unknown fields fail validation to catch silent misspellings.

Evidence sources remain authoritative: provider project settings, live routing, deployed revision,
process/container launch configuration, and original decision records. The helper validates
structure and matching deployment ids, not the truth of those sources. Curators must inspect them.
`sample: true` is prohibited when the registry has `demo: false`.

## Changes and connections

`capture` adds a draft. `amend` replaces one record's content, retains the previous snapshot, and
returns it to draft. `promote` accepts evidence-backed knowledge. `link` adds a typed relationship.
`relocate` updates a matching URI, records the old URI, and returns the record to draft because
its location claim needs verification. `retire` retains the record and incoming links.

Relation types: `runs_on`, `built_from`, `documents`, `depends_on`, `related_to`, `supersedes`.
Retired targets stay visible and labeled. Aliases are old URIs retained in history, searchable in
the dashboard. Normal links connect current records; `supersedes` connects separate historical
subjects. Renaming a card's title does not require a new id.

An operational map can link to a team standard served through an MCP or installed package.
That does not make the map the owner of that standard or a deployment controller.
