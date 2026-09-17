# Texas Tech University Graduate School — Thesis/Dissertation Formatting Requirements

Compiled 2026-09-16 for the purpose of writing a compliant LaTeX document class.

## 0. Sources consulted

| Source | URL | Notes |
|---|---|---|
| TTU Graduate School Formatting Manual, "Revised February 2026" (35 pp.) | https://www.depts.ttu.edu/gradschool/academic/thesis_diss/forms/2026-2027/Formatting_Manual_2026_Update.pdf | Authoritative. Sections: Document Preparation; Basic Formatting Requirements; Special Categories; Getting Help. Page refs below (p.N) are to this PDF. |
| Formatting Guidelines page | https://www.depts.ttu.edu/gradschool/academic/thesis_diss/defend_format_submit/formatting/FormattingGuidelines.php | States "Specifications in the following guide supercede style guide specifications." Fallback: Turabian 7th ed. (2007). |
| Templates page | https://www.depts.ttu.edu/gradschool/academic/thesis_diss/defend_format_submit/formatting/TD_Templates.php | Links 3 Word templates (below). States: "Currently the Graduate School does not supply an approved LaTEX template." and "using LaTEX does not remove your responsibility to make changes to your formatting when asked to do so by the Graduate School." |
| Word templates (MS Word 2007/2010) | …/formatting/TemplateFrontMatter_2021.docx, …/formatting/Template_MainText_2021.docx, …/formatting/Template_BackMatter_2021.docx | **Could not be downloaded from this sandbox** (proxy egress policy returns 403 for www.depts.ttu.edu from curl; WebFetch sees only binary). /home/claude/research/ttu_templates/ is therefore empty. The exact template wording was instead recovered from three May 2026 TTU documents produced with the Word template (see §6). |
| ETD Checklist (Updated SP2024) | https://www.depts.ttu.edu/gradschool/academic/thesis_diss/forms/2023-2024/ETDChecklistUpdatedSP2024.pdf | The reviewer's 42-item checklist; reproduced in §17. |
| Format/Defend/Submit hub | https://www.depts.ttu.edu/gradschool/academic/thesis_diss/defend_format_submit/DefendFormatSubmit.php | |
| Style Guides page | https://www.depts.ttu.edu/gradschool/academic/thesis_diss/defend_format_submit/formatting/StyleGuides.php | §15 |
| ETD info / ETD accounts | …/defend_format_submit/etd/etd_info.php, …/etd/etd.php | §14 |
| Real 2026 TTU documents in ThinkTech repository (title pages follow the Word template) | Li (PhD CS, May 2026, LaTeX-made) handle 2346/109249; Wilson (PhD Animal Science, May 2026, Word) 2346/109347; Latifi (PhD HTRM, May 2026, Word) 2346/109351; Meduri (MS CS, May 2026, Word) uuid fe9a3aef-5e83-45da-834a-55ac61a7e520 | https://ttu-ir.tdl.org/ (DSpace REST at /server/api/) |
| Community LaTeX templates | see §16 | |

Contact for formatting questions: Allison Belisle, Dissertation Supervisor, etd.gradschool@ttu.edu, 806.834.5163.

---

## 1. Paper size and margins (manual p.14)

- Paper size: not explicitly stated in the manual; US Letter (8.5 × 11 in) is universal practice and assumed by all TTU templates.
- **Left margin: 1.5 in OR 1.0 in** — either is allowed, but must be consistent throughout. (The ETD checklist item 26 still says "1.5 inch left margin; 1 inch top, right and bottom"; the 2026 manual allows 1.0 in as an alternative. Safest default for the class: `1.5in`, with a `1in` option.)
- **Top, right, bottom: 1.0 in.**
- **No mirror margins** (document is single-sided/one-side; even and odd pages identical).
- Everything — text, tables, figures, appendix material, page numbers — must sit within the margins. Oversized material: landscape page or continuation onto multiple pages (see §10).

## 2. Font (manual p.21)

- One font, one size, used consistently throughout (headings may differ in size/weight; see §8).
- Minimum **12 pt for serif** fonts (examples: Times New Roman, Cambria); minimum **10 pt for sans-serif** (Arial, Calibri). Recommend a standard serif or sans-serif face, not decorative.
- **Standard black** font colour. Hyperlinks (in references or anywhere) must be plain black text, not blue/underlined.
- Text inside tables may go down to **8 pt** minimum.
- Running header is **1 pt smaller** than body text (see §4).
- Page numbers: same font and size as body text.

## 3. Line spacing (manual p.21; ETD checklist 33–34)

