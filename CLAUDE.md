# Kaappi Book

A XeLaTeX book teaching the Kaappi Scheme programming language to programmers
who already know Python/JS/Ruby. Draft first edition, 18 chapters + 7 appendices.

Part of the [kaappi multi-repo workspace](../CLAUDE.md).

## Build

Requires XeLaTeX via TeX Live 2024+ (fontspec needs XeLaTeX, not pdfLaTeX).

```bash
make            # full build — 3 XeLaTeX passes (TOC, index, cross-refs)
make once       # single pass — fast iteration, refs may be stale
make view       # full build then open build/kaappi-book.pdf
make clean      # remove build/
```

Output: `build/kaappi-book.pdf`

## Project Layout

```
main.tex              Document root — title page, preface, \input chapter files
preamble/
  colors.tex          Color definitions (grayscale palette, darkbrown accent)
  packages.tex        All \usepackage calls
  fonts.tex           fontspec: EB Garamond (body), Source Sans 3 (headings), Fira Code (mono)
  fonts-memoir.tex    Memoir heading font overrides
  decorations.tex     Lambda ornament, section/chapter break rules
  layout.tex          6×9" page geometry, margins, chapter style, page style
  styles.tex          mdframed environments (note, warning, exercise, codeoutput)
  listings.tex        Scheme language definition, lstlisting styles (scheme, repl)
chapters/             One .tex per chapter, \input'd from main.tex
fonts/                Bundled .ttf (EB Garamond, Source Sans 3, Fira Code)
build/                Output directory (gitignored)
```

## Book Structure

| Part | Chapters | Files |
|------|----------|-------|
| I: Getting Started | 1. Introduction, 2. Installation, 3. First Steps | ch01–ch03 |
| II: The Language | 4. Data Types, 5. Lists & Pairs, 6. Functions, 7. Control Flow, 8. Local Bindings, 9. Higher-Order Functions, 10. I/O | ch04–ch10 |
| III: Going Further | 11. Macros, 12. Library System, 13. Records, 14. Error Handling, 15. Continuations | ch11–ch15 |
| IV: Beyond R7RS | 16. Standard Library (SRFIs), 17. FFI, 18. Concurrency | ch16–ch18 |
| Appendices | A. R7RS Reference, B. CLI Reference, C. SRFI Catalog, D. Error Messages, E. Ecosystem, F. Glossary, G. Further Reading | appendix-a–g |

## Writing Guidelines

- Target audience: programmers who know Python/JS/Ruby but not Scheme or Lisp
- Active voice, short sentences, no academic jargon
- One concept per section; build on previous chapters
- Every concept must have a runnable Kaappi code example
- Compare to Python/JS equivalents when it clarifies
- Keep code examples under 20 lines; split longer demos into steps
- End each chapter with `\section*{Summary}` (bulleted key takeaways) then `\section*{Exercises}`

## LaTeX Conventions

- Never add `\usepackage` in chapter files — edit `preamble/packages.tex`
- Never use `\lstset` in chapter files — global config in `preamble/listings.tex`
- Scheme code: `\begin{lstlisting}...\end{lstlisting}` (default style)
- REPL sessions: `\begin{lstlisting}[style=repl]` (shows `>` prompt)
- Inline code: `\code{define}` or `\lstinline{(+ 1 2)}`
- Callout: `\begin{note}[Title]...\end{note}`
- Pitfall: `\begin{warning}[Title]...\end{warning}`
- Exercise: `\begin{exercise}[Title]...\end{exercise}` (auto-numbered per chapter)
- REPL output: `\begin{codeoutput}[Title]...\end{codeoutput}`
- Section transition: `\sectionbreak`
- Chapter end ornament: `\chapterend`
- Cross-refs: `\label{sec:topic}` / `\ref{sec:topic}`
- Index: `\index{continuations}` near first significant mention

## Kaappi Reference Sources

When writing about Kaappi features, verify against these sources (not from memory).
All paths are relative to this repo root (`kaappi-book/`):

- **Kaappi source code**: `../kaappi/` — the Zig implementation
  - `../kaappi/src/` — core runtime, compiler, VM, GC, primitives (~48k lines)
  - `../kaappi/lib/` — portable Scheme SRFI libraries (.sld files)
  - `../kaappi/docs/dev/` — architecture, IR, LLVM backend docs
  - `../kaappi/CONFORMANCE.md` — R7RS compliance details
  - `../kaappi/CLAUDE.md` — detailed build options, architecture, coding patterns
- **Website docs**: `../kaappi.github.io/` — the kaappi-lang.org site source
  - `../kaappi.github.io/docs/guide/tutorial.md` — beginner tutorial
  - `../kaappi.github.io/docs/guide/language.md` — language quick reference
  - `../kaappi.github.io/docs/procedures/` — 600+ procedure reference by category
  - `../kaappi.github.io/docs/guide/srfi-support.md` — SRFI availability table
  - `../kaappi.github.io/docs/guide/cli.md` — CLI flags and subcommands
  - `../kaappi.github.io/docs/cookbook/` — practical recipes
- **Wiki**: `../wiki/` — Scheme language reference

## Key Facts

- R7RS-small compliant, 554 built-in procedures, 33 syntax forms, 72 SRFIs
- Written in Zig; runs on macOS ARM64, Linux x86_64/ARM64/RISC-V, WASM
- Pipeline: Reader → Expander → IR → Bytecode → Register VM (+ LLVM native backend)
- C FFI via `(kaappi ffi)`, green threads via `(kaappi fibers)`, SRFI-18 OS threads
- Package manager: thottam

## Commits

Short imperative subject line. Body explains _why_, not _what_.
