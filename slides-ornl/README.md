# ORNL seminar deck (modular)

`index.html` is the 45-minute ORNL research-seminar cut of the defense deck — **40 slides: 32 in the main run (five of them section dividers) and 8 backups** — weighted toward quantum–HPC integration: Q-GEAR on Perlmutter, GPU knitting in ShardQ, CUDA-Q inside the RubriQ training loop, the nonlinear-wave cost model, and a closing slide on how the stack maps onto OLCF / Frontier. Same engine, theme, Magic-Move transitions and keyboard controls as `../slides/`; see that README for presenting and printing.

**Do not edit `index.html` by hand — it is generated.** The deck is a composition described in `deck.json`; rebuild with

```bash
python3 scripts/build_deck.py slides-ornl/deck.json       # -> index.html + artifact.html
make ornl                                                  # the same, plus ornl-slides.pptx
```

## How the manifest works

`deck.json` is a list of slides. Each entry is one of:

| Entry | Meaning |
|---|---|
| `{"use": "<data-id>"}` | the defense slide with that `data-id` in `../slides/index.html`, verbatim (`qg-time`, `shardq`, …) |
| `{"use": "<data-id>", "set": {css: html}, "drop": [css …], "notes": "…", "group": "…", "title": "…", "id": "…"}` | the same slide with overrides: `set` replaces the innerHTML of the first element matching each CSS selector (inside the slide), `drop` removes matching elements (an entry may be `{"selector": ".card", "contains": "COMMITTEE"}` to remove only the match containing a string), `notes` replaces the speaker notes, `group` overrides `data-morph-group`, `title` the overview title, `id` the `data-id` |
| `{"module": "modules/<file>.html"}` | a new slide: one `<section class="slide" …>` in a file, using the same layout classes as the defense deck (`modules/ornl-fit.html` is the OLCF slide) |
| `{"comment": "…"}` | ignored — use it to mark sections and time budgets |

`sec_map` at the top renames the bottom-left chapter labels globally (`"III · Q-GEAR"` → `"Simulation · Q-GEAR"`), so dissertation chapter numbers never reach the seminar. Overrides run in headless Chromium, so inline SVG charts survive untouched, and the engine re-injects page numbers and the Double T for the new slide count.

**To readjust the talk:** move an entry between the main run and the backup block (the backups follow the `Thank you` slide and carry `"group": "backup"` so they cross-fade rather than morph), delete an entry, reorder entries, or pull in any other defense slide by its `data-id` (`grep 'data-id=' ../slides/index.html` lists them). Then rebuild. Adjacent slides morph when they share a `data-morph-group` token, exactly as in the defense deck, so a reordered run keeps its transitions wherever the groups still touch.

## Files

- `deck.json` — the manifest (edit this)
- `modules/ornl-fit.html` — the new "Where this stack meets OLCF" slide
- `index.html`, `artifact.html` — generated deck and its claude.ai artifact fragment
- `ornl-slides.pptx` — generated PowerPoint (native text boxes / shapes / pictures with Morph transitions; `python3 scripts/slides_to_pptx.py slides-ornl/index.html slides-ornl/ornl-slides.pptx`)

Placeholders still to fill: the date on the title slide ("2026 · date TBD").
