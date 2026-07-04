#!/usr/bin/env python3
"""Verify REPL listings in the book against the actual kaappi binary.

Extracts every ``\\begin{lstlisting}[style=repl]`` block from the given .tex
files, replays the inputs (lines starting with "> ") through ``kaappi`` in
piped mode, and diffs the actual output against the output printed in the
book. Each chapter is replayed as one continuous session, matching the
"type along in one REPL" reading experience, so definitions carry across
blocks within a chapter.

Plain (non-repl) Scheme listings are fed to the session as silent context --
they often define procedures that later repl listings call -- but their
output is not checked. Unbalanced ones (syntax templates like
``(if test consequent alternate)``) are skipped.

Skipped blocks:
  - blocks after ``\\section*{Exercises}`` (they show results of code the
    reader is asked to write),
  - blocks containing ``???`` placeholders or ``(*@`` LaTeX escapes,
  - Python comparison listings.

Known, intentional divergences live in tools/repl-check-ignore.txt as
``<file-basename>:<line>`` entries (the line number of the "> " input line),
with an optional ``# reason`` comment.

Usage: python3 tools/check-repl-listings.py chapters/*.tex
Exit status: 0 if no unexpected mismatches, 1 otherwise.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Honor $KAAPPI (as documented in CLAUDE.md) so the listings can be checked
# against a locally built interpreter. Each chapter is replayed in a fresh
# temp cwd (see run_chapter), so a relative $KAAPPI would resolve against that
# temp dir and fail -- use an absolute path, e.g.
#   KAAPPI=$PWD/../kaappi/zig-out/bin/kaappi make check-repl
KAAPPI = os.environ.get("KAAPPI", "kaappi")
MARKER_FMT = "@@REPL-CHECK-{}@@"
BEGIN_RE = re.compile(r"\\begin\{lstlisting\}\[([^\]]*)\]")
END_MARK = r"\end{lstlisting}"
EXERCISES_MARK = r"\section*{Exercises}"


def paren_delta(line, in_string):
    """Net paren depth change of a line, honoring strings, chars, comments.

    Returns (delta, in_string) where in_string carries multi-line strings.
    """
    delta = 0
    i = 0
    n = len(line)
    while i < n:
        c = line[i]
        if in_string:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == ";":  # line comment
            break
        if c == "#" and i + 1 < n and line[i + 1] == ";":
            i += 2  # datum comment "#;": the following datum still balances
            continue
        if c == "#" and i + 1 < n and line[i + 1] == "\\":
            i += 3  # skip "#\x"; named chars' remaining letters are harmless
            continue
        if c == "(":
            delta += 1
        elif c == ")":
            delta -= 1
        i += 1
    return delta, in_string


class Unit:
    def __init__(self, path, lineno, is_context=False):
        self.path = path
        self.lineno = lineno  # line of the first "> " input line
        self.input_lines = []
        self.expected = []
        self.is_context = is_context  # fed to the session, output discarded


def extract_units(path):
    """Yield Units from all runnable style=repl blocks in a .tex file."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    units = []
    in_block = False
    past_exercises = False
    block_lines = []  # (lineno, text)

    def flush_context_block(block):
        text = "\n".join(t for _, t in block)
        if "???" in text or "(*@" in text or not block:
            return
        if "..." in text:
            return  # syntax template: would compile-error and end the session
        depth = 0
        in_str = False
        for _, raw in block:
            d, in_str = paren_delta(raw, in_str)
            depth += d
        if depth != 0 or in_str:
            return  # syntax template or fragment, not runnable
        unit = Unit(path, block[0][0], is_context=True)
        unit.input_lines = [t for _, t in block]
        units.append(unit)

    def flush_block(block):
        text = "\n".join(t for _, t in block)
        if "???" in text or "(*@" in text:
            return
        cur = None
        depth = 0
        in_str = False
        reading_input = False
        for lineno, raw in block:
            if raw.startswith("> "):
                cur = Unit(path, lineno)
                units.append(cur)
                body = raw[2:]
                cur.input_lines.append(body)
                depth, in_str = 0, False
                d, in_str = paren_delta(body, in_str)
                depth += d
                reading_input = depth > 0 or in_str
            elif cur is not None and reading_input:
                if raw.startswith("...") and not in_str:
                    raw = raw[3:]  # "..." is the REPL's continuation prompt
                cur.input_lines.append(raw)
                d, in_str = paren_delta(raw, in_str)
                depth += d
                reading_input = depth > 0 or in_str
            elif cur is not None:
                cur.expected.append(raw.rstrip())

    is_repl_block = False
    for idx, line in enumerate(lines, start=1):
        if EXERCISES_MARK in line:
            past_exercises = True
        if not in_block:
            if past_exercises:
                continue
            m = BEGIN_RE.search(line)
            if m:
                opts = m.group(1)
                if "language=Python" in opts:
                    continue
                in_block = True
                is_repl_block = "style=repl" in opts
                block_lines = []
            elif line.strip() == r"\begin{lstlisting}":
                in_block = True
                is_repl_block = False
                block_lines = []
        else:
            if END_MARK in line:
                in_block = False
                if is_repl_block:
                    flush_block(block_lines)
                else:
                    flush_context_block(block_lines)
            else:
                block_lines.append((idx, line))
    return units


