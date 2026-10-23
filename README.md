# Where

Where keeps the skill, local website, example data, real map, and tests in one repository.

GitHub: [cwkoenigs/so-where](https://github.com/cwkoenigs/so-where) (private).

```bash
make demo
```

Open `http://127.0.0.1:8765/` for the fictional working example. Stop with Ctrl-C.
Use `make map` to edit the real local inventory at `http://127.0.0.1:8767/`.

## Repository layout

| Path | Purpose |
| --- | --- |
| `so-where/SKILL.md` | Agent workflow and invocation guidance |
| `so-where/references/where.py` | Canonical Python server, generator, and manifest helper |
| `so-where/references/dashboard.html` | Canonical HTML/CSS/JavaScript template |
| `so-where/references/contract.md` | Record and evidence contract |
| `demo/registry.json` | Fictional example records; `demo: true` |
| `demo/evidence/` | Clearly labeled fictional evidence |
| `maps/local/registry.json` | Real local observations; `demo: false` |
| `maps/local/evidence/` | Local observations and relocation history |
| `tests/` | Isolated behavioral and installer tests |
| `docs/design.md` | Product model and implementation boundaries |
| `.where.json` | Points agents to the real map |

The JSON manifests are canonical. `index.html`, `START.md`, and `obsidian/` inside each map
directory are generated, ignored by Git, and rebuilt by the helper. Optional Obsidian exports
are ordinary Markdown; Obsidian is not required. Local observations contain machine-specific
paths and should be reviewed before sharing this repository with another machine or audience.

## Commands

Requires Python 3.9+ on macOS or Linux, plus Make for the shortcuts. No Python package install.

```bash
make build       # rebuild the demo and real map
make check       # validate both manifests
make test        # run isolated tests
make install     # link this repository's skill into installed local runtimes
make demo        # launch the demo on loopback port 8765
make map         # launch the real map on loopback port 8767
```

The helper is directly available without Make:

```bash
python3 so-where/references/where.py --root demo serve --port 8765
python3 so-where/references/where.py --root maps/local check
python3 so-where/references/where.py --root maps/local build
python3 so-where/references/where.py --help
```

`make install` creates or updates only `so-where` symlinks in existing Codex and Claude Code
runtime directories. It refuses to overwrite a real skill directory. Source edits happen here;
the runtime links do not create another copy. Restart the runtime when new skill discovery is needed.

## Workflow

Untangle a real serving chain, capture the compact answer as a draft, attach observations, and
promote once the evidence supports it. A rebuild never refreshes observation dates. Relocation
updates pointers and preserves history; physical moves remain separate operations.

The repository has no required remote or cloud service. A local Git commit is versioning, not
publication. The independent older `where`/Atlas inventories are outside this repository and
are not merged or modified by this consolidation.
