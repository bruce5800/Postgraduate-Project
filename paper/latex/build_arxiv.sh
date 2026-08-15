#!/bin/bash
# Assemble a self-contained arXiv submission bundle.
# Output: latex/arxiv/arxiv_submission.tar.gz  (tex + fragments + figs + .bbl)
# Differences vs the TALG submission build:
#   - documentclass options: nonacm (no ACM rights boilerplate), no `review`
#     line numbers — the public preprint look;
#   - figure paths rewritten to a bundled figs/ directory;
#   - the .bbl is generated locally and shipped (arXiv does not run bibtex);
#   - the local hyperxmp.sty stub is used ONLY for the local verification
#     compile and is excluded from the tarball (arXiv's TeX Live has the real one).
set -e
cd "$(dirname "$0")"

./build_paper.sh talg_main | tail -2   # refresh fragments + sanity-check the source

rm -rf arxiv
mkdir -p arxiv/ch arxiv/figs

sed -e 's/\\documentclass\[manuscript,screen,review\]{acmart}/\\documentclass[manuscript,screen,nonacm]{acmart}/' \
    talg_main.tex > arxiv/arxiv_main.tex

for f in ch/*.tex; do
  sed 's|\.\./\.\./results/|figs/|g' "$f" > "arxiv/$f"
done

grep -ho 'figs/[A-Za-z0-9_]*\.\(png\|pdf\|jpg\)' arxiv/ch/*.tex | sort -u | while read -r p; do
  cp "../../results/$(basename "$p")" "arxiv/$p"
done
echo "figures bundled: $(ls arxiv/figs | wc -l | tr -d ' ')"

# plain-text abstract for the metadata form
pandoc -f latex -t plain ch/abstract.tex -o arxiv/abstract.txt 2>/dev/null || true

# local verification compile (also produces the .bbl that arXiv needs)
cp refs_clean.bib hyperxmp.sty arxiv/
cd arxiv
pdflatex -interaction=nonstopmode arxiv_main.tex > build_arxiv.log 2>&1 || {
  echo "pass 1 FAILED:"; grep -A3 '^!' build_arxiv.log | head -20; exit 1; }
bibtex arxiv_main >> build_arxiv.log 2>&1
pdflatex -interaction=nonstopmode arxiv_main.tex >> build_arxiv.log 2>&1 || true
pdflatex -interaction=nonstopmode arxiv_main.tex >> build_arxiv.log 2>&1 || {
  echo "final pass FAILED:"; grep -A3 '^!' build_arxiv.log | head -20; exit 1; }
pages=$(pdfinfo arxiv_main.pdf 2>/dev/null | awk '/Pages/{print $2}')
undef=$(grep -c 'Citation .* undefined' arxiv_main.log || true)
echo "local verification: arxiv_main.pdf ${pages:-?} pages; undefined citations: ${undef:-0}"

# the tarball ships sources + bbl only — no stub, no .bib, no build artifacts
tar czf arxiv_submission.tar.gz arxiv_main.tex arxiv_main.bbl ch figs
echo "OK: $(pwd)/arxiv_submission.tar.gz ($(du -h arxiv_submission.tar.gz | cut -f1))"
