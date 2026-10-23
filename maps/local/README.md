# Real map of the local Where website

This map records the real repository, serving root, and verified local process for this implementation.

Start at [the daily index](START.md), [the interactive file view](index.html), or
[the optional linked Markdown index](obsidian/Where.md). The canonical data is [registry.json](registry.json).
The repository's `.where.json` points here.

## The serving chain

`http://127.0.0.1:8765/` → Python helper in `so-where/references/` → `demo/index.html`.

The canonical repository is `~/Developer/so-where`. Run `make demo` from its root to start the
fictional example on port 8765, or `make map` to edit this real map separately on port 8767.
The helper builds the demo HTML from the canonical template and `demo/registry.json`.
Both installed agent links point to this repository's `so-where/` directory.

The latest [consolidation observation](evidence/repository-consolidation.md) verifies the listener,
process command, working directory, source hashes, and matching HTTP response. Earlier stopped
and running observations are preserved in evidence and record history. The former skills-os
location is retired in this map, with its history intact.

The old chat output paths are compatibility symlinks. They lead to this repository, rather than
separately maintained site or map copies. The independent older `~/Developer/where` inventory is
not part of this implementation and was left unchanged.

This map has `demo: false`. The Harbor example data in `demo/` remains fictional. After future
restarts, verify the listener and served files again before refreshing the running-instance claim.
