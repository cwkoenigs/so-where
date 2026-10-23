# Local Where website observation

This records real local file and network observations at 2026-10-23T00:17:49+00:00.

## Endpoint and runtime

`http://127.0.0.1:8765/` refused the connection. A targeted `lsof` check found no listening
process on TCP port 8765. There is no currently serving process to attribute to a running release.
The browser inventory also contained no accessible in-app tab for that address during inspection.

## Source bundle

The existing generated website is `/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more/outputs/where-sample/index.html`.
Its source manifest is `/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more/outputs/where-sample/registry.json`, with `demo: true`.
Those Harbor records are fictional sample contents. This separate map has `demo: false` and
records the real local application, without importing Harbor as infrastructure.

Reading `/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more/outputs/where-sample/so-where/references/where.py` establishes:

- Lines 232–242: `build` loads the sibling `dashboard.html` template, embeds registry data,
  and writes `index.html` inside the selected root.
- Lines 306–320: `/` maps to `index.html` in that root and the handler reads its bytes.
- Line 347: `HTTPServer` binds to `127.0.0.1` and the chosen port.
- Lines 384–406: `--root` selects the directory; `serve` builds before starting the server.

The launch command used earlier in this same chat was:

```bash
python3 "/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more/outputs/where-sample/so-where/references/where.py" --root "/Users/clarkkoenigs/Documents/Codex/2026-10-22/i-want-to-create-one-more/outputs/where-sample" serve
```

That is historical session evidence, not a current process observation. The files have remained
in place. Restarting was not part of this mapping operation.

## Reusable skill repository

The reusable skill is in `/Users/clarkkoenigs/Developer/skills-os/so-where`.
Its Git remote is `https://github.com/cwkoenigs/skills-os.git` and current committed HEAD is `7db4b8705ddb9907897eb37b74d966ddb4515255`.
The current working tree reports `so-where/` as untracked; this skill is not in that committed HEAD.
Codex and Claude Code symlinks both resolve to this repository folder.

The registered helper and the sample helper have the same SHA-256 hash:
`e869b4d100f96a5ccc9979a31d847eb4ef850562ba2d0fbcbbde9623980a6946`. This proves the two helper copies match; it does not mean the sample
site automatically reads the registered copy. The historical launch used the sample copy.

The chat workspace is not a Git repository. Its website files have no Git commit identity.
Measured file hashes and exact command results are retained in `local-site-observation.json`.
