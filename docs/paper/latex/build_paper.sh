#!/bin/bash
# Build the ITCS/LIPIcs paper PDF from the markdown drafts in ../ (docs/paper/*.md).
# Same philosophy as the thesis builds: EDIT THE MARKDOWN, NOT ch/*.tex.
# Pipeline: strip comments (incl. author notes — required for double-blind), strip
# heading numbers (LaTeX renumbers), map [Choo24]-style labels to \cite{bibkey},
# pandoc -> section fragments, bibtex plainurl over note-stripped references.bib.
set -e
cd "$(dirname "$0")"
mkdir -p ch

python3 - <<'EOF'
import re, subprocess, pathlib

LABEL2KEY = {
    'KVV90':  'kvv1990ranking',        'FMMM09': 'feldman2009online',
    'JL14':   'jailletlu2014online',   'HK73':   'hopcroftkarp1973',
    'LV18':   'lykouris2018caching',   'WZ20':   'weizhang2020tradeoffs',
    'ACI22':  'aci2022mpd',            'Choo24': 'choo2024imperfect',
    'BEM26':  'bem2026testmatch',      'Chl21':  'chledowski2021caching',
    'Bor18':  'borodin2018experimental',
    'CJKL22': 'canonne2022tolerance',  'VV11':   'valiant2011unseen',
    'JHW18':  'jiao2018l1',
}
alt = '|'.join(LABEL2KEY)
LABEL_RE = re.compile(r'\[((?:%s)(?:,\s*(?:%s))*)\]' % (alt, alt))

def preprocess(text):
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    text = re.sub(r'^(#+) (\d+(?:\.\d+)*)\.?\s+', r'\1 ', text, flags=re.M)
    text = LABEL_RE.sub(lambda m: r'\cite{%s}' % ','.join(
        LABEL2KEY[l.strip()] for l in m.group(1).split(',')), text)
    for a, b in [('\u2248', r'$\approx$'), ('\u2713', r'$\checkmark$'),
                 ('\u2192', r'\ensuremath{\rightarrow}'), ('\u2212', '-'),
                 ('\u03c4', r'$\tau$'), ('\u03b7', r'$\eta$'), ('\u2113', r'$\ell$')]:
        text = text.replace(a, b)
    return text

def md2tex(md):
    r = subprocess.run(
        ['pandoc', '-f', 'markdown', '-t', 'latex', '--syntax-highlighting=none',
         '--top-level-division=section'],
        input=md, capture_output=True, text=True, check=True)
    tex = r.stdout.replace(r'\def\LTcaptype{none}', '')
    tex = re.sub(r'\\label\{[^}]*\}', '', tex)
    # md image paths are relative to docs/paper/; latex compiles from docs/paper/latex/
    tex = tex.replace('../../results/', '../../../results/')
    return tex

FILES = ['00_abstract_intro', '01_setup', '02_unified_benchmark', '03_order_error',
         '04_test_and_fallback', '05_external_validity', '06_theory',
         '07_serving_related_conclusion']
for f in FILES:
    text = preprocess(pathlib.Path(f'../{f}.md').read_text())
    if f == '00_abstract_intro':
        # "# <title>" then "## Abstract" then "---" then "## Introduction ..."
        parts = re.split(r'^## ', text, flags=re.M)
        abstract = next(p for p in parts if p.startswith('Abstract'))
        abstract = abstract[len('Abstract'):].replace('\n---\n', '\n').strip()
        intro = next(p for p in parts if p.startswith('Introduction'))
        pathlib.Path('ch/abstract.tex').write_text(md2tex(abstract))
        pathlib.Path(f'ch/{f}.tex').write_text(md2tex('# ' + intro.strip()))
    else:
        pathlib.Path(f'ch/{f}.tex').write_text(md2tex(text))
print(f'fragments: {len(FILES)} sections + abstract')

bib = pathlib.Path('../../references.bib').read_text()
bib = re.sub(r',?\s*note\s*=\s*\{[^{}]*\}', '', bib)   # notes are internal TODO markers
pathlib.Path('refs_clean.bib').write_text(bib)
print('refs_clean.bib regenerated')
EOF

pdflatex -interaction=nonstopmode itcs_main.tex > build_paper.log 2>&1 || {
  echo "pdflatex pass 1 FAILED — tail:"; grep -A3 '^!' build_paper.log | head -30; exit 1; }
bibtex itcs_main >> build_paper.log 2>&1 || {
  echo "bibtex FAILED — tail:"; tail -20 build_paper.log; exit 1; }
pdflatex -interaction=nonstopmode itcs_main.tex >> build_paper.log 2>&1 || true
pdflatex -interaction=nonstopmode itcs_main.tex >> build_paper.log 2>&1 || {
  echo "pdflatex final pass FAILED — tail:"; grep -A3 '^!' build_paper.log | head -30; exit 1; }

pages=$(pdfinfo itcs_main.pdf 2>/dev/null | awk '/Pages/{print $2}')
echo "OK: built itcs_main.pdf (${pages:-?} pages)"
undef=$(grep -c 'Citation .* undefined' itcs_main.log || true)
[ "${undef:-0}" -gt 0 ] && echo "WARNING: $undef undefined citations" || echo "citations: all resolved"
