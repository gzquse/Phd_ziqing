# Defense slide deck

`index.html` is the complete Ph.D. defense deck for *Scaling Quantum Computing Across the Stack* (Ziqing Guo, Texas Tech University). It is one self-contained file: vanilla HTML, CSS and JavaScript, no external scripts, stylesheets, fonts or images. Every figure and chart is inline SVG or CSS, so the file works offline, from a USB stick, and as a claude.ai artifact.

- 68 slides (63 talk slides + 5 backup slides), each with speaker notes
- fixed 1920 x 1080 logical canvas, letterboxed into any window or phone
- Keynote-style "Magic Move" transitions between adjacent slides
- dark theme by default, light theme on `T` (initial theme follows the OS setting)

## Presenting

Open `index.html` in Chrome, Edge, Safari or Firefox (Chromium gives the smoothest morphs). Press `F` for fullscreen and `S` to open the presenter panel: it shows the current slide's notes, a running timer (click "reset timer" to restart) and the title of the next slide. The panel is part of the same window, so for a two-screen setup open the file twice, put one window on the projector in fullscreen and the other on the laptop with `S`; both follow the URL hash, so typing `#/23` in either window jumps that window to slide 23.

| Key | Action |
|---|---|
| `→` `Space` `PageDown` `N` `Enter` | next slide |
| `←` `PageUp` `Backspace` `P` | previous slide |
| `Home` / `End` | first / last slide |
| `O` or `Esc` | overview grid of every slide (click a thumbnail, or move with arrows and press Enter) |
| `S` | presenter notes panel with timer |
| `T` | toggle dark / light theme (remembered in `localStorage`) |
| `F` | fullscreen |
| `?` or `H` | help overlay |

Also: click or tap the right / left third of the screen, swipe left / right on touch screens, or scroll the mouse wheel (debounced). The URL hash `#/12` deep-links to slide 12 and is updated on every move, so a link or a bookmark reopens the deck at that slide.

## Exporting a PDF handout

File > Print (or `Ctrl/Cmd+P`), choose "Save as PDF", landscape, margins "None", and enable background graphics. The print stylesheet prints exactly one slide per page on a 1920 x 1080 px page (20 x 11.25 in) in the light theme with the UI hidden; 68 pages for the whole deck. Chrome's `--print-to-pdf` or Playwright's `page.pdf(prefer_css_page_size=True, print_background=True)` produce the same file headlessly.

## How the slides are built

Every slide is a `<section class="slide" data-id="..." data-morph-group="...">` inside `#stage`, in presentation order. Inside a slide the layout classes are:

- `.hd` with `.kicker` (small accent label) and `h1` (headline, `h1.xl` on dividers)
- `.body` fills the rest of the slide (`.body.top` aligns content to the top, `.center` centers it)
- `.card` / `.row` / `.col` for cards and grids, `.card.stat` + `.num` for big numbers, `.chips` / `.chip` for pills
- `ul.big` for talk bullets, `table.tbl` (`.sm`, `.xs`) for tables, `pre.code` for pseudo-code
- `svg.fig` for hand-written charts and diagrams (classes `.s1`..`.s6` / `.k1`..`.k6` are the six colour-blind-safe series fills / strokes, `.ax`, `.grid`, `.ref`, `.ln`, `.box`, `.wire`, `.gate` etc.)
- `.sec` bottom-left chapter label, `.rail` bottom-right "you are here" rail of the five stack layers
- `<aside class="notes">` speaker notes (hidden on the slide, shown in the presenter panel)

To add a slide, copy an existing `<section>` and place it where it should appear in the order; the counter, progress bar, overview grid and `#/N` links update automatically. `data-title="..."` overrides the title shown in the overview and notes panel.

## How morph ids work

Between two **adjacent** slides that share at least one token in `data-morph-group` (a divider slide lists two groups, e.g. `data-morph-group="qgear deal"`, to bridge sections), every element whose `data-morph="<id>"` appears on both slides is animated from its old position and size to its new one instead of fading. The engine uses FLIP with the Web Animations API (650 ms, `cubic-bezier(0.32,0.72,0,1)`):

- **plain text** (a leaf element with no background or border): translate + uniform scale from the font-size ratio, plus colour and opacity; if the text content differs it cross-fades while it moves
- **boxes** (`.bg` inside cards and chips, containers): translate + non-uniform scale, background and border colour
- **SVG `rect`, `circle`, `ellipse`, `line` and polyline `path` (`M ... L ...` only)**: the geometry attributes themselves are tweened, so bars grow or re-order, points slide along re-scaled axes and lines extend (a shorter polyline is padded with its last point); `fill` is animated too
- **other SVG nodes** (`text`, `g`): transform FLIP with `transform-box: fill-box`

Elements present only on the outgoing slide fade and scale to 0.97; elements only on the incoming slide fade in and rise 24 px with a 36 ms stagger in DOM order. A container that holds a matched element is not faded as a whole; the engine recurses into it so its other children fade individually. Ids must be unique within a slide. Navigating backwards morphs backwards automatically. Jumping to a non-adjacent slide, or to a slide in a different group, cross-fades. With `prefers-reduced-motion: reduce` every transition is a plain cross-fade.

Recurring ids in this deck: `L1-bg`..`L5-bg` and `L1-t`..`L5-t` are the five stack layers (cards on slide 3, agenda rows, RQ rows, contribution rows, the rail on every divider and takeaway, and the answers on slide 58); `sec` is the chapter label; `kicker` cross-fades the header label; chart ids are prefixed per chart (`qg-*` Q-GEAR time vs qubits, `dl-*` DEAL gains, `pp-*` VQT perplexity bars, `qe-*` QEC disturbance bars).

## Sources and conventions

All numbers come from `research/ziqing_guo_bibliography.md`; the thesis statement and research questions are quoted verbatim from `research/WRITING_GUIDE.md`. Charts that connect a few reported values with a scaling law (Q-GEAR time vs qubits, the nonlinear-wave cost model) say so in their footnote. Placeholders to fill in before the defense: the date ("Month DD, 2027") and the committee members on slides 1 and 62.

Design tokens live in `:root` at the top of the `<style>` block (`--bg`, `--fg`, `--acc*`, `--s1`..`--s6`); the light theme redefines them under `@media (prefers-color-scheme: light)` and `:root[data-theme="light"]`. Chart series colours were validated for colour-vision deficiency and contrast on both surfaces; every series also differs by marker shape and dash pattern.
