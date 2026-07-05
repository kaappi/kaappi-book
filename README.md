# Kaappi: A Scheme Programming Language

A book about the [Kaappi](https://kaappi-lang.org/) Scheme implementation, targeting beginners with some programming experience.

## Building

Requires XeLaTeX (TeX Live 2024+).

```bash
make        # Full build (latexmk resolves TOC/index/refs)
make once   # Single pass (fast iteration)
make view   # Open PDF in default viewer
make clean  # Remove build artifacts
```

The output is `build/kaappi-book.pdf`.

## Cover

A print-ready wrap cover for the KDP 6"×9" paperback (back cover, spine, and
front cover on one full-bleed sheet):

```bash
make cover                  # Print-ready PDF → build/cover.pdf
make cover-proof            # Same, with KDP trim/bleed/spine/safe-area guides
make cover-proof PAGES=400  # Proof a hypothetical interior page count
make view-cover             # Build and open
```

All horizontal geometry derives from `\PageCount` in `cover.tex`: the spine
width is pages × 0.002252" (KDP's black-&-white-on-white factor), and the
sheet width, fold positions, and proofing guides follow. After an interior
reflow, update `\PageCount`, rebuild, and eyeball `make cover-proof`. A build
warning fires if the spine gets too thin for the spine text (below ~0.32",
about 142 pages).

The front-cover cup illustration (`images/cover-cup.png`) was generated with
the Gemini API and post-processed with an alpha edge-fade so it blends into
the espresso background. To regenerate it:

```bash
GEMINI_API_KEY=... python3 scripts/generate-cover-cup.py
```

Generation is nondeterministic — check that the steam still reads as a clean
λ, then rebuild the cover.

## Structure

```
main.tex              Entry point
cover.tex             KDP paperback wrap cover (see Cover above)
preamble/             LaTeX configuration (fonts, layout, styles, listings)
chapters/             Chapter source files
images/               Cover artwork (Gemini-generated cup illustration)
scripts/              Verification and asset-generation scripts
fonts/                Bundled TTF fonts (EB Garamond, Source Sans 3, Fira Code)
build/                Output directory (gitignored)
```

## Fonts

- **EB Garamond** — body text (serif)
- **Source Sans 3** — headings (sans-serif)
- **Fira Code** — code listings (monospace)

## Chapter Outline

| Part | Chapters |
|------|----------|
| I: Getting Started | Introduction, Installation, First Steps |
| II: The Language | Data Types, Lists, Control Flow, Functions, Bindings, Higher-Order Functions, I/O |
| III: Going Further | Macros, Libraries, Records, Error Handling, Continuations |
| IV: Beyond R7RS | Standard Library (SRFIs), FFI, Concurrency |
| Appendices | R7RS Reference, CLI Reference, SRFI Catalog, Error Messages, Ecosystem, Glossary, Further Reading |

## Related

- [Kaappi source](https://github.com/kaappi/kaappi) — the Scheme implementation in Zig
- [kaappi-lang.org](https://kaappi-lang.org/) — end-user documentation and interactive tour
