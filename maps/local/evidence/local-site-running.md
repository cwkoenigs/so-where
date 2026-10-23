# Local Where website running

Observed at 2026-10-23T11:52:42+00:00.

The HTTP endpoint `http://127.0.0.1:8765/` returned status 200. Its response bytes exactly matched `/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more/outputs/where-sample/index.html`.

## Runtime

```text
COMMAND   PID         USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
Python  11751 clarkkoenigs    4u  IPv4 0xbeae80eaecd2b555      0t0  TCP 127.0.0.1:8765 (LISTEN)

11751 Fri Oct 23 06:51:28 2026     /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python outputs/where-sample/so-where/references/where.py --root outputs/where-sample serve
p11751
fcwd
n/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more
```

The command selects `outputs/where-sample` relative to the observed working directory `/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more`. The launch helper is the bundled sample copy.

## Source

The source snapshot id is `sha256:a2db33aa948b127772b1071494b5dbc9c0bcec93925c568072d9bd3b47c4b188`. This is a measured content fingerprint of the Python helper, HTML template, and input registry; it is not a Git commit. The local instance identity is `local-pid-11751-html-91a0c44a61c74cb5`. Full measured hashes are retained in `local-site-running.json`.

The root workspace remains outside Git. The reusable skill is still separate in skills-os. The sample's Harbor infrastructure remains fictional. This observation verifies a local running instance; it does not establish persistent hosting or uptime monitoring.
