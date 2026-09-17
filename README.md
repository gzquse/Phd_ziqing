# Scaling Quantum Computing Across the Stack — Ph.D. Dissertation & Defense Deck

**Ziqing Guo** · Department of Computer Science · Texas Tech University · Advisor: Ziwen Pan

This repository holds the LaTeX source of the dissertation, a TTU-format document class, the
bibliography, the research notes used to draft it, and the web-based defense slide deck with
Apple-Keynote-style morph transitions.

```
.
├── thesis/                 LaTeX dissertation (build with latexmk; see Makefile)
│   ├── main.tex            metadata (title, committee, date) + chapter order
│   ├── ttuthesis.cls       TTU Graduate School formatting (Feb-2026 manual) as a class
│   ├── preamble.tex        shared packages and macros (quantikz, pgfplots, algorithm2e, …)
│   ├── frontmatter/        acknowledgments, abstract, list of abbreviations
│   ├── chapters/           ch01 … ch09
│   ├── appendices/         A: Q-GEAR usage · B: artifacts & reproducibility · C: AI-use declaration
│   └── latexmkrc
├── bib/refs.bib            169 BibTeX entries (biblatex-ieee / biber)
├── slides/index.html       defense deck — single self-contained file (68 slides)
├── slides/README.md        how to present / export PDF / add slides
├── research/               bibliography of Ziqing Guo's work, TTU formatting requirements, writing guide
├── scripts/                check_chapter.sh (compile one chapter), slides_check.py, slides_to_pdf.py
└── Makefile
```

## Build the dissertation

Requirements: TeX Live 2023+ with `biblatex`, `biber`, `biblatex-ieee`, `quantikz`, `pgfplots`,
`algorithm2e`, `tocloft`, `titlesec`, `mathptmx` (Debian/Ubuntu: `texlive-full` or
`texlive-latex-extra texlive-bibtex-extra texlive-science texlive-fonts-recommended biber`).

```bash
make            # → thesis/main.pdf
make check      # compile every chapter in isolation (fast iteration)
make todos      # list open \todo{} markers
make wordcount
```

Current build: **256 pages**, 0 undefined references, 0 undefined citations.

### Dissertation structure

| Chapter | Title | Research question | Based on |
|---|---|---|---|
| I | Introduction | — | — |
| II | Background and Related Work | — | — |
| III | GPU-Accelerated Circuit Simulation at HPC Scale | RQ1 Scale | Q-GEAR (ICPP 2025) |
| IV | Hardware-Aware Optimization on Noisy Devices | RQ2 Noise | DEAL (IEEE QCE 2025), QAWA |
| V | Vectorized Encodings for Quantum Learning | RQ3 Data | QPIE (QST 2025), VQT (AAAI SS 2025), ShardQ, NNQA |
| VI | Learned Synthesis and Honest Cost Accounting | RQ4 Synthesis | RubriQ, nonlinear-wave cost study |
| VII | Auditing Error Correction on Shared Cloud Hardware | RQ5 Trust | QEC randomness audit |
| VIII | Toward a Post-Quantum-Secure Quantum Stack | RQ5 Trust | Light Rider QPC SDK, NIST FIPS 203/204/205 |
| IX | Conclusion and Future Work | — | — |

### TTU formatting

`ttuthesis.cls` encodes the Graduate School's Formatting Manual (Revised February 2026) and ETD
checklist: 1.5 in left / 1 in other margins, 12 pt serif, double spacing, running header
`Texas Tech University, <Name>, <Month Year>` 1 pt smaller at 0.5 in from the top, page numbers
centered 0.5 in from the bottom (none on title/copyright; roman from ii at Acknowledgments;
arabic from Chapter I), front-matter order Title → Copyright → Acknowledgments → TOC → Abstract →
LOT → LOF → Abbreviations, `CHAPTER I` / TITLE two-line uppercase headings, table titles above and
figure titles below, single-spaced bibliography entries with body spacing between, lettered
appendices with A.1-style floats. The Graduate School does **not** supply or endorse a LaTeX
template; the requirements as researched are in `research/ttu_format_requirements.md`.
Class options: `dissertation|thesis`, `doublespacing|onehalfspacing`, `leftmargin15|leftmargin10`.

Accessibility (WCAG 2.1 AA tagged PDF, required from Spring 2026) is **not** yet produced by this
build (pdfLaTeX, TeX Live 2023). Every figure carries a `% alt:` comment; switch to LuaLaTeX with
`\DocumentMetadata{tagging=on}` on TeX Live 2025+ to emit PDF/UA before submission.

## Before submission — open items

* Fill placeholders in `thesis/main.tex`: previously earned degrees, committee members, graduation
  month/year, current Dean of the Graduate School.
* Resolve the `\todo{}` markers (`make todos`; ≈ 38 across chapters, each naming exactly what to verify
  against the source paper).
* Re-plotted figures use the values reported in the papers with illustrative intermediate points
  (stated in each caption); replace with the original data where available.
* Confirm canonical DOI for Q-GEAR (ACM ICPP main vs. workshop volume) and publication status of the
  2025–2026 preprints.
* Attach the signed TTU AI Use Agreement (Appendix C).

## Defense slides

Open `slides/index.html` in any modern browser — no server, no dependencies. Keys: `→ ← Space`
navigate, `O` overview grid, `S` presenter notes + timer, `T` light/dark theme, `F` fullscreen,
`?` help. Deep links: `index.html#/12`. Elements sharing a `data-morph` id on adjacent slides
animate between their positions (Keynote "Magic Move"). `make slides-check` walks every slide in
headless Chromium; `make slides-pdf` exports a one-slide-per-page PDF handout.

## Research notes

`research/ziqing_guo_bibliography.md` — verified list of publications, venues, DOIs, repositories
and quantitative results (the single source of facts for the chapters).
`research/WRITING_GUIDE.md` — the narrative ("golden thread"), RQ1–RQ5, chapter map and style rules.
