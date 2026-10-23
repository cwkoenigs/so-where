# Repository consolidation

Observed 2026-10-23T12:34:23+00:00.

All components of this implementation now live in `/Users/clarkkoenigs/Developer/so-where`: the canonical skill in `so-where/`, fictional site in `demo/`, real inventory in `maps/local/`, and tests in `tests/`. Git is initialized on `main`; no remote is configured.

The earlier separate `~/Developer/where` inventory was inspected for a name collision and left unchanged. Its Markdown cards were not imported into this implementation.

The former chat output directories are compatibility symlinks into this repository. The former untracked skills-os skill copy was extracted; installed Codex and Claude Code links now point directly to this repository's `so-where/`. No second maintained copy remains in skills-os. A migration backup retains the former files in the chat's scratch directory.

## Running website

`http://127.0.0.1:8765/` returned HTTP 200. Its HTML bytes exactly matched `demo/index.html`.

```text
COMMAND   PID         USER   FD   TYPE            DEVICE SIZE/OFF NODE NAME
Python  19338 clarkkoenigs    4u  IPv4 0x95e4564104d3318      0t0  TCP 127.0.0.1:8765 (LISTEN)

/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python so-where/references/where.py --root demo serve --port 8765
p19338
fcwd
n/Users/clarkkoenigs/Developer/so-where
```

The local instance is `local-pid-19338-html-98a894df313f548e`. Its measured source fingerprint is `sha256:a902818cb45d1f557dee173d36d8b6a998a308c07df27d0ade86d80a2403bd08`, calculated from the helper, template, and demo registry; this is a content digest, not a Git commit id. Full hashes and exact observations are in `repository-consolidation.json`.

The server was restarted using `make demo` in the new repository. The generated site still contains fictional Harbor records, and those records are not imported into the real inventory. Local Git versioning does not publish this map.
