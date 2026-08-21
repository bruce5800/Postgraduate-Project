#!/bin/bash
# Build the paper PDF from the markdown drafts in ../ (docs/paper/*.md).
# PRIMARY TARGET: TALG Empirical Track (JEA's successor) — acmart `manuscript`
# review format (talg_main.tex). itcs_main.tex (LIPIcs) is kept for reference /
# a possible arXiv layout but is no longer built by default.
# Same philosophy as the thesis builds: EDIT THE MARKDOWN, NOT ch/*.tex.
# Pipeline: strip comments (author notes), strip heading numbers (LaTeX
# renumbers), map [Choo24]-style labels to \cite{bibkey}, pandoc -> section
# fragments, bibtex ACM-Reference-Format over note-stripped references.bib.
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
    'Bor18':  'borodin2018experimental', 'MY11': 'mahdianyan2011',
    'CJKL22': 'canonne2022tolerance',  'VV11':   'valiant2011unseen',
    'JHW18':  'jiao2018l1',
    'GR17':   'gupta2017pac',          'Bal20':  'balcan2020datadriven',
    'Wald47': 'wald1947sequential',    'BCJG25': 'bhattacharyya2025product',
    'ASSS25': 'antoniadis2025switching', 'CD26': 'cui2026skirental',
    'MT04':   'mannortsitsiklis2004',  'KCG16': 'kaufmann2016complexity',
    'DLL11':  'dudik2011doubly',       'CJS25': 'choo2025fractional',
    'Hoe63':  'hoeffding1963probability', 'Ser74': 'serfling1974probability',
}
alt = '|'.join(LABEL2KEY)
LABEL_RE = re.compile(r'\[((?:%s)(?:,\s*(?:%s))*)\]' % (alt, alt))

def strip_comments(text):
    """Delete HTML comment blocks (author notes, REV annotations).

    A comment block written *inside* a paragraph is preceded by a blank line but
    followed immediately by prose; deleting only its own lines would leave that blank
    line behind and split the paragraph in the PDF.  So when prose resumes right after
    the block, the preceding blank line(s) go too and the paragraph stays whole.
    """
    lines, out, i = text.split('\n'), [], 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith('<!--'):
            j = i
            while j < len(lines) and '-->' not in lines[j]:
                j += 1
            if j < len(lines) and not lines[j].split('-->', 1)[1].strip():
                if j + 1 < len(lines) and lines[j + 1].strip():   # prose resumes
                    while out and not out[-1].strip():
                        out.pop()
                i = j + 1
                continue
        out.append(re.sub(r'<!--.*?-->', '', lines[i]))
        i += 1
    return re.sub(r'<!--.*?-->', '', '\n'.join(out), flags=re.S)


def preprocess(text):
    text = strip_comments(text)
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
    # figure paths in the markdown are relative to paper/*.md; pdflatex runs in
    # paper/latex/, from which ../../results/ already resolves correctly.
    return tex

FILES = ['00_abstract_intro', '01_setup', '02_unified_benchmark', '03_order_error',
         '04_test_and_fallback', '05_external_validity', '06_theory',
         '07_serving_related_conclusion', '08_appendix']
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

bib = pathlib.Path('../../docs/references.bib').read_text()
bib = re.sub(r',?\s*note\s*=\s*\{[^{}]*\}', '', bib)   # notes are internal TODO markers
pathlib.Path('refs_clean.bib').write_text(bib)
print('refs_clean.bib regenerated')
EOF

MAIN=${1:-talg_main}
pdflatex -interaction=nonstopmode "$MAIN.tex" > build_paper.log 2>&1 || {
  echo "pdflatex pass 1 FAILED — tail:"; grep -A3 '^!' build_paper.log | head -30; exit 1; }
bibtex "$MAIN" >> build_paper.log 2>&1 || {
  echo "bibtex FAILED — tail:"; tail -20 build_paper.log; exit 1; }
pdflatex -interaction=nonstopmode "$MAIN.tex" >> build_paper.log 2>&1 || true
pdflatex -interaction=nonstopmode "$MAIN.tex" >> build_paper.log 2>&1 || {
  echo "pdflatex final pass FAILED — tail:"; grep -A3 '^!' build_paper.log | head -30; exit 1; }

pages=$(pdfinfo "$MAIN.pdf" 2>/dev/null | awk '/Pages/{print $2}')
echo "OK: built $MAIN.pdf (${pages:-?} pages)"
undef=$(grep -c 'Citation .* undefined' "$MAIN.log" || true)
[ "${undef:-0}" -gt 0 ] && echo "WARNING: $undef undefined citations" || echo "citations: all resolved"
