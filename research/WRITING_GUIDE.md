# Dissertation Writing Guide (shared by all chapter authors)

## The dissertation in one paragraph (the "golden thread")

**Title:** *Scaling Quantum Computing Across the Stack: GPU-Accelerated Circuit Simulation, Hardware-Aware Algorithms, Quantum Learning, and Verifiable Error Correction for the Post-Quantum Era*

**Author:** Ziqing Guo, Ph.D. in Computer Science, Texas Tech University (advisor: Ziwen Pan). Work done with NERSC/LBNL (Jan Balewski), UMD QLab / BosonQ Psi (Alex Khan), TTU (Wenshuo Hu, Victor Sheng, Jie Li, Yong Chen), U. Saskatchewan (Steven Rayan), RIT (Kewen Xiao), Lightrider (Anthony Lawrence, Renyu Wang), Quantropi (Randy Kuang).

**Thesis statement.** Useful quantum computation in the coming decade will be delivered not by a quantum processor alone but by a *co-designed stack* in which classical high-performance computing (HPC) surrounds the QPU at every layer: (i) GPU-accelerated simulation to develop, verify and calibrate circuits at scales the hardware cannot yet reach; (ii) hardware-aware algorithm design that replaces black-box variational optimization with structure derived from the problem and the device; (iii) structured, vectorized data encodings that make the classical–quantum data interface efficient and learnable; (iv) AI/HPC-driven synthesis that compiles toward fault-tolerant resource budgets; and (v) security-aware error correction and post-quantum cryptography so that the same stack can be *trusted* when it runs on shared cloud hardware in the post-quantum era.

**Five research questions** (refer to them by number, e.g. "RQ1", in every chapter):
- **RQ1 (Scale):** How far can classical HPC push exact circuit simulation, and how do we make that capability usable without rewriting quantum programs? → Chapter III (Q-GEAR).
- **RQ2 (Noise):** How can optimization algorithms on NISQ devices exploit problem and hardware structure instead of black-box parameter search? → Chapter IV (DEAL, QAWA).
- **RQ3 (Data):** How should classical data enter and leave a quantum processor so that learning models are shot-efficient, hardware-compatible and trainable? → Chapter V (QPIE, VQT, ShardQ, NNQA).
- **RQ4 (Synthesis):** Can learned, HPC-scale synthesis produce circuits that respect fault-tolerant resource budgets, and what does honest cost accounting say about end-to-end quantum advantage? → Chapter VI (RubriQ; measurement/reload costs in nonlinear-wave simulation).
- **RQ5 (Trust):** How do we make error-corrected computation on shared cloud QPUs auditable and secure, and how does that connect to post-quantum cryptography standards? → Chapters VII (QEC randomness audit) and VIII (PQC / Light Rider QPC SDK).

**Chapter map** (use `\cref{ch:...}` with these labels):
| Chapter | File | Label | Theme | Source papers (bib keys) |
|---|---|---|---|---|
| I Introduction | ch01-introduction.tex | ch:intro | — | all |
| II Background | ch02-background.tex | ch:background | foundations | related-work keys |
| III GPU-Accelerated Simulation at HPC Scale | ch03-qgear.tex | ch:qgear | A | guo2025qgear, guo2025qgearsoftware |
| IV Hardware-Aware Optimization on Noisy Devices | ch04-nisq-optimization.tex | ch:nisq | B | guo2025deal, guo2025qawa |
| V Vectorized Encodings for Quantum Learning | ch05-quantum-learning.tex | ch:qml | C | guo2025qpie, guo2025vqt, guo2025shardq, guo2026nnqa |
| VI Learned Synthesis and Honest Cost Accounting | ch06-ai-synthesis.tex | ch:synthesis | F/A/D | guo2026rubriq, guo2026rubriqsoftware, guo2026nonlinearwaves, guo2026splitstepqude |
| VII Auditing Error Correction on Shared Cloud Hardware | ch07-qec-security.tex | ch:qec | D/E | guo2026qecaudit |
| VIII Toward a Post-Quantum-Secure Quantum Stack | ch08-pqc.tex | ch:pqc | E | guo2026lightriderqpc, nist2024fips203/204/205, nist2019fips1403, nist2015sp80090a |
| IX Conclusion | ch09-conclusion.tex | ch:conclusion | — | all |
| App. A Q-GEAR artifacts | appA-qgear-artifacts.tex | app:qgear | | |
| App. B Reproducibility & artifacts | appB-reproducibility.tex | app:repro | | |
| App. C AI-use disclosure | appC-ai-use.tex | app:ai | | |

