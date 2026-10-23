---
name: so-where
description: Maintain a curated map of what runs where and why. Use for “what serves this website”, “what is on this server”, “save this untangling”, daily system orientation, evidence-backed project links, and updating location references. Produces a local manifest and compact cards without moving source material.
user-invocable: true
---

# Where

Turn a resolved investigation into a durable, evidence-backed answer that survives the session.
Keep the map in a user-chosen directory. Keep code, deployment configuration, and original notes
where they belong. Owner: the person curating that map.

## Locate the map

Use the map named in the current request or a project-owned `.where.json` containing
`{"registry": "<relative-or-absolute-path-to-registry.json>"}`. Resolve a relative path against
the pointer file. Do not scan unrelated private directories. If no map is configured, use a
`where/` directory in the current workspace, tell the user its location, and create an empty
registry using the helper's `init` command. Never treat a sample registry as a real inventory.

## Choose the operation

- **Orient:** Read `registry.json`. Answer with the relevant compact records: purpose, primary
  location, serving chain, confidence date, unresolved questions, and a next action. Separate
  curated knowledge from live observations. The daily view highlights stale records and drafts.
- **Untangle:** Trace the address or process actually in use through routing, hosting/project,
  deployment, repository, subdirectory, revision, and runtime root/entry point. Use existing
  project tools for read-only inspection. A matching folder name, successful build, or ready
  deployment alone does not identify the code serving users. If access is missing, preserve the
  exact gap and create a draft with an actionable next check.
- **Capture:** Distill only the reusable answer and the reason it was confusing. Reference
  original evidence, including the source session if accessible; do not copy whole transcripts.
  Add a draft even when some facts are unknown. Use stable ids and search before adding duplicates.
- **Promote:** Accept a draft into curated knowledge once evidence supports the assertion and
  explicit uncertainties are resolved. This changes the map only. For a service, require route,
  source/build, and runtime evidence for the same observed deployment. Show the compact result.
- **Connect:** Add typed relationships between existing ids, such as `runs_on`, `built_from`,
  `documents`, or `depends_on`. Preserve external source links. Export linked Markdown for an
  Obsidian vault; do not assume an installed Obsidian vault or modify one without a destination.
- **Relocate:** Update a location pointer only when a new location is established; retain the old
  URI, reason, and date. If the user actually requests a filesystem move or deployment promotion,
  handle that as a separate scoped operation, verify its result, then amend this map.
- **Amend or retire:** Keep the id. An amendment returns a record to draft and retains the prior
  snapshot in its history. Retire obsolete entries rather than silently deleting lineage.

## Write records

Read [references/contract.md](references/contract.md) when creating or amending a record.
Use [references/where.py](references/where.py) for deterministic validation, mutations, and views;
run `python3 <skill-dir>/references/where.py --help` for commands. It uses only Python's standard
library. `references/dashboard.html` is its self-contained presentation template.

The JSON is canonical. Generated `START.md`, `index.html`, and `obsidian/` pages are views.
Capture needs a record JSON file; the helper assigns an id and forces draft status. Evidence is
an attributed observation, with scope, time, source reference, and the fact it supports. Redact
credentials; store environment variable names or secret-store references, never values.

Record a fact as verified only after observing evidence that supports it. A review, rebuild,
promotion, or relocation must not reset observation timestamps. The helper checks record shape
and evidence coverage; it cannot authenticate evidence or inspect a deployment on its own.
Label disputed evidence and keep the record in draft. Link the specific conflicting observations.

Use per-machine location labels for local checkouts. A repository is not a running service, a
checkout is not a deployment, and one repository may produce multiple deployed services.
For multi-server inventories, represent each independently deployed service as its own record.

## Repeatable daily and session workflow

At day start, build the map, then show what needs attention and the serving chains relevant to
today's work. Do not perform broad network/server scans or create a recurring schedule implicitly.
At the end of a resolved investigation, capture the outcome when requested; otherwise offer a
short capture. Amend an existing record if its subject is the same. Preserve dissent and gaps.

Run `check` after changes and `build` to refresh the cards and linked Markdown. The build does not
change verification dates. For real registries, set `demo` to `false`; the validator rejects sample
evidence. Keep generated Obsidian exports in a dedicated folder and edit the canonical JSON.

## Boundary and validation

This skill owns the operational map. `so-capture` owns reusable team gotchas/standards and their
publication workflow; link to those records when available rather than recreating that workflow.
Do not deploy, move repositories, change routing, publish records, or message people just because
the map describes those actions. Respect authorization for the actual requested operation.

Validate with the helper and realistic scenarios: an incomplete serving chain stays draft, a
stale observation stays stale after build, relocation preserves identity/history, and exports
resolve internal relationships. See the working sample's tests for an executable evaluation.
