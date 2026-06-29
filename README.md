# Kaappi: A Scheme Programming Language

A book about the [Kaappi](https://kaappi-lang.org/) Scheme implementation, targeting beginners with some programming experience.

## Building

Requires XeLaTeX (TeX Live 2024+).

```bash
make        # Full build (3 passes for TOC/index)
make once   # Single pass (fast iteration)
make view   # Open PDF in default viewer
make clean  # Remove build artifacts
```

The output is `build/kaappi-book.pdf`.

## Structure

```
main.tex              Entry point
preamble/             LaTeX configuration (fonts, layout, styles, listings)
chapters/             Chapter source files
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
| II: The Language | Data Types, Lists, Functions, Control Flow, Bindings, Higher-Order Functions, I/O |
| III: Advanced Topics | Macros, Libraries, Error Handling, Records, Continuations |
| IV: Beyond R7RS | Standard Library (SRFIs), FFI, Concurrency |
| Appendices | R7RS Reference, CLI Reference, SRFI Catalog, Error Messages, Ecosystem, Glossary, Further Reading |

## Related

- [Kaappi source](https://github.com/kaappi/kaappi) — the Scheme implementation in Zig
- [kaappi-lang.org](https://kaappi-lang.org/) — end-user documentation and interactive tour