## Source of truth for facts

`research/ziqing_guo_bibliography.md` contains the verified summaries (authors, venues, numbers). **Use the numbers there; do not invent new experimental numbers.** Where you need a detail that is not in the summary (e.g., a hyper-parameter, an exact table value), write the sentence with a `\todo{verify: ...}` marker rather than guessing — e.g. `the optimizer budget was 1000 iterations\todo{verify against paper}`. A reader must be able to distinguish established results from placeholders. Keep TODOs sparse (aim ≤ 8 per chapter) and specific.

## Length and form

- Target word counts are given in each assignment; the dissertation as a whole must exceed 100 pages at 12 pt double spacing (≈ 280 words/page of prose; figures/tables/equations add pages).
- Each chapter: `\chapter{Title}\label{ch:...}` then, for chapters based on published work, a `\authorshipstatement{...}` (TTU multi-paper rule) naming the paper(s), venue, coauthors, and the candidate's role (e.g. "The candidate designed the framework, implemented the software, ran all experiments and wrote the manuscript; coauthors advised on HPC deployment (J.B.) and supervised the work (Z.P.)."). Then an un-numbered lead paragraph ("This chapter addresses RQ1 …"), then numbered sections.
- Standard research-chapter skeleton: Introduction/Motivation → Problem statement & preliminaries (chapter-specific; general background lives in Chapter II — cross-reference it with `\cref{sec:bg:...}` rather than repeating) → Method/Design (with algorithm boxes, equations, circuit diagrams) → Implementation → Experimental setup (hardware, software versions, metrics) → Results (tables/figures) → Discussion & limitations → Relation to the other chapters (explicitly say how it feeds forward/back: e.g. "The Q-GEAR pipeline of \cref{ch:qgear} was used to validate the 20-qubit DEAL circuits before hardware submission") → Summary.
- Voice: "we" for the work; "this dissertation" for the whole document; present tense for what the chapter does, past tense for experiments performed. Formal academic prose. No marketing language. No bullet-heavy text; use prose paragraphs, with `itemize`/`enumerate` only for genuinely list-like content (contribution lists, algorithm steps).
- Every result number must be attributed: "as reported in \cite{guo2025qgear}" or in a table sourced from it.
- Section labels: prefix with the chapter short-name to avoid collisions: `\label{sec:qgear:design}`, `\label{fig:qgear:scaling}`, `\label{tab:nisq:hw}`, `\label{eq:qml:vqdp}`, `\label{alg:deal}`. Background sections use `sec:bg:<topic>` (see the list in the Chapter II assignment) so other chapters can reference them.
- Refer to chapters/sections/figures/tables/equations only with `\cref{}` / `\Cref{}` (never hard-coded numbers).

## TTU formatting rules you must respect inside chapter text

- **Table titles above tables** (`\begin{table}[htbp]\caption{...}\label{...}\centering ... \end{table}` — caption FIRST). **Figure titles below figures** (caption LAST). Use `[htbp]`, never `[H]` unless unavoidable.
- Every table and figure must be mentioned in the text *before* it appears (write the `\cref` sentence, then the float).
- Every figure needs a 1–2 sentence alt-text: put it as a LaTeX comment `% alt: ...` directly above `\begin{figure}` (a later pass will convert these to accessibility tags).
- Captions: sentence case, full sentence(s), end with a period. Captions that state numbers must say where they come from ("Data from \cite{...}." or "Schematic.").
- Tables ≥ 8 pt; use `booktabs` (`\toprule\midrule\bottomrule`), no vertical rules. Long tables: `longtable` with header repeated.
- Equations numbered with `equation`/`align` (numbers appear as (3.2)); refer to them with `\cref{eq:...}`.
- Headings: `\section`, `\subsection`, (rarely) `\subsubsection`. No `\section*`. Title Case for section titles. No dangling single subsections (if you have 4.1.1 you need 4.1.2).
- Colors: only the palette in `preamble.tex` (`cbBlue`, `cbOrange`, `cbGreen`, `cbRed`, `cbPurple`, `cbSky`, `cbGray`); plots must vary marker/line style as well as color (accessibility rule).
- Hyperlinks/URLs go in the bibliography, not in body text, except for repository URLs in the appendices (`\url{}`).
- No footnotes for citations. Footnotes allowed sparingly for remarks.

