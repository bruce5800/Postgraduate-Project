#!/bin/bash
# 投稿稿的双栏批注版：左原文、右批注卡片。批注在 paper/*.md 里是 HTML 注释，
# latex/build_paper.sh 会剥掉，所以 talg_main.pdf 不受影响。
set -e
cd "$(dirname "$0")"
SECTIONS="${*:-00_abstract_intro 01_setup 02_unified_benchmark 03_order_error 04_test_and_fallback 05_external_validity 06_theory 07_serving_related_conclusion}"
echo "sections: $SECTIONS"
python3 rev2tex.py $SECTIONS > body.tex
xelatex -interaction=nonstopmode review_main.tex > build_review.log 2>&1 || {
  echo "FAILED — first error:"; grep -A4 '^!' build_review.log | head -30; exit 1; }
xelatex -interaction=nonstopmode review_main.tex >> build_review.log 2>&1 || true
mv -f review_main.pdf paper_review.pdf
pages=$(pdfinfo paper_review.pdf 2>/dev/null | awk '/Pages/{print $2}')
n=$(grep -c '^<!--REV' $(for s in $SECTIONS; do echo "../$s.md"; done) | awk -F: '{s+=$2} END {print s}')
marks=$(grep -o '\\revhlid' body.tex | wc -l | tr -d ' ')
echo "OK: paper_review.pdf — ${pages:-?} 页, ${n:-?} 条批注, ${marks} 处原文着色"
