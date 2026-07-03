# TODO

Tracked work items for the book. Remove items when done.

| Priority | Item | Notes |
|----------|------|-------|
| High | Fix TODO-marked REPL listing divergences in chapters 10–18 | The transcript checker now exists (`make check-repl`, `tools/check-repl-listings.py`) and verified all 18 chapters on 2026-07-03: chapters 1–9 are clean; the real divergences it found in chapters 10–18 are recorded as `TODO` entries in `tools/repl-check-ignore.txt` (invented error formats in ch11/ch14, ch15 continuation-counter output, ch16 SRFI imports / `regexp-replace` / hash-ordering / `hash-table-ref` examples, ch18 fiber output). One ch18 listing also blocks forever — the checker prints a timeout warning until it is fixed. Fix each listing and delete its ignore entry. |