- Body text: **double (2.0) or one-and-a-half (1.5)** — either, but consistent throughout, including Acknowledgments and Abstract.
- **Single-spacing is required within**: multi-line (2+ line) centered or side-margin subheadings; multi-line table titles and figure titles/captions; within each reference/bibliography entry; within each multi-line TOC/LOT/LOF entry; within multi-line abbreviation-list entries.
- **Body spacing (double or 1.5) between**: separate references; separate TOC/LOT/LOF entries; abbreviation entries.
- Block quotations: the manual is silent — follow the approved style guide (Turabian/APA/etc. all single-space or indent block quotes; class should offer a single-spaced, indented `quote`).
- Footnotes: size/spacing not specified by the manual — style guide governs. Footnotes at foot of page, numbered by chapter or consecutively; table/figure footnotes numbered separately from text footnotes (p.22).
- Paragraphs: first-line indent OR block style, per style guide, used consistently. Full justification is discouraged ("Do NOT use full justification unless your … software is sufficiently sophisticated … to keep your text from appearing with large gaps") — TeX qualifies; either ragged-right or justified is acceptable if there are no large gaps.

## 4. Page numbering and running header (manual p.15; ETD checklist 12–24)

Page numbers:
- **Title page: no number. Copyright page: no number.** (Both are counted; the copyright page is effectively page i but never prints a number.)
- **Front matter: lowercase Roman numerals**, first printed number is **ii** on the Acknowledgments page (or on the first page of the Table of Contents if there is no Acknowledgments). Continues consecutively through the last front-matter page.
- **Main text and back matter: Arabic numerals starting at 1 on the first page of Chapter 1**, consecutive through references and appendices (no restart).
- Position: **bottom of page, centered, within the bottom margin, 0.5 in from the bottom edge** of the paper. Centered on the physical page.
- Same font and size as body text; **no dashes or other decoration** around the number.

Running header:
- Appears on **every page from the Acknowledgments (page ii) through the end of the document** — i.e., all pages except title and copyright pages. It does appear on chapter-opening pages.
- Text: **`Texas Tech University, <Student Full Name>, <Month Year>`** (e.g., `Texas Tech University, Gaoxiang Li, May 2026` — no comma between month and year in the header).
- **Right-aligned to the right margin**, **0.5 in from the top edge** of the page (i.e., in the top margin), same typeface as body text, **1 pt smaller** than body text (12 pt body → 11 pt header). No rule line.

## 5. Required order of front matter (manual p.17; ETD checklist 8)

| # | Page | Required? | Page number | Header | In TOC? |
|---|---|---|---|---|---|
| 1 | Title page | Required | none | no | no |
| 2 | Copyright page | Required ("All theses/dissertations must have a copyright page") | none | no | no |
| 3 | Acknowledgments | Optional; max 2 pages | ii | yes | yes |
| 4 | Table of Contents | Required | next roman | yes | no (does not list itself) |
| 5 | Abstract | Optional but strongly recommended; 2–3 paragraphs; no subheadings; no citations | roman | yes | yes |
| 6 | List of Tables | Required if more than two tables | roman | yes | yes |
| 7 | List of Figures | Required if more than two figures | roman | yes | yes |
| 8 | List of Abbreviations / Symbols / Nomenclature (use only one term as the title) | As needed; always the **last** front-matter page | roman | yes | yes |
| (9) | Preface | Very rare; if used it immediately precedes Chapter I, keeps roman numbering, is titled "Preface", and is listed in TOC | roman | yes | yes |

Note the order **Acknowledgments → Table of Contents → Abstract** (Abstract comes after the TOC at TTU, unlike many schools). Observed real documents follow this: TOC entries "Acknowledgments ii / Abstract … / List of Tables … / List of Figures …".

