#!/bin/bash
# Build the ANNOTATED review copy: the thesis chapters with the <!--REV --> annotations
# rendered as visible coloured boxes.  Review artefact only — never the submitted PDF.
#
#   ./build_review.sh                 # default: the focus chapters
#   ./build_review.sh 01_introduction 06_test_and_fallback
#
# The submitted builds (latex_school/build_school.sh, latex/build.sh, latex/build_zh.sh)
# all strip HTML comment blocks, so the annotations are invisible to them; ./check_clean.sh
# proves it.
set -e
cd "$(dirname "$0")"

CHAPTERS="${*:-01_introduction 06_test_and_fallback 11_conclusion}"

tmp="$(mktemp -t thesisrevXXXX).md"
cat 00_front.md >> "$tmp"; printf '\n\n' >> "$tmp"
python3 rev2tex.py 00_abstract.md >> "$tmp"; printf '\n\n' >> "$tmp"
for c in $CHAPTERS; do
  python3 rev2tex.py "../en/$c.md" >> "$tmp"; printf '\n\n' >> "$tmp"
done
echo "chapters included: $CHAPTERS"

# ctexrep + fontset=macnew: same CJK setup latex/build_zh.sh already builds with.
# No --number-sections: the markdown headings carry the thesis's own numbering.
pandoc "$tmp" --metadata-file=review_meta.yaml -H review_header.tex \
  --top-level-division=chapter --toc --toc-depth=2 \
  --pdf-engine=xelatex -o thesis_review.pdf > build_review.log 2>&1 || {
    echo "FAILED — tail of build_review.log:"; tail -30 build_review.log; rm -f "$tmp"; exit 1; }
rm -f "$tmp"

pages=$(pdfinfo thesis_review.pdf 2>/dev/null | awk '/Pages/{print $2}')
boxes=$(grep -c '^<!--REV' 00_abstract.md $(for c in $CHAPTERS; do echo "../en/$c.md"; done) \
        | awk -F: '{s+=$2} END {print s}')
echo "OK: built thesis_review.pdf (${pages:-?} pages, ${boxes:-?} annotations)"
