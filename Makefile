MAIN = main
JOBNAME = kaappi-book
BUILD_DIR = build
LATEX = xelatex
LATEX_FLAGS = -output-directory=$(BUILD_DIR) -jobname=$(JOBNAME) -interaction=nonstopmode -halt-on-error

.PHONY: all clean view once

all: $(BUILD_DIR)/$(JOBNAME).pdf

$(BUILD_DIR)/$(JOBNAME).pdf: $(MAIN).tex preamble/*.tex chapters/*.tex
	@mkdir -p $(BUILD_DIR)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	-cd $(BUILD_DIR) && makeindex $(JOBNAME).idx
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

once:
	@mkdir -p $(BUILD_DIR)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

clean:
	rm -rf $(BUILD_DIR)/*

view: $(BUILD_DIR)/$(JOBNAME).pdf
	open $(BUILD_DIR)/$(JOBNAME).pdf
