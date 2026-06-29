MAIN = main
BUILD_DIR = build
LATEX = xelatex
LATEX_FLAGS = -output-directory=$(BUILD_DIR) -interaction=nonstopmode -halt-on-error

.PHONY: all clean view once

all: $(BUILD_DIR)/$(MAIN).pdf

$(BUILD_DIR)/$(MAIN).pdf: $(MAIN).tex preamble/*.tex chapters/*.tex
	@mkdir -p $(BUILD_DIR)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

once:
	@mkdir -p $(BUILD_DIR)
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

clean:
	rm -rf $(BUILD_DIR)/*

view: $(BUILD_DIR)/$(MAIN).pdf
	open $(BUILD_DIR)/$(MAIN).pdf