Front-matter heading text as rendered by the Word template (observed in Wilson, Latifi, Meduri 2026, all Word-produced): **ACKNOWLEDGMENTS**, **TABLE OF CONTENTS**, **ABSTRACT**, **LIST OF TABLES**, **LIST OF FIGURES** — centered, all caps, at the top of the page, styled as a level-1 (chapter-level) heading. The manual names them in title case ("Acknowledgments", "Table of Contents", "Abstract", "List of Tables", "List of Figures", "List of Abbreviations") and does not mandate caps; but the ETD checklist requires that the references heading be "a level 1 heading, formatted the same way as others" and that TOC entries match the heading style in the document, so front-matter headings must use the same style as chapter titles. The class should make heading case a single switch (default: all caps, matching the Word template output). Spelling: the manual uses "Acknowledgments" (Latifi's "ACKNOWLEDGEMENTS" was accepted, so either is tolerated; default to "Acknowledgments").

## 6. Title page — exact wording and layout (manual p.17; Word template as rendered)

Manual requirements: title (**≤ 238 characters including spaces**, NOT bold); student name followed by previously earned degree abbreviations exactly as on the transcript (undergraduate first, e.g. "Jane Q. Doe, B.S., M.S."); whether the document is a Thesis or Dissertation; the degree-granting department/major; the "Submitted … in partial fulfillment" text exactly as in the template; the degree name in ALL CAPS; committee members with the chair designated beneath his/her name; the Dean's Representative is NOT listed; the Graduate School dean's name and title; month and year of graduation; **no signature lines** on the electronic copy. Everything centered, single-spaced within blocks, one page.

### Exact text — Dissertation (as produced by TemplateFrontMatter_2021.docx; verified identical in Wilson 2026 and Latifi 2026, and mirrored by Meduri 2026):

```
<Title of the Dissertation, Mixed Case, Not Bold,
Wrapped Onto Additional Lines If Needed>

by

<First Middle Last, B.S., M.S.>

A Dissertation

In

<Computer Science>

Submitted to the Graduate Faculty
of Texas Tech University in
Partial Fulfillment of
the Requirements for
the Degree of

DOCTOR OF PHILOSOPHY

Approved

<Chair Name, Ph.D.>
Chair of the Committee

<Member Name, Ph.D.>

<Member Name, Ph.D.>

<Member Name, Ph.D.>

Mark Sheridan, Ph.D.
Dean of the Graduate School

May, 2026
```

Concrete instance (Wilson, PhD Animal Science, May 2026, Word template):

```
Liver Abscess Effects on Rumen Histology, Morphology, and Feeding Behavior in
Beef–Dairy Cattle, Surveillance of Salmonella Enterica Throughout the Beef Carcass, and
Characterization of Salmonella Enterica Using MALDI-TOF

by

Reese Andrew Wilson, M.S.

A Dissertation

In

Animal Science

Submitted to the Graduate Faculty
of Texas Tech University in
Partial Fulfillment of
the Requirements for
the Degree of

DOCTOR OF PHILOSOPHY
Approved

Dale R. Woerner, Ph.D.
Chair of the Committee

Bradley J. Johnson, Ph.D.

Blake A. Foraker, Ph.D.

T. G. Nagaraja, Ph.D.

Nikki Shariat, Ph.D.

Mark Sheridan, Ph.D.
Dean of the Graduate School

May, 2026
```

### Exact text — Master's Thesis (Meduri, MS Computer Science, May 2026, Word template):

```
Patient-Adaptive Seizure Prediction via Autonomic Phenotyping and Neuro-Symbolic
AI Confidence Modulation

by

Jahnavi Meduri M.S.

A Thesis

In

Computer Science

Submitted to the Graduate Faculty
of Texas Tech University in
Partial Fulfillment of
the Requirements for
the Degree of

MASTER OF SCIENCE

Approved

Bashir I. Morshed Ph.D.
Chair of the Committee

Tianxi Ji Ph.D.

Mark Sheridan Ph.D.
Dean of the Graduate School

May, 2026
```

Details to encode in the class:
- Line "by" is lowercase; "In" is capitalized (Word template). The LaTeX-produced Li 2026 dissertation omitted "by" and used lowercase "in" and was still accepted, but the Word template form should be the default.
- Fixed five-line block, line breaks exactly: `Submitted to the Graduate Faculty` / `of Texas Tech University in` / `Partial Fulfillment of` / `the Requirements for` / `the Degree of`.
- Degree in caps: `DOCTOR OF PHILOSOPHY`, `MASTER OF SCIENCE`, `MASTER OF ARTS`, `DOCTOR OF EDUCATION`, etc.
- `Approved` on its own line (no colon), then chair's name with `Chair of the Committee` directly beneath, then each remaining member on its own line separated by a blank line. No signature lines, no "Accepted".
- Dean block: current dean's name and `Dean of the Graduate School` (as of 2026: `Mark Sheridan, Ph.D.`; the checklist requires the current dean's name — make it a settable macro).
- Date: month and year of graduation. The Word template renders `May, 2026` (with comma; seen in Wilson and Meduri); Latifi's `May 2026` was also accepted. Default to `Month, Year`, with the running header using `Month Year` (no comma).
- Vertical spacing: the Word template spreads the blocks down the page with blank lines; the community class uses 14 pt gaps between blocks and 28 pt before the dean block and the date, all single-spaced and centered. Title page has no header and no page number.

## 7. Copyright page (manual pp.17–18; ETD checklist 9–12)

- Required for every thesis/dissertation.
- Content: either the word "Copyright" **or** the © symbol (never both), the year of the graduating semester, and the student's name: e.g. `Copyright 2026, Reese Andrew Wilson` (Word template form) or `©2026, Gaoxiang Li`.
- **Centered both horizontally and vertically** on an otherwise blank page. No page number, no running header.

