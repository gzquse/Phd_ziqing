# Ziqing Guo — Ph.D. dissertation & defense slides
# Targets: make (thesis), make thesis, make slides-pdf, make check, make clean, make zip

THESIS_DIR := thesis
MAIN       := main
PDF        := $(THESIS_DIR)/$(MAIN).pdf
SLIDES     := slides/index.html

.PHONY: all thesis check clean distclean slides-pdf slides-check zip wordcount todos

all: thesis

thesis: $(PDF)

$(PDF): $(THESIS_DIR)/$(MAIN).tex $(THESIS_DIR)/ttuthesis.cls $(THESIS_DIR)/preamble.tex \
        $(wildcard $(THESIS_DIR)/chapters/*.tex) $(wildcard $(THESIS_DIR)/frontmatter/*.tex) \
        $(wildcard $(THESIS_DIR)/appendices/*.tex) bib/refs.bib
	cd $(THESIS_DIR) && latexmk -pdf -interaction=nonstopmode $(MAIN).tex
	@pdfinfo $(PDF) | grep Pages

# Compile every chapter/appendix in isolation (fast feedback while writing one chapter)
check:
	@for f in $(THESIS_DIR)/chapters/*.tex $(THESIS_DIR)/appendices/*.tex; do \
	  scripts/check_chapter.sh $${f#$(THESIS_DIR)/} || exit 1; done

# Word counts per chapter (prose approximation via detex)
wordcount:
	@for f in $(THESIS_DIR)/chapters/*.tex; do printf "%-45s %6s\n" $$f $$(detex $$f | wc -w); done

# List open TODO markers
todos:
	@grep -n "\\\\todo{" $(THESIS_DIR)/chapters/*.tex $(THESIS_DIR)/frontmatter/*.tex $(THESIS_DIR)/appendices/*.tex || true

# Export the web deck as a PDF handout (one slide per page) with headless Chromium
slides-pdf:
	python3 scripts/slides_to_pdf.py $(SLIDES) slides/defense-slides.pdf

# Walk every slide in headless Chromium and fail on console errors
slides-check:
	python3 scripts/slides_check.py $(SLIDES)

clean:
	cd $(THESIS_DIR) && latexmk -c $(MAIN).tex; rm -rf $(THESIS_DIR)/build-check

distclean: clean
	cd $(THESIS_DIR) && latexmk -C $(MAIN).tex

zip: thesis
	git archive --format=zip --prefix=ziqing-guo-phd-thesis/ -o ../ziqing-guo-phd-thesis.zip HEAD
	@echo "wrote ../ziqing-guo-phd-thesis.zip"
