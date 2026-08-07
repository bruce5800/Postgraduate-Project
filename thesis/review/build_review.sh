#!/bin/bash
# Build the ANNOTATED review copy: original text left, annotation cards right, quoted
# spans underlined in the text with a matching inline id.  Review artefact only.
#
#   ./build_review.sh                 # default: the focus chapters
#   ./build_review.sh 01_introduction 06_test_and_fallback
#
# The submitted builds all strip HTML comment blocks, so the annotations are invisible
# to them; ./check_clean.sh proves it.
set -e
cd "$(dirname "$0")"

CHAPTERS="${*:-01_introduction 06_test_and_fallback 11_conclusion}"
echo "chapters included: $CHAPTERS"

python3 rev2tex.py $CHAPTERS > body.tex

xelatex -interaction=nonstopmode review_main.tex > build_review.log 2>&1 || {
  echo "FAILED — first error:"; grep -A4 '^!' build_review.log | head -30; exit 1; }
xelatex -interaction=nonstopmode review_main.tex >> build_review.log 2>&1 || true
mv -f review_main.pdf thesis_review.pdf

pages=$(pdfinfo thesis_review.pdf 2>/dev/null | awk '/Pages/{print $2}')
boxes=$(grep -c '^<!--REV' 00_abstract.md $(for c in $CHAPTERS; do echo "../en/$c.md"; done) \
        | awk -F: '{s+=$2} END {print s}')
marks=$(grep -o '\\revhlid' body.tex | wc -l | tr -d ' ')
over=$(grep -c 'Overfull \\[hv]box' build_review.log || true)
echo "OK: thesis_review.pdf — ${pages:-?} pages, ${boxes:-?} annotations, ${marks} quotes underlined in text, ${over} overfull boxes"