## 8. Headings: chapters and subheadings (manual pp.21–22)

Chapter (top-level/major-division) headings:
- Each chapter starts on a new page. "Each new chapter should start on its own page and should have 'Chapter' and the number on the line above the chapter title." → two lines: `CHAPTER I` (or `Chapter 1`) then the title on the next line.
- Numbering style (Roman vs Arabic) and case are not prescribed by the manual; the Word template output uses centered ALL CAPS Roman: `CHAPTER I` / `INTRODUCTION` (Wilson, Latifi). LaTeX-made documents using `1. INTRODUCTION` or `1. Introduction` on one line were also accepted (Meduri, Li), but the two-line form is the manual's stated rule. Title must not be bold on the title page; chapter headings may be bold.
- All level-1 headings — front-matter sections, chapter titles, Notes, References/Bibliography, Appendix banners — must share the same formatting (ETD checklist 41).
- Major divisions: Notes (endnotes) if used; References/Bibliography; Appendix/Appendices.

Subheadings:
- Each level must be visually distinctive (centered vs. flush-left; bold / italic / underline vs. regular; serif vs. sans), and all subheadings at the same level identical. Avoid too many levels.
- A **decimal numbering system is optional**; if subheadings are decimal-numbered (1.1, 1.1.1), then **equations, figures and tables MUST also use decimal numbering** (Table 2.3, Figure 4.1, Eq. (3.2)). Conversely, if not numbering subheadings, use plain consecutive numbering for floats/equations.
- **Dangling-heading rule**: a subheading at the bottom of a page must be moved to the next page if fewer than two lines of text fit beneath it (set club/widow/penalties accordingly).
- Multi-line subheadings single-spaced.
- Subheadings appearing in the TOC must be the same levels in all chapters; no appendix subheadings in the TOC.

## 9. Table of Contents, List of Tables, List of Figures, List of Abbreviations (manual pp.18–20)

Table of Contents:
- Heading "Table of Contents" (rendered TABLE OF CONTENTS by the template). Lists every front-matter division except title, copyright, and the TOC itself; every chapter number and title; back-matter divisions (Notes, References/Bibliography, Appendix/Appendices with their titles).
- Subheadings optional; if included, same levels in all chapters; indented "in increments of tabs" from the chapter titles (a consistent step per level). No subheadings from within appendices.
- Spacing: double or 1.5 between entries (single spacing permitted between lesser sub-levels in a very long TOC); multi-line entries single-spaced with the wrapped text aligned under the entry text (not running into the page-number column).
- Page numbers right-aligned at the right margin. Leader dots optional, but if used in the TOC they must also be used in LOT/LOF (consistency).
- Front-matter page numbers appear in lowercase roman in the TOC (checklist 15). Entry wording/formatting must match the headings in the body (checklist 25).

List of Tables / List of Figures:
- Required if more than two tables / more than two figures. Titles "List of Tables", "List of Figures" (rendered LIST OF TABLES / LIST OF FIGURES).
- Entry = number + title (wording and capitalization exactly as in the body). **Do not repeat the word "Table"/"Figure"** on each line (i.e., "2.1  Summary of …", not "Table 2.1 Summary of …"). Titles should be unique (the list may show the full caption or a shortened form, but consistently).
- Single-space within multi-line titles (wrap aligned under title text); double/1.5 between entries; page numbers right-aligned; leaders match TOC.
- **Appendix tables and figures must be numbered, titled, and included** in these lists.

List of Abbreviations / Symbols / Nomenclature:
- Title uses **one** of those terms. Last page(s) of front matter. Alphabetized by abbreviation/symbol. Single-space within a multi-line explanation; double/1.5 between entries. (A glossary placed in the back matter is treated as an appendix: alphabetized, single-spaced, hanging indent, p.26.)

## 10. Tables, figures, equations, music examples (manual pp.22–24)

Tables:
- Every table has a unique number and title, **title ABOVE the table**. Numbered in order of first mention; each table must be mentioned in the text before it appears; placed in the text near the mention if it is discussed there.
- Font inside tables ≥ 8 pt where possible. Tables must be real tables (not images/screenshots), with designated header row(s) for accessibility.
- Multi-page tables: repeat the column headings on each page and title continuation pages "Table 4.1. Continued" (number then "Continued").
- Oversized: landscape-oriented page (page number still at the bottom center of the portrait page position / within margins) or split across pages. Must fit within margins.
- Caption text format used in practice: `Table 2.1. Title text` (number followed by period).

Figures ("charts, graphs, code excerpts, maps, illustrations, photographs, lists of 4+ lines, etc."):
- Unique number and title; **title ABOVE or BELOW the figure, consistent throughout** — the ETD checklist (item 39) expects "figure titles are BELOW the figures", so default to below.
- Every figure needs **1–2 sentences of alt-text** (PDF accessibility). Mention in text before appearance; number in order of mention; oversized figures as for tables.
- Multi-line captions single-spaced.

