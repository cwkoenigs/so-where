# Where design

Where turns the conclusion of an investigation into a small, connected record that can be trusted in proportion to its evidence.

## The daily experience

The first screen answers: what needs another look, what is already understood, and where do I go?
Search spans titles, reasons, locations, old locations in history, and evidence. Cards remain short;
selecting one expands the serving chain, original evidence, links, and curation actions.

The sample deliberately includes an active website, its source repo and runtime host, a misleading
archive, a ready-to-curate investigation note, a stale preview, and an unresolved background job.
These are different knowledge states, not uptime indicators.

## Why a manifest

A central folder gives the user one entry point. A canonical JSON manifest gives the helper
predictable mutations and validation. Generated Markdown gives people plain files they can read
in a repository or Obsidian. A generated HTML view gives the user condensed cards and search.
Sources stay owned by their projects; the map stores pointers and the distilled answer.

This is one index with several views, not a second copy of every project's documentation.

## What a record means

Each record has an immutable id, purpose, reason, owner, locations, evidence, a review window,
and links to other records. A service also identifies its address, host, deployment, source,
subdirectory, revision, runtime root, environment, and entry point. This connects a familiar
name to the actual execution location.

Knowledge state (`draft`, `curated`, `retired`) is separate from freshness (`current`, `stale`).
Curated knowledge can become stale. Drafts preserve useful partial answers. A lack of evidence
is an explicit next task rather than a guessed connection.

## Capture and promotion

The agent distills the answer at the end of an investigation. A capture enters the inbox. A
service cannot be promoted until route, build/source, and runtime observations agree on one
immutable deployment and the open questions are resolved. Promotion is acceptance into the map,
with no release operation attached to it. The oldest required observation determines freshness.

The helper validates shape, completeness, matching release ids, and dates. It cannot prove a
text observation is true. The skill must inspect real evidence through the available project
tools before creating real claims. An HTTP 200 alone cannot establish a repository or revision.

## Changes without losing the trail

Amendment retains the previous record snapshot and returns the current record to draft.
Relocation changes a pointer, retains its former location in history, and asks for verification.
Actual file moves or runtime deployments belong to the source project workflow. Once complete,
their results can be recorded here. Retirement leaves the record and its incoming links intact.

The helper serializes writes with a local file lock, validates before saving, and atomically
replaces the manifest. It retains one immediate backup; events and prior snapshots provide
lineage. Put the map in Git for long-term versioning, diffs, and rollback. Generated views are
rebuildable if a view write is interrupted after the manifest has saved.

## Daily loop and curation ownership

At day start, open the map and look at stale and draft records. Inspect only what matters for the
current task. At session end, distill a resolved investigation into an existing or new draft.
Review it when evidence is sufficient. Repeat when routing, hosting, deployment roots, or
repository ownership changes. A rebuild never counts as a fresh observation.

No scheduler or background scanner is installed. A future scheduled check should be explicitly
scoped to a known set of services and should notify only when evidence or routing changes matter.

## Connections and distribution

Typed relations describe the operational world. Wiki links present the same graph in Obsidian.
A project pointer identifies the map location. External standards, team captures, and source
sessions remain external references. A future hosted search/MCP adapter could expose the same
manifest, while the skill/helper could ship in the versioned team package; neither is needed to
run this sample. Those adapters are a possible extension, not delivered infrastructure.

## Boundaries of this sample

The server is a single-user local editor for macOS/Linux. It uses a per-process mutation token,
Host/Origin checks, revision checks, and bounded JSON requests. It does not provide account-based
access, multi-user synchronization, Git conflict resolution, monitoring, provider-specific
discovery, or a physical file-move engine. Opening the HTML file is a read-only experience.

The portable map does not require a cloud service. When two machines use it, each location needs
a machine label; a shared absolute checkout path must not be assumed valid on both machines.
