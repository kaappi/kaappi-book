MAIN = main
JOBNAME = kaappi-book
BUILD_DIR = build
COMMON_FLAGS = -output-directory=$(BUILD_DIR) -jobname=$(JOBNAME) -interaction=nonstopmode -halt-on-error
COVER_FLAGS = -output-directory=$(BUILD_DIR) -interaction=nonstopmode -halt-on-error
LATEXMK = latexmk
LATEXMK_FLAGS = -xelatex $(COMMON_FLAGS)
XELATEX = xelatex

.PHONY: all clean view once check-repl check-examples cover cover-proof view-cover

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

# Print-ready full-bleed wrap cover (12.797" x 9.250", KDP spec; see
# cover.tex). latexmk reruns XeLaTeX until the remember-picture page
# anchor settles.
cover:
	@mkdir -p $(BUILD_DIR)
	$(LATEXMK) -xelatex $(COVER_FLAGS) cover.tex

# Same cover with the KDP guide overlay (trim, bleed, spine folds, safe
# area) for proofing. Two passes resolve remember-picture on a fresh jobname.
cover-proof:
	@mkdir -p $(BUILD_DIR)
	$(XELATEX) $(COVER_FLAGS) -jobname=cover-proof "\def\GUIDES{}\input{cover.tex}"
	$(XELATEX) $(COVER_FLAGS) -jobname=cover-proof "\def\GUIDES{}\input{cover.tex}"

view-cover: cover
	open $(BUILD_DIR)/cover.pdf

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
