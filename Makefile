MAIN = main
JOBNAME = kaappi-book
BUILD_DIR = build
COMMON_FLAGS = -output-directory=$(BUILD_DIR) -jobname=$(JOBNAME) -interaction=nonstopmode -halt-on-error
LATEXMK = latexmk
LATEXMK_FLAGS = -xelatex $(COMMON_FLAGS)
XELATEX = xelatex

.PHONY: all clean view once check-repl check-examples

# Full build: latexmk runs XeLaTeX (and makeindex) as many times as needed
# to resolve the TOC, index, and cross-references.
all:
	@mkdir -p $(BUILD_DIR)
	$(LATEXMK) $(LATEXMK_FLAGS) $(MAIN).tex

# Quick iteration: a single XeLaTeX pass (TOC/index/refs may be stale).
once:
	@mkdir -p $(BUILD_DIR)
	$(XELATEX) $(COMMON_FLAGS) $(MAIN).tex

view: all
	open $(BUILD_DIR)/$(JOBNAME).pdf

# Replay every REPL listing through the kaappi binary and diff the output
# shown in the book against reality. Needs `kaappi` on PATH.
check-repl:
	python3 tools/check-repl-listings.py chapters/*.tex

# Verify appendix error messages and code examples against the real
# kaappi interpreter (needs ../kaappi built, or set KAAPPI=/path/to/kaappi).
check-examples:
	bash scripts/check-appendix-examples.sh

clean:
	-$(LATEXMK) -C $(COMMON_FLAGS) $(MAIN).tex >/dev/null 2>&1
	rm -rf $(BUILD_DIR)/*