Equations:
- Within margins; **equation numbers in parentheses at the right margin**; decimal numbering if subheadings are decimal-numbered; "Eq." abbreviation not needed; 1–2 sentences of alt-text (MathML tagging satisfies this in LaTeX).

Music examples: number and title **BELOW** the example; no List of Examples in the front matter; alt-text required.

## 11. Footnotes / notes / endnotes (manual p.22)

- Footnotes: at the foot of the page; numbered by chapter or consecutively through the document; table/figure footnotes numbered separately from text footnotes. Format (size, spacing) per style guide.
- Chapter notes: begin on a new page at the end of each chapter under the subheading "Notes".
- Endnotes: immediately after the last chapter, before References; start on a new page under the top-level heading "Notes"; listed in the TOC as its own section.

## 12. References / Bibliography (manual p.25; checklist 40–42)

- Title per style guide: "References", "Bibliography", "Literature Cited", "Works Cited", etc. (observed: REFERENCES, BIBLIOGRAPHY). Formatted as a level-1 heading identical to chapter headings; starts on a new page; listed in TOC.
- Placement: after the last chapter (and after Endnotes if any), **before the appendices**. In a multi-paper document, per-chapter reference lists are allowed and a comprehensive back-matter list may then be omitted (§13).
- **Single-space within each entry; body spacing (double or 1.5) between entries. Do not split an entry across pages.** Hyperlinks/DOIs/URLs as plain black text (no blue, no underline).
- Page numbering continues (Arabic) from the body. Citation style must follow an approved style guide; documents with no recognized citation format are not approved.

## 13. Appendices (manual pp.25–26)

- Placed after the References. Page numbering continues consecutively.
- Multiple appendices are lettered **A, B, C …**, each with a title; a **single appendix carries no letter** and is titled simply "Appendix".
- Appendix title formatted like a chapter title: "Appendix" (or "APPENDIX A") on one line and the title on the next, same style as chapter headings; listed in the TOC with title. Some documents use an "APPENDICES" divider; not required.
- All appendix material must fit within the margins without obscuring page numbers. All appendix tables and figures must be numbered, titled, and listed in the LOT/LOF (numbered A.1, A.2 … when lettered, or continuing the plain sequence for a single appendix). No appendix subheadings in the TOC.
- **No original signatures** (replace with the text "ORIGINAL SIGNATURE AVAILABLE UPON REQUEST"); redact personal identifying information (phone numbers, addresses, SSNs, specific hometowns) in appendices and Acknowledgments.
- The signed **AI Use Agreement**, if AI/LLM tools were used, goes in an appendix (§14).

Special categories (manual pp.27–29):
- Multi-paper/journal-article format: Chapter I must be an introduction explaining the whole document and rationale; one chapter per article (with abstract/introduction/methods/results/discussion subheadings as appropriate); a final (brief) summary/synthesis chapter; each chapter may have its own reference list; an **authorship statement** (and bibliographic reference if published/submitted) must appear under the chapter title of any co-authored/published chapter; student must be primary author or have had major roles; work must originate at TTU.
- Creative writing: Chapter I introduction, then the creative work(s); poems as subheadings within a chapter or grouped into chapters with header pages; short stories may have chapter header pages.
- Music composition / theatre arts: Introduction (Ch. I), Methodology (if required), the creative work as a chapter, Conclusion chapter, References.
- Foreign-language documents: formatting unchanged; wholly foreign-language documents may have major division headings in that language, partially foreign-language documents use English headings; abstract in English or dual-language.

## 14. PDF, accessibility, ETD submission, forms, fees (manual pp.6–9, 30–34; ETD pages)

Accessibility (effective Spring 2026): the PDF must pass WCAG 2.1 Level AA checks — document title and language set in metadata; real structural tags for headings (logical structure and reading order); descriptive alt-text on every figure/equation/music example; real (semantic) lists, columns, and TOC; simple tables with header rows, never images of tables; hyperlinks with descriptive text (never "click here"); contrast ≥ 4.5:1 for text and ≥ 3:1 for informative figure elements; figures must not rely on color alone (vary line styles/markers); long descriptions where needed. For LaTeX this means a tagged PDF (`\DocumentMetadata{tagging=on, lang=en-US, pdfstandard=UA-2 ...}` with LuaLaTeX, `\includegraphics[alt={...}]`, header-row table tagging); the community 2026 class validates with veraPDF for PDF/UA-2.

