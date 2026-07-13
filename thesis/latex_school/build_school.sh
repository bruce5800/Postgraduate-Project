#!/bin/bash
# Build the University-of-Bristol-template thesis PDF.
# Pipeline: ../en/*.md --(preprocess+pandoc fragments, citations as biblatex)--> ch/*.tex,
# meta.yaml abstract --> abstract.tex, docs/references.bib minus notes --> refs_clean.bib,
# then pdflatex + biber. Edit the markdown chapters, not ch/*.tex.
set -e
cd "$(dirname "$0")"

CHAPTERS="01_introduction 02_background 03_model_methodology 04_unified_benchmark \
05_order_error 06_test_and_fallback 07_external_validity 08_exploratory_negatives \
09_theory 10_serving_case_study 11_conclusion"
APPENDICES="A_reproduction B_proof_details"

preprocess() {
  # same rules as latex/build.sh, plus raw "→" (pdflatex-safe via \ensuremath)
  sed -e '/<!--/,/-->/d' "$1" \
    | sed -E 's/^# (Chapter [0-9]+\.|Appendix [A-Z]\.) /# /' \
    | sed -E 's/^(#{2,3}) ([A-Z]\.)?[0-9]+(\.[0-9]+)* /\1 /' \
    | sed -e 's/≈/$\\approx$/g' -e 's/✓/$\\checkmark$/g' \
          -e 's/→/\\ensuremath{\\rightarrow}/g'
}

mkdir -p ch
for c in $CHAPTERS $APPENDICES; do
  preprocess "../en/$c.md" \
    | pandoc -f markdown -t latex --biblatex --syntax-highlighting=none \
        --top-level-division=chapter \
    | sed -e 's/\\def\\LTcaptype{none}//' -e 's/\\label{[^}]*}//g' \
    > "ch/$c.tex"
done
# ^ pandoc marks caption-less longtables with \LTcaptype{none}; KOMA's longtable
#   support evaluates that as a counter name and errors ("No counter 'none'").
#   Our tables carry no captions, so dropping the marker changes nothing.
echo "fragments: $(ls ch/*.tex | wc -l | tr -d ' ') chapters"

# abstract.tex from latex/meta.yaml's "abstract: |" block
python3 - <<'EOF'
import re, subprocess, pathlib
meta = pathlib.Path('../latex/meta.yaml').read_text()
m = re.search(r'^abstract: \|\n((?:  .*\n?)+)', meta, re.M)
text = '\n'.join(l[2:] for l in m.group(1).splitlines())
tex = subprocess.run(['pandoc', '-f', 'markdown', '-t', 'latex'],
                     input=text, capture_output=True, text=True, check=True).stdout
pathlib.Path('abstract.tex').write_text(tex)
EOF
echo "abstract.tex regenerated"

# refs_clean.bib = references.bib minus note fields (biblatex prints notes; ours are TODO markers)
python3 - <<'EOF'
import re, pathlib
bib = pathlib.Path('../../docs/references.bib').read_text()
bib = re.sub(r',?\s*note\s*=\s*\{[^{}]*\}', '', bib)
pathlib.Path('refs_clean.bib').write_text(bib)
EOF
echo "refs_clean.bib regenerated (note fields stripped)"

# word count (main-matter fragments only, per regulations it's the body count)
if command -v texcount >/dev/null 2>&1; then
  wc_total=$(texcount -total -sum -q ch/*.tex 2>/dev/null | awk '/Sum count/{print $NF}')
else
  # approximation: strip TeX commands/math and count words (verify with texcount before submission)
  wc_total="$(sed -E -e 's/\\[a-zA-Z]+(\[[^]]*\])?(\{[^{}]*\})?//g' -e 's/[{}$&%]//g' ch/*.tex \
    | wc -w | tr -d ' ') (approx.)"
fi
echo "\\newcommand{\\uobwordcount}{${wc_total:-TODO}}" > wordcount.tex
echo "word count: ${wc_total:-TODO}"

pdflatex -interaction=nonstopmode thesis.tex > build_school.log 2>&1 || {
  echo "pdflatex pass 1 FAILED — tail:"; grep -A3 '^!' build_school.log | head -30; exit 1; }
biber thesis >> build_school.log 2>&1 || {
  echo "biber FAILED — tail:"; tail -20 build_school.log; exit 1; }
pdflatex -interaction=nonstopmode thesis.tex >> build_school.log 2>&1 || true
pdflatex -interaction=nonstopmode thesis.tex >> build_school.log 2>&1 || {
  echo "pdflatex final pass FAILED — tail:"; grep -A3 '^!' build_school.log | head -30; exit 1; }

pages=$(pdfinfo thesis.pdf 2>/dev/null | awk '/Pages/{print $2}')
echo "OK: built thesis.pdf (${pages:-?} pages)"
# check the FINAL pass only (thesis.log), not the accumulated build_school.log
undef=$(grep -c 'Citation .* undefined' thesis.log || true)
[ "${undef:-0}" -gt 0 ] && echo "WARNING: $undef undefined citations" || echo "citations: all resolved"
