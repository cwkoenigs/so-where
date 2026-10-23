# Where working example

This is a fictional map for trying capture, curation, search, links, and relocation history.

From the repository root run `make demo`, then open `http://127.0.0.1:8765/`.
Try promoting the complete investigation note, then the incomplete nightly job. The first can
be accepted while its observations remain recent; the second stays draft until its gaps are filled.

The source manifest is `registry.json`. Its evidence is deliberately fictional. Do not turn this
into a real map by relabeling sample evidence. The real local inventory is in `maps/local/` at
the repository root and can be viewed separately with `make map` on port 8767.

The local `so-where` and `tests` directory links preserve old sample commands while pointing
to the single canonical skill and test suite at repository root.