## Figures and tables (create them — they are required, not optional)

We do **not** have the papers' original image files. Instead create:
1. **Circuit diagrams** with `quantikz` (`\begin{quantikz} ... \end{quantikz}` inside a `figure`).
2. **Re-plotted data** with `pgfplots` using the numbers reported in the bibliography summary (e.g., QAOA vs DEAL success vs. layers; Q-GEAR time vs. qubits; VQT RMSE vs. batch). When you reconstruct a trend from a few reported points, the caption must say "Re-plotted from the values reported in \cite{...}; intermediate points are illustrative." Use `\begin{tikzpicture}\begin{axis}[...]` with `\addplot coordinates {...}`. Keep plots simple and compilable.
3. **Architecture / pipeline / threat-model schematics** with plain TikZ (nodes + arrows). Keep node text short.
4. **Tables** of hardware used (device, qubits, median CZ error, T1/T2), of results, of resource counts, and of comparisons with prior work — populated from the bibliography summary; unknown cells get `\todo{}` or "—".
Aim for 4–7 floats per research chapter, 3–5 in Background. Every float compiles (test it!).

Do not write `\includegraphics` for files that do not exist. If a figure truly needs an external image later, write a TikZ placeholder box with the intended content described inside it and a `\todo{replace with figure from paper X, Fig. N}`.

## Algorithms

Use `algorithm2e`: `\begin{algorithm}[htbp]\caption{...}\label{alg:...}\KwIn{...}\KwOut{...} ... \end{algorithm}`. Note algorithm2e's caption position is set by the package (top) — that is acceptable for algorithm floats.

## Citations

Only cite keys that exist in `bib/refs.bib` (run `grep "^@" bib/refs.bib` to list them). If you need a reference that is missing, add a complete BibTeX entry to **your own file** `bib/extra-chNN.bib` (NN = your chapter number; create it) — do not edit `refs.bib`. Mark uncertain fields with `% TODO`. Prefer canonical references already in refs.bib. Use `\cite{}` (numeric IEEE style); `\textcite{}`-style prose ("Farhi et al.~\cite{farhi2014qaoa}") is fine.

## Macros available (preamble.tex)

`\qgear \deal \qawa \qpie \vqt \shardq \nnqa \rubriq \cudaq \qiskit \qcrank` (product names), `\bigO{n}`, `\Hcost`, `\Hmix`, `\code{n}{k}{d}` → [[n,k,d]], `\ket{} \bra{} \expval{}` (physics), `\eps`, `\R \C \Z`, `\Tr`, `\poly`, `\argmin`, `\argmax`, theorem environments `theorem lemma proposition corollary definition assumption remark`, `\todo{...}`, `\authorshipstatement{...}`, `\aideclaration{...}`, `\SI{}{}`/`\num{}` (siunitx), `\qty`. Do not define new global macros in chapter files (local `\newcommand` inside a chapter is a collision risk); if you need one, prefix it with your chapter name (`\qgearFoo`).

## Compile check (mandatory before you finish)

From the repo root: `scripts/check_chapter.sh chapters/chNN-name.tex` (or `appendices/appX-name.tex`). It must print `OK` with no undefined references *within your chapter* (references to other chapters' labels will be undefined in isolation — that is expected; list them in your report). Fix all errors and any `Overfull \hbox` > 20 pt. Report the page count it prints.

## Deliverable report

When done, report: word count (`detex file | wc -w` or `texcount`), page count from the check script, list of floats, list of `\todo{}` markers, list of cross-chapter labels you referenced, and any new bib keys added.
