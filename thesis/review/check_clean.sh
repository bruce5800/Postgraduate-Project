#!/bin/bash
# Prove the annotations cannot leak into the submitted thesis.
#
# For each annotated chapter: run build_school.sh's exact preprocess + pandoc call on
# (a) the annotated file and (b) the same file with every REV block deleted, then diff
# the generated LaTeX.  Identical .tex => identical thesis.pdf.
set -e
cd "$(dirname "$0")"

CHAPTERS="${*:-01_introduction 02_background 03_model_methodology 04_unified_benchmark 05_order_error 06_test_and_fallback 07_external_validity 08_exploratory_negatives 10_serving_case_study 11_conclusion A_reproduction}"
status=0

# verbatim from latex_school/build_school.sh
preprocess() {
  sed -e '/<!--/,/-->/d' "$1" \
    | sed -E 's/^# (Chapter [0-9]+\.|Appendix [A-Z]\.) /# /' \
    | sed -E 's/^(#{2,3}) ([A-Z]\.)?[0-9]+(\.[0-9]+)* /\1 /' \
    | sed -e 's/≈/$\\approx$/g' -e 's/✓/$\\checkmark$/g' \
          -e 's/→/\\ensuremath{\\rightarrow}/g'
}
to_tex() {
  preprocess "$1" | pandoc -f markdown -t latex --biblatex --syntax-highlighting=none \
      --top-level-division=chapter
}

for c in $CHAPTERS; do
  f="../en/$c.md"
  bare="$(mktemp -t bareXXXX).md"
  python3 - "$f" > "$bare" <<'EOF'
import re, sys
sys.stdout.write(re.sub(r'<!--REV\n.*?\n-->\n*', '', open(sys.argv[1], encoding='utf-8').read(), flags=re.S))
EOF
  n=$(grep -c '^<!--REV' "$f" || true)
  if diff -q <(to_tex "$f") <(to_tex "$bare") > /dev/null; then
    echo "OK   $c  — $n annotations, generated LaTeX identical to un-annotated"
  else
    echo "FAIL $c  — annotations change the generated LaTeX:"; status=1
    diff <(to_tex "$f") <(to_tex "$bare") | head -20
  fi
  rm -f "$bare"
done

[ $status -eq 0 ] && echo "PASS: the submitted PDFs are unaffected by the annotations."
exit $status