Submission format: **PDF** (unless a security/patent restriction applies). The manual's Word instructions (Save As → PDF, not "Save as Adobe PDF") exist only to preserve tags/alt-text. One document, one PDF (supplementary files may be uploaded separately). Fonts should be embedded (standard for pdfTeX/LuaTeX output).

ETD system: submit through Vireo at **https://ttu-etd.tdl.org** (log in with TTU eRaider). Five screens: verify personal information; license; document/committee information and release option (**No Delay / 1-Year / 3-Year / 6-Year Hold**); upload the PDF as "Manuscript in PDF" plus optional supplementary files; confirm. Reviewer returns a marked-up PDF if corrections are needed; student uploads a replacement and clicks "Corrections Completed". Approved documents cannot be edited. Publication in the TTU ThinkTech repository (https://ttu-ir.tdl.org) within ~3 months of graduation unless embargoed. Suggested file naming from the ETD info page: `LastName_FirstName_DissReview.pdf` (review draft) and `LastName_FirstName_Diss.pdf` / `..._Thesis.pdf` (final); Vireo itself stores the file as `LASTNAME-PRIMARY-YEAR.pdf`.

Required electronic forms (initiated by the department via Dynamic Forms): Master's — Defense Notification Form, Oral Defense and Thesis-Dissertation Approval Form, Final Document Approval Form; Doctoral — the same plus the Report of the Graduate Dean's Representative. Defense must be held by the semester deadline (see https://www.depts.ttu.edu/gradschool/academic/deadlines/).

Fee: one-time **$50.00 thesis-dissertation fee** (posted to the student account after the ETD is received; must be paid before the degree is awarded). No bound paper copies are required.

AI use: if AI/LLM tools were used, a signed **AI Use Agreement** (https://www.depts.ttu.edu/gradschool/academic/thesis_diss/forms/2023-2024/TTU_AI_Use_Agreement_for_Theses_and_Dissertations.pdf) must be submitted with the document (as an appendix), and a **declaration listing the tools and purposes must appear under the heading of each chapter where AI was used**. AI may only edit, not create content; may assist with data analysis/summaries but may not draw conclusions; AI may not be an author. Guidance: …/forms/2023-2024/AI_Guidance_for_TTU_Theses_and_Dissertations.pdf. Previously published own work must be cited (self-plagiarism). Google Docs is not recommended as the authoring tool.

## 15. Approved style guides (StyleGuides.php)

Graduate School manual rules supersede the style guide wherever they conflict. If the department specifies none, **Turabian (7th ed., 2007)** is required. Department mapping on the page (dated): APA — Marriage & Family Therapy, RHIM/Hospitality, Mass Communications, Psychology, HESS, College of Education; MLA — Theatre & Dance, English; Chicago — History, Rawls College of Business; CBE — (listed for History/Rawls on the page); Turabian — Physics (with a department-defined MS Word guide), Wind Science & Engineering; department-designated journal style — Animal & Food Sciences, HESS. Engineering/CS departments typically use IEEE or a journal style approved by the department; the community 2026 class defaults to IEEE numeric via biblatex.

## 16. Community LaTeX templates (none official)

| Repo / class | URL | Notes |
|---|---|---|
| **JLMicus/Texas-Tech-University-LaTeX-Thesis-and-Dissertation-Template** — class `ttuthesis2026.cls` (`\ProvidesClass{ttuthesis2026}[2026/08/22 v1.0]`, loads `report` 12pt oneside letterpaper) | https://github.com/JLMicus/Texas-Tech-University-LaTeX-Thesis-and-Dissertation-Template (branch `master`) | Most current (pushed 2026-08-26), written against the Feb-2026 manual; LuaLaTeX + `\DocumentMetadata{tagging=on}` for PDF/UA-2; TeX Gyre Termes 12 pt; `\ThesisSetup{...}` keys (title, first-name, last-name, credentials, department, degree, degree-type, month, year, committee, left-margin={1in|1.5in}, line-spacing={onehalf|double}, structure={chapters|sections}); macros `\ThesisTitlePage`, `\ThesisCopyrightPage`, `\ThesisAcknowledgments`, `\ThesisTableOfContents`, `\ThesisAbstract`, `\ThesisListOfTables`, `\ThesisListOfFigures`, `\ThesisAbbreviations`, `\ThesisMainMatter`, `\ThesisBibliography`, `\ThesisAppendices`; geometry `left=1in,right=1in,top=1in,textheight=9in,headsep=24.27pt,footskip=0.5in`; header 11 pt right-aligned "Texas Tech University, \textit{Name}, Month Year"; page number centered on the physical page; chapters "CHAPTER I" centered bold 14 pt uppercase; captions "Figure 1.1. Title" flush left single-spaced; IEEE biblatex; `docs/requirements-matrix.md` maps 77 manual requirements to implementation with page numbers. Title page text: title / by / name / "A Thesis|Dissertation" / In / department / the 5-line "Submitted…" block / DEGREE / Approved / chair + "Chair of the Committee" / members / dean + "Dean of the Graduate School" / Month Year. Includes example PDFs `TTU-Example-Dissertation.pdf`, `TTU-Example-Thesis.pdf`. |
| **michael12276/TTU-Thesis-and-Dissertation-Updated-Template** | https://github.com/michael12276/TTU-Thesis-and-Dissertation-Updated-Template | Zip-only (`Thesis_Template_TTU_MichaelBrown.zip`), pushed 2026-08-27; derived from Chris Monico's (TTU Math & Stats) accessible template with structure from Aaron Hill's; requires LuaLaTeX + TeX Live 2025 (Overleaf). |
| **c3h899/TTU-Thesis-Template-Unofficial** | https://github.com/c3h899/TTU-Thesis-Template-Unofficial (branch `main`) | Archive of Robert E. Byerly's (TTU Math) template; `thesis_template.tex` + `preamble.tex`, `Cover/TitlePage.tex` (title / by / "FirstName LastName, Degree. Held." / A Thesis / In / Department / Submitted-block / DEGREE / chair / "Chair of the Committee" / members / "Mark Sheridan" / "Dean of the Graduate School" / "GraduatingMonth, GraduatingYear"), copyright "© YEAR, FirstName LastName", double spacing, gray right header, LIST OF TABLES / LIST OF FIGURES headings. Last push 2022. |
| **ahill818/ttuthesis_temp** — class `ttuthes2015.cls` (`\LoadClass[oneside,openany,12pt]{book}`) | https://github.com/ahill818/ttuthesis_temp | Atmospheric Science MS template (2015); "CHAPTER n" uppercase centered with uppercase title beneath; copyright "Copyright #1, #2"; double spacing; fancyhdr right header. Dated (pre-2016 rules). |
| Overleaf gallery | https://www.overleaf.com/latex/templates/tagged/texas-tech-university → "There are no articles matching your tags"; search "texas tech" returns nothing relevant | No Overleaf TTU template exists. |

The Graduate School explicitly does not endorse any LaTeX template.

## 17. ETD Checklist (Updated SP2024) — reviewer's items, verbatim

Title Page: (1) The title page matches the template. (2) The title is NOT in bold. (3) The student's previous degrees are listed after her or his name, starting with the undergraduate degree. (4) The chair of the committee is clearly designated. (5) The Dean's Representative is NOT listed. (6) The graduation semester is correct. (7) The Graduate Dean's name is correct.
Front Matter: (8) The front matter is in the correct order. (9) The copyright information is centered on the page, between both the top and bottom and left and right margins. (10) Either the copyright symbol is used OR the word "copyright" is used, but NOT both. (11) The correct copyright symbol is used. (12) The copyright page is unnumbered. (13) Page numbering begins with "ii" on either the acknowledgements page, or, if there is not an acknowledgements, on the first page of the Table of Contents. (14) The front matter is numbered using lowercase Roman numerals (ii, iii, etc.). (15) The front matter page numbers are lowercase in the table of contents.
Headers/Page Numbers: (16) The main text is numbered using Arabic numerals (1,2,3, etc.). (17) All page numbers are centered at the bottom of the page, 0.5 inches above the bottom of the page. (18) Page "1" is the first page of the first chapter. (19) The running header starts on page ii. (20) The running header is 0.5 inches from the top of the page. (21) The font of the running header is the same font type as the main text. (22) The font of the running header is 1 point size smaller than the main text. (23) The running header is aligned with the right margin. (24) The running header contains: Texas Tech University, the student's full name, the correct semester.
Table of Contents: (25) The headings are formatted the same way in the table of contents as they are in the main document.
Margins: (26) The margins of the entire document (including front matter) are: 1.5 inch left margin; 1 inch top, right and bottom.
Acknowledgements: (27) professional in tone and appropriate in content; (28) [needs editing]; (29) no more than 2 pages; (30) spaced the same way as the main text.
Main Body: (31) clear heading hierarchy; (32) headings formatted consistently; (33) line spacing consistent throughout (including acknowledgements and abstract); (34) line spacing is correct (either 1.5X or 2X); (35) document, in-text citations and bibliography follow the appropriate style guide; (36)–(37) [language/editing].
Tables and Figures: (38) The table titles are ABOVE the tables. (39) The figure titles are BELOW the figures.
References: (40) formatted correctly and consistent with the chosen style guide; (41) The title of the bibliography/references section is a level 1 heading, formatted the same way as others; (42) The page numbers are contiguous with the body of the document.

## 18. Implementation checklist for the LaTeX class (derived)

1. `\LoadClass[12pt,oneside,letterpaper]{report}` (or `book` with `openany`); `geometry`: `left=1.5in` (option `leftmargin=1in`), `right=1in, top=1in, bottom=1in`, `headsep` so header baseline sits 0.5 in from top edge, `footskip` so page number sits 0.5 in from bottom edge, `includehead=false, includefoot=false`; no twoside/mirror margins.
2. Fonts: 12 pt serif default (Times-like), black; header 11 pt; captions normal size; tables may drop to 8 pt.
3. `setspace`: `\onehalfspacing` or `\doublespacing` option; single-spacing in captions, bib entries, multi-line headings, TOC/LOT/LOF entries, abbreviation list, block quotes.
4. `fancyhdr` page styles: `ttuempty` (title, copyright: nothing), `ttumain` (right header `Texas Tech University, <Name>, <Month Year>`; centered footer page number, centered on the paper not the text block); make `plain` = `ttumain` so chapter openers keep the header.
5. Front-matter driver: title page → copyright (vertically centered, no number) → `\pagenumbering{roman}\setcounter{page}{2}` at Acknowledgments (or TOC) → TOC → Abstract → LOT (if >2) → LOF (if >2) → Abbreviations (last) → `\pagenumbering{arabic}` at Chapter 1.
6. Title page macro emitting exactly the §6 text with `\ifthesis`/`\ifdissertation` switching "A Thesis"/"A Dissertation", `\MakeUppercase{degree}`, chair + "Chair of the Committee", member list, dean + "Dean of the Graduate School", "Month, Year". Title never bold; enforce ≤238 chars with a warning.
7. Level-1 heading instance shared by chapters, front-matter sections, References and Appendix banners: centered, (default) uppercase, two-line `CHAPTER I` / TITLE with option for Arabic; new page each. Subheading levels distinct and consistent; `\clubpenalty=\widowpenalty=10000` and a heading `needspace` of ≥2 lines. Decimal numbering of sections implies decimal numbering of tables/figures/equations (`\numberwithin`).
8. `caption`: tables `position=above`, figures `position=below`, label format `Table 2.1.` (period), single-spaced, flush-left or centered consistently; `longtable` continuation caption "Table 2.1. Continued" with repeated headers; equation numbers `(2.1)` at right margin.
9. TOC/LOT/LOF: level-1 entries un-indented, subsections indented by a fixed tab step per level, page numbers flush right, dot leaders (all-or-none across all lists), single-spaced multi-line entries with body spacing between entries; LOT/LOF entries show number + title without the word "Table"/"Figure"; front-matter entries and Appendix titles included; no appendix subsections.
10. Bibliography: level-1 heading (style-guide title), single-spaced entries with 1.5/2× between (`\bibitemsep`), `\interlinepenalty=10000` to prevent splitting entries, `hyperref[hidelinks]` so URLs print black; supports per-chapter `refsection`s for multi-paper format.
11. `\appendix`: single appendix unlettered ("APPENDIX"), multiple lettered ("APPENDIX A" + title), chapter-style banner, floats numbered A.1…, listed in LOT/LOF; TOC entry with title.
12. Accessibility: LuaLaTeX + `\DocumentMetadata{tagging=on, lang=en-US, pdfversion=2.0, pdfstandard=UA-2}` (or at least `pdfstandard=UA-1` on a recent TeX Live), `hypersetup{pdftitle,pdfauthor,pdflang}`, `\includegraphics[alt={…}]`, `\tagpdfsetup{table/header-rows={1}}`, real `itemize/enumerate`, descriptive link text; validate with veraPDF.
13. Provide a `\aideclaration{...}` helper for the under-chapter-heading AI disclosure and an `\authorshipstatement{...}` for multi-paper chapters.

## 19. Known gaps / caveats

- The three official Word templates could not be downloaded from this environment (host blocked for direct downloads; WebFetch cannot parse .docx). Their rendered wording was reconstructed from three May-2026 TTU documents produced with them, which agree with each other line-for-line on the title page and headings; minor observed variance: date `May, 2026` (2 docs) vs `May 2026` (1 doc); `ACKNOWLEDGMENTS` vs `ACKNOWLEDGEMENTS`. Download the .docx files from a normal network to confirm block spacing and any embedded instructions.
- The manual leaves case/boldness/centering of chapter headings and front-matter headings to the style guide; the Word-template convention (centered, all caps, "CHAPTER I") is what the checklist's "matches the template"/"formatted the same way as others" items are judged against, so it is the safest default.
- The ETD checklist (2024) still lists the 1.5 in left margin only; the 2026 manual allows 1.0 in. Provide both, default 1.5 in.
- Block-quotation and footnote typography are governed by the department's style guide, not the Graduate School.
