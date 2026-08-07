#!/usr/bin/env python3
"""Turn <!--REV ... --> annotation blocks in the thesis markdown into visible LaTeX boxes.

The annotations live inside HTML comments, so every *normal* build
(latex/build.sh, latex_school/build_school.sh, latex/build_zh.sh) strips them and
produces a byte-identical thesis.  Only build_review.sh runs this script, which
converts them instead of deleting them.

Block format (the opening <!--REV and the closing --> must each be on their own line,
otherwise the other builds' sed range would swallow surrounding text):

    <!--REV
    id: R1-01
    role: R1 二审考官
    level: 必改
    kind: 术语未解释
    quote: governed by a Kendall-tau order error
    note: what is wrong
    fix: what to do instead
    -->

Fields other than `id` are optional; `note`/`fix`/`quote` may span several lines
(continuation lines are simply lines that carry no "key:" prefix).
Annotation text must be plain text: no math, no LaTeX.  Specials are escaped here.
"""
import re
import sys

LEVEL_COLOR = {"必改": "revMust", "建议": "revShould", "可选": "revNice"}
FIELDS = ("id", "role", "level", "kind", "quote", "note", "fix")

TEX_ESCAPE = {
    "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&",
    "#": r"\#", "^": r"\textasciicircum{}", "_": r"\_", "%": r"\%",
    "~": r"\textasciitilde{}",
}


def esc(text):
    return "".join(TEX_ESCAPE.get(c, c) for c in text)


def parse_block(body):
    """key: value lines (with continuations) -> dict."""
    fields, key = {}, None
    for line in body.splitlines():
        m = re.match(r"\s*(" + "|".join(FIELDS) + r")\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            fields[key] = val
        elif key and line.strip():
            fields[key] += " " + line.strip()
    return fields


def render(fields):
    level = fields.get("level", "建议")
    color = LEVEL_COLOR.get(level, "revShould")
    header = " · ".join(
        x for x in (fields.get("id", ""), fields.get("role", ""), level, fields.get("kind", "")) if x
    )
    out = ["\\begin{revbox}{%s}{%s}" % (color, esc(header))]
    if fields.get("quote"):
        out.append("\\textbf{原文}\\hspace{0.45em}\\textquotedblleft %s\\textquotedblright\\par" % esc(fields["quote"]))
    if fields.get("note"):
        out.append("\\textbf{问题}\\hspace{0.45em}%s\\par" % esc(fields["note"]))
    if fields.get("fix"):
        out.append("\\textbf{建议}\\hspace{0.45em}%s" % esc(fields["fix"]))
    out.append("\\end{revbox}")
    return "\n\n" + "\n".join(out) + "\n\n"


def convert(text):
    def sub(m):
        return render(parse_block(m.group(1)))

    # REV blocks -> boxes; every other HTML comment block -> dropped.
    text = re.sub(r"<!--REV\n(.*?)\n-->", sub, text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    # same unicode fixups the other builds apply
    for a, b in (("≈", r"$\approx$"), ("✓", r"$\checkmark$"), ("→", r"\ensuremath{\rightarrow}")):
        text = text.replace(a, b)
    return text


if __name__ == "__main__":
    sys.stdout.write(convert(open(sys.argv[1], encoding="utf-8").read()))
