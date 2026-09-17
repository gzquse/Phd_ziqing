#!/usr/bin/env bash
# Compile a single chapter (or appendix) file in isolation against ttuthesis.cls.
# Usage: scripts/check_chapter.sh chapters/ch03-qgear.tex
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
rel="${1:?usage: check_chapter.sh chapters/chNN-name.tex}"
name="$(basename "${rel%.tex}")"
mkdir -p "$here/thesis/build-check"
cd "$here/thesis"
# Per-chapter bibliographies (bib/extra-chNN.bib, see WRITING_GUIDE.md) are loaded alongside refs.bib.
extrabib=""
for f in "$here"/bib/extra-*.bib; do
  [ -e "$f" ] && extrabib="$extrabib\\addbibresource{$f}"$'\n'
done
cat > "build-check/check-$name.tex" <<TEX
\documentclass[dissertation,doublespacing,leftmargin15]{ttuthesis}
\input{preamble}
\title{Check build}\author{Ziqing Guo}
\addbibresource{$here/bib/refs.bib}
${extrabib}\begin{document}
\ttumainmatter
\input{$rel}
\ttureferences
\end{document}
TEX
export TEXINPUTS=".:$here/thesis:"
export BIBINPUTS=".:$here/bib:"
( cd build-check && latexmk -pdf -interaction=nonstopmode -halt-on-error -bibtex- -f "check-$name.tex" >"check-$name.log.txt" 2>&1 || true
  # run biber + two more passes explicitly so citations resolve
  biber "check-$name" >/dev/null 2>&1 || true
  pdflatex -interaction=nonstopmode -halt-on-error "check-$name.tex" >/dev/null 2>&1 || true
  pdflatex -interaction=nonstopmode -halt-on-error "check-$name.tex" >"check-$name.log.txt" 2>&1 || true )
log="build-check/check-$name.log"
if grep -q "^!" "$log"; then
  echo "=== ERRORS in $rel ==="; grep -A4 "^!" "$log" | head -40; exit 1
fi
echo "OK: $rel"
grep -E "Warning: (Citation|Reference) .* undefined" "$log" | sort -u | head -20 || true
grep -E "Overfull \\\\hbox \([0-9]{2,}" "$log" | head -5 || true
pdfinfo "build-check/check-$name.pdf" | grep Pages