def load_ignores(repo_root):
    ignores = {}
    f = repo_root / "tools" / "repl-check-ignore.txt"
    if not f.exists():
        return ignores
    for raw in f.read_text(encoding="utf-8").splitlines():
        entry, _, reason = raw.partition("#")
        entry = entry.strip()
        if entry:
            ignores[entry] = reason.strip()
    return ignores


def normalize(seg):
    out = [l.rstrip() for l in seg]
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    return out


def run_chapter(units):
    """Replay a chapter's units in one kaappi session; return actual outputs."""
    feed = []
    for i, u in enumerate(units):
        feed.extend(u.input_lines)
        feed.append('(display "\\n{}\\n")'.format(MARKER_FMT.format(i)))
    try:
        # Run in a scratch directory so file-writing listings (chapter 10)
        # do not litter the repository.
        proc = subprocess.run(
            [KAAPPI],
            input="\n".join(feed) + "\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
            cwd=tempfile.mkdtemp(prefix="repl-check-"),
        )
        stdout = proc.stdout
    except subprocess.TimeoutExpired as e:
        stdout = e.stdout or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        print(
            "WARN {}: session timed out; results after the hang are missing".format(
                Path(units[0].path).name
            ),
            file=sys.stderr,
        )
    segments = []
    cur = []
    idx = 0
    for line in stdout.splitlines():
        if line.strip() == MARKER_FMT.format(idx):
            segments.append(cur)
            cur = []
            idx += 1
        else:
            cur.append(line)
    while len(segments) < len(units):  # crash or lost marker: pad
        segments.append(["<no output: session ended early>"])
    return segments


def main(argv):
    repo_root = Path(__file__).resolve().parent.parent
    ignores = load_ignores(repo_root)
    files = [a for a in argv if a.endswith(".tex")]
    if not files:
        print("usage: check-repl-listings.py chapters/*.tex", file=sys.stderr)
        return 2

    total = passed = ignored = 0
    failures = []
    for path in files:
        units = extract_units(path)
        if not units:
            continue
        segments = run_chapter(units)
        for u, seg in zip(units, segments):
            if u.is_context:
                continue
            total += 1
            exp, act = normalize(u.expected), normalize(seg)
            if exp == act:
                passed += 1
                continue
            key = "{}:{}".format(Path(u.path).name, u.lineno)
            if key in ignores:
                ignored += 1
                continue
            failures.append((key, u, exp, act))

    for key, u, exp, act in failures:
        print("FAIL {}".format(key))
        print("  input:    {}".format(" ".join(l.strip() for l in u.input_lines)))
        print("  expected: {}".format(exp if exp else "<nothing>"))
        print("  actual:   {}".format(act if act else "<nothing>"))
    print(
        "\n{} checked: {} passed, {} ignored, {} failed".format(
            total, passed, ignored, len(failures)
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
