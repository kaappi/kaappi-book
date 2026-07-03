# TODO

Tracked work items for the book. Remove items when done.

| Priority | Item | Notes |
|----------|------|-------|
| Medium | Drop "upstream" entries from `tools/repl-check-ignore.txt` as kaappi fixes land | All 18 chapters now pass `make check-repl` (2026-07-03). The remaining ignore entries are either inherent (interactive-only listings, stdin/filesystem examples) or blocked on kaappi bugs reported upstream: multiple-values truncation at the REPL (ch16 partition/unzip2), and mid-session library-import corruption (ch16 srfi 158/113/128 units). When those core fixes ship, delete the matching entries and re-run `make check-repl`; the ch11/ch14 error listings can also show real messages once uncaught exceptions print their message and irritants. |
