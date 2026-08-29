#!/bin/bash
# Build the University-of-Bristol-template thesis PDF.
# Pipeline: ../en/*.md --(preprocess+pandoc fragments, citations as biblatex)--> ch/*.tex,
# meta.yaml abstract --> abstract.tex, docs/references.bib minus notes --> refs_clean.bib,
# then pdflatex + biber. Edit the markdown chapters, not ch/*.tex.
set -e
cd "$(dirname "$0")"

CHAPTERS="01_introduction 02_background 03_model_methodology 04_unified_benchmark \
05_order_error 06_test_and_fallback 07_external_validity 08_exploratory_negatives \
10_serving_case_study 11_conclusion"
APPENDICES="A_reproduction"
# (09_theory and B_proof_details were cut from the thesis 2026-07-27 — see
#  docs/T1_WITNESS_GAP.md; theory lives in the companion paper, outlook in §10.2.)

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

# Appendix A.2 contains long monospaced script/output paths. Pandoc gives its four
# columns equal widths and \texttt does not normally wrap, so the columns overprint.
# Keep the Markdown as the source of truth, then tailor only this generated longtable:
# give the path columns more room, shrink the table slightly, and allow code to wrap.
python3 - <<'EOF'
from pathlib import Path

path = Path('ch/A_reproduction.tex')
tex = path.read_text()
section = tex.index(r'\section{\texorpdfstring{Figure / table')
table_start = tex.index(r'\begin{longtable}', section)
table_end = tex.index(r'\end{longtable}', table_start)
block = tex[table_start:table_end]

def code_to_path(text):
    r"""Convert Pandoc's escaped \texttt{...} cells to breakable \path|...|."""
    marker = r'\texttt{'
    out = []
    cursor = 0
    while True:
        start = text.find(marker, cursor)
        if start < 0:
            out.append(text[cursor:])
            return ''.join(out)
        out.append(text[cursor:start])
        i = start + len(marker)
        content_start = i
        depth = 1
        while i < len(text) and depth:
            if text[i] == '\\':
                i += 2
                continue
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
            i += 1
        content = text[content_start:i - 1]
        content = content.replace(r'\_', '_').replace(r'\{', '{').replace(r'\}', '}')
        # Leave entries containing other LaTeX commands (for example \textless{}) alone.
        if '\\' in content:
            out.append(text[start:i])
        else:
            out.append(r'\path|' + content + '|')
        cursor = i

block = code_to_path(block)

old_width = r'p{(\linewidth - 6\tabcolsep) * \real{0.2500}}'
for width in ('0.2400', '0.2900', '0.3400', '0.1300'):
    block = block.replace(
        old_width,
        rf'p{{(\linewidth - 6\tabcolsep) * \real{{{width}}}}}',
        1,
    )

table_setup = (
    r'\footnotesize' + '\n'
    r'\linespread{1}\selectfont' + '\n'
    r'\setlength{\tabcolsep}{3pt}' + '\n'
)
block = table_setup + block
tex = tex[:table_start] + block + tex[table_end:]

# Apply the same safe path conversion to ordinary inline filenames in the appendix.
# Compact verbatim blocks locally so long annotated commands stay inside the margin.
tex = code_to_path(tex)
tex = tex.replace(
    r'\begin{verbatim}',
    '{\\footnotesize\\linespread{1}\\selectfont\n' + r'\begin{verbatim}',
)
tex = tex.replace(r'\end{verbatim}', r'\end{verbatim}' + '\n}')
path.write_text(tex)
EOF
echo "appendix A.2 table: wrapping and column widths applied"

echo "fragments: $(ls ch/*.tex | wc -l | tr -d ' ') chapters"

# abstract.tex from latex/meta.yaml's "abstract: |" block
python3 - <<'EOF'
import re, subprocess, pathlib
meta = pathlib.Path('../latex/meta.yaml').read_text().splitlines()
# The block runs to the first non-blank line that is not indented; blank lines are part
# of it (an earlier regex stopped at the first blank line and silently dropped every
# paragraph after the opening one).
start = meta.index('abstract: |') + 1
body = []
for line in meta[start:]:
    if line.strip() == '':
        body.append('')
    elif line.startswith('  '):
        body.append(line[2:])
    else:
        break
text = '\n'.join(body).strip('\n') + '\n'
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

# word count: body chapters ONLY — ch/*.tex would sweep in the appendix, but the regulations
# count the body. texcount if it is installed; otherwise count the words pandoc actually
# renders from the same chapters, which is far closer than stripping TeX with a regex.
if command -v texcount >/dev/null 2>&1; then
  body_tex=""; for c in $CHAPTERS; do body_tex="$body_tex ch/$c.tex"; done
  wc_total=$(texcount -total -sum -q $body_tex 2>/dev/null | awk '/Sum count/{print $NF}')
else
  wc_total=$(for c in $CHAPTERS; do sed -e '/<!--/,/-->/d' "../en/$c.md"; done \
    | pandoc -f markdown -t plain --wrap=none 2>/dev/null | wc -w | tr -d ' ')
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
