#!/usr/bin/env bash
# Verify that the error messages quoted in Appendix D and the runnable
# examples in Appendices A and E still match the actual kaappi interpreter.
# Run from anywhere: ./scripts/check-appendix-examples.sh
#
# Binary lookup order: $KAAPPI, `kaappi` on PATH, then
# <workspace>/kaappi/zig-out/bin/kaappi found by walking up from this repo.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Locate the kaappi workspace (the directory containing the kaappi/ core repo)
WORKSPACE=""
d="$ROOT"
for _ in 1 2 3 4 5; do
    d="$(dirname "$d")"
    if [ -d "$d/kaappi/src" ]; then WORKSPACE="$d"; break; fi
done

KAAPPI="${KAAPPI:-}"
if [ -z "$KAAPPI" ]; then
    if command -v kaappi >/dev/null 2>&1; then
        KAAPPI="$(command -v kaappi)"
    elif [ -n "$WORKSPACE" ] && [ -x "$WORKSPACE/kaappi/zig-out/bin/kaappi" ]; then
        KAAPPI="$WORKSPACE/kaappi/zig-out/bin/kaappi"
    else
        echo "error: kaappi binary not found (set \$KAAPPI or build ../kaappi)" >&2
        exit 2
    fi
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
pass=0
fail=0
skip=0

# check NAME EXPECTED_SUBSTRING [LIB_PATH] <<'EOF' ... program ... EOF
check() {
    local name="$1" expected="$2" libpath="${3:-}"
    local prog="$TMP/$name.scm" out
    cat > "$prog"
    if [ -n "$libpath" ]; then
        out="$(cd "$TMP" && "$KAAPPI" --lib-path "$libpath" "$prog" 2>&1)"
    else
        out="$(cd "$TMP" && "$KAAPPI" "$prog" 2>&1)"
    fi
    if printf '%s' "$out" | grep -qF "$expected"; then
        pass=$((pass + 1))
    else
        fail=$((fail + 1))
        echo "FAIL: $name"
        echo "  expected substring: $expected"
        echo "  got: $(printf '%s' "$out" | head -2)"
    fi
}

## Appendix D: error message wording ------------------------------------

check undefined-variable "undefined variable 'foo'" <<'EOF'
(foo 1)
EOF

check set-unbound "set!: unbound variable 'nope'" <<'EOF'
(set! nope 42)
EOF

check type-error-car "type error in 'car': expected pair, got ()" <<'EOF'
(car '())
EOF

check type-error-plus 'expected number, got #<string>' <<'EOF'
(+ 1 "two")
EOF

check arity "'f': expected 2 arguments, got 1" <<'EOF'
(define (f a b) a)
(f 1)
EOF

check not-a-procedure "not a procedure" <<'EOF'
(define x 42)
(x 1)
EOF

check exception-raised "error: division by zero" <<'EOF'
(/ 1 0)
EOF

check error-irritants "error: bad input 42" <<'EOF'
(error "bad input" 42)
EOF

check guard-message "division by zero" <<'EOF'
(guard (e (#t (display (error-object-message e))))
  (/ 1 0))
EOF

check index-out-of-bounds "vector-ref: index 5 out of range" <<'EOF'
(vector-ref (vector 1) 5)
EOF

check stack-overflow "error.StackOverflow" <<'EOF'
(define (forever n) (+ 1 (forever (+ n 1))))
(forever 0)
EOF

check unexpected-eof "error.UnexpectedEof" <<'EOF'
(define (square x)
  (* x x)
EOF

check unterminated-string "error.UnterminatedString" <<'EOF'
(display "oops)
EOF

check unexpected-right-paren "error.UnexpectedRightParen" <<'EOF'
(display (+ 1 2)))
EOF

check invalid-escape "error.InvalidEscape" <<'EOF'
(display "hello\q")
EOF

check invalid-syntax "error.InvalidSyntax" <<'EOF'
(lambda)
EOF

check library-not-found "library not found: (nope.utils)" <<'EOF'
(import (nope utils))
EOF

## Appendix A: built-ins are available without imports ------------------

check no-import-needed "(1 3)" <<'EOF'
(display (filter odd? (list 1 2 3)))
EOF

check no-import-sqrt "4" <<'EOF'
(display (sqrt 16))
EOF

# ...but portable SRFIs (the 64 .sld ones) do need an import
check portable-srfi-needs-import "undefined variable 'list-sort'" <<'EOF'
(display (list-sort < (list 3 1 2)))
EOF

check portable-srfi-with-import "(1 2 3)" <<'EOF'
(import (srfi 132))
(display (list-sort < (list 3 1 2)))
EOF

## Appendix E: quick-start examples (need sibling ecosystem repos) ------

if [ -n "$WORKSPACE" ] && [ -d "$WORKSPACE/kaappi-json/lib" ]; then
    printf '{"name": "Ada", "port": 8080}\n' > "$TMP/config.json"
    check json-example "Ada" "$WORKSPACE/kaappi-json/lib" <<'EOF'
(import (kaappi json))
(define data
  (call-with-input-file "config.json" json-read))
(display (cdr (assoc "name" data)))
EOF
else
    skip=$((skip + 1))
    echo "SKIP: json-example (kaappi-json repo not found)"
fi

if [ -n "$WORKSPACE" ] && [ -d "$WORKSPACE/kaappi-cli/lib" ]; then
    check cli-example "#t Ada 1" "$WORKSPACE/kaappi-cli/lib" <<'EOF'
(import (kaappi cli))
(define app
  (cli "greet" "A greeting tool"
    (flag "-l" "--loud" "Use uppercase")
    (option "-n" "--times" "Repeat N times" 1)
    (argument "name" "Name to greet")))
(define result (run-cli-parse app '("-l" "Ada")))
(display (parsed-flag? result "loud")) (display " ")
(display (cdr (assoc "name" (parsed-args result)))) (display " ")
(display (parsed-ref result "times"))
EOF
else
    skip=$((skip + 1))
    echo "SKIP: cli-example (kaappi-cli repo not found)"
fi

echo
echo "check-appendix-examples: $pass passed, $fail failed, $skip skipped"
[ "$fail" -eq 0 ]
