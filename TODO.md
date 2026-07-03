# TODO

Tracked work items for the book. Remove items when done.

| Priority | Item | Notes |
|----------|------|-------|
| High | Transcript checker (`tools/check-transcripts.sh`) | Extract `style=repl` listings from chapters, run the inputs through the installed `kaappi` binary, and diff the printed outputs against the book. Chapters 1–4 were verified by hand (2026-07-03); build this before giving chapters 5–18 the same accuracy pass, since that is where most transcript drift will hide. |
