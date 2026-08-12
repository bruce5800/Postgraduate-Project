#!/usr/bin/env python3
"""Build the two-column annotated review body: original text left, annotation cards right.

Reads the <!--REV --> blocks that live inline in thesis/en/*.md (and review/00_abstract.md),
converts each markdown block to LaTeX in one pandoc pass, pairs every block with the
annotations anchored to it, and underlines the quoted span inside the original text with a
matching inline id.

The annotations stay HTML comments, so every real build still strips them (check_clean.sh).

    python3 rev2tex.py 01_introduction 06_test_and_fallback  >  body.tex
"""
import re
import subprocess
import sys
import pathlib

HERE = pathlib.Path(__file__).parent
EN = HERE.parent

LEVEL_COLOR = {"必改": "revMust", "建议": "revShould", "可选": "revNice"}
FIELDS = ("id", "role", "level", "kind", "quote", "mark", "note", "fix")
MARKER = "ZZBLK%dZZ"
MARKER_RE = re.compile(r"ZZBLK(\d+)ZZ")

TEX_ESCAPE = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&",
              "#": r"\#", "^": r"\textasciicircum{}", "_": r"\_", "%": r"\%",
              "~": r"\textasciitilde{}"}

unmatched = []


def esc(t):
    return "".join(TEX_ESCAPE.get(c, c) for c in t)


# ---------------------------------------------------------------- markdown side

def split_chunks(text):
    """-> [(kind, text)] where kind in {ann, drop, head, fig, raw, body}.

    Fence-aware: a ``` block stays one chunk even though it contains blank lines
    (Table 4.1 is a {=latex} block, Appendix A has bash blocks).
    """
    out, buf, fence = [], [], False

    def flush():
        if not buf:
            return
        chunk = "\n".join(buf).strip("\n")
        buf.clear()
        if not chunk.strip():
            return
        s = chunk.lstrip()
        if s.startswith("<!--REV"):
            out.append(("ann", chunk))
        elif s.startswith("<!--"):
            out.append(("drop", chunk))
        elif s.startswith("```"):
            out.append(("raw", chunk))          # full width: may hold a float
        elif s.startswith("#"):
            out.append(("head", chunk))
        elif s.startswith("!["):
            out.append(("fig", chunk))
        else:
            out.append(("body", chunk))

    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            if not fence and buf:
                flush()                          # text before an opening fence
            buf.append(line)
            fence = not fence
            if not fence:
                flush()                          # closing fence ends the chunk
            continue
        if fence:
            buf.append(line)
        elif line.strip():
            buf.append(line)
        else:
            flush()
    flush()
    return out


def parse_ann(chunk):
    fields, key = {}, None
    for line in chunk.splitlines()[1:-1]:
        m = re.match(r"\s*(" + "|".join(FIELDS) + r")\s*:\s*(.*)$", line)
        if m:
            key, fields[m.group(1)] = m.group(1), m.group(2).strip()
        elif key and line.strip():
            fields[key] += " " + line.strip()
    return fields


def pandoc(md):
    return subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "latex", "--top-level-division=chapter",
         "--syntax-highlighting=none"],
        input=md, capture_output=True, text=True, check=True).stdout


# ---------------------------------------------------------------- highlighting

CMD = re.compile(r"\\[a-zA-Z]+\*?")


def plainify(tex):
    """Strip LaTeX markup -> (plain text, index map back into `tex`)."""
    plain, idx, i, n = [], [], 0, len(tex)
    while i < n:
        c = tex[i]
        if c == "\\":
            m = CMD.match(tex, i)
            if m:                                   # \emph, \ldots, ...
                i = m.end()
                if tex[i:i + 2] == "{}":
                    i += 2
                continue
            if tex[i:i + 2] in (r"\(", r"\["):      # inline / display math
                close = r"\)" if tex[i + 1] == "(" else r"\]"
                j = tex.find(close, i)
                i = n if j < 0 else j + 2
                continue
            plain.append(tex[i + 1])                # escaped literal: \% \_ \& ...
            idx.append(i + 1)
            i += 2
            continue
        if c in "{}":
            i += 1
            continue
        if c.isspace():
            if plain and plain[-1] != " ":
                plain.append(" ")
                idx.append(i)
            i += 1
            continue
        plain.append(c)
        idx.append(i)
        i += 1
    return "".join(plain), idx


def norm_quote(q):
    q = re.sub(r"\$[^$]*\$", " ", q)                 # drop math
    q = q.replace("*", "")
    return re.sub(r"\s+", " ", q).strip()


TRANS = str.maketrans({"—": "-", "–": "-", "\u201c": '"', "\u201d": '"',
                       "\u2018": "'", "\u2019": "'", "`": "'"})


def norm_plain(p):
    return p.translate(TRANS)          # 1:1 only — index map must stay valid


def build_pattern(q):
    """Regex tolerant of pandoc's re-wrapping, dashes and smart quotes."""
    out, i = [], 0
    while i < len(q):
        c = q[i]
        if q[i:i + 3] == "...":
            out.append(".{0,240}?")
            i += 3
        elif c.isspace():
            out.append(r"\s+")
            while i < len(q) and q[i].isspace():
                i += 1
        elif c == "-":
            out.append(r"[-\s]{1,4}")
            i += 1
        elif c in "'\"`":
            out.append(r"[\'\"`]{1,2}")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return "".join(out)


def find_span(plain, quote):
    """Locate `quote` (... = wildcard) in `plain`; fall back to a word run."""
    plain_n = norm_plain(plain)
    q = norm_quote(quote)
    if len(q) < 12:
        return None

    def search(text):
        m = re.search(build_pattern(text), plain_n, re.I)
        return (m.start(), m.end()) if m else None

    hit = search(q)
    if hit:
        return hit
    words = q.split(" ")
    for k in range(min(16, len(words)), 3, -1):
        hit = search(" ".join(words[:k]))
        if hit:
            return hit
    for k in range(min(16, len(words)), 3, -1):
        hit = search(" ".join(words[-k:]))
        if hit:
            return hit
    return None


def clean_runs(tex, start, end):
    """Maximal markup-free runs in [start,end) — safe as a soul \\hl argument."""
    runs, i, run_start = [], start, None

    def close(j):
        nonlocal run_start
        if run_start is not None:
            runs.append((run_start, j))
            run_start = None

    while i < end:
        c = tex[i]
        if c == "\\":
            close(i)
            if tex[i:i + 2] in ("\\(", "\\["):            # math: skip to the closer
                j = tex.find("\\)" if tex[i + 1] == "(" else "\\]", i)
                i = end if j < 0 else j + 2
            else:
                m = CMD.match(tex, i)
                i = m.end() if m else i + 2
            continue
        if c in "{}$":
            close(i)
            i += 1
            continue
        if run_start is None:
            run_start = i
        i += 1
    close(end)
    return [(a, b) for a, b in runs if len(tex[a:b].strip()) >= 18
            and len(tex[a:b].split()) >= 3]


def locate(tex, target, taken):
    """Where to mark `target` in `tex`, or None. `taken` = spans already claimed."""
    if not target or target.strip() in ("-", "none"):
        return None
    plain, idx = plainify(tex)
    hit = find_span(plain, target)
    if not hit:
        return None
    s, e = idx[hit[0]], idx[min(hit[1], len(idx)) - 1] + 1
    if any(not (e <= s2 or s >= e2) for s2, e2 in taken):
        return None
    runs = clean_runs(tex, s, e)
    if not runs:
        return None
    return max(runs, key=lambda r: r[1] - r[0])


def apply_marks(tex, marks):
    """marks = [(start, end, id, level)] -> tex with soul highlights, back to front."""
    for s, e, aid, level in sorted(marks, key=lambda m: -m[0]):
        color = LEVEL_COLOR.get(level, "revShould")
        tex = (tex[:s] + "\\revhl{%s}{%s}\\revhlid{%s}{%s}"
               % (color, tex[s:e].strip(), color, esc(aid)) + tex[e:])
    return tex


# ---------------------------------------------------------------- cards

def card(a, quote_shown):
    color = LEVEL_COLOR.get(a.get("level", ""), "revShould")
    head = " · ".join(x for x in (a.get("id", ""), a.get("role", ""),
                                  a.get("level", ""), a.get("kind", "")) if x)
    body = []
    if not quote_shown and a.get("quote"):
        body.append("\\textbf{原文}\\hspace{0.4em}\\textquotedblleft %s\\textquotedblright\\par"
                    % esc(a["quote"]))
    if a.get("note"):
        body.append("\\textbf{问题}\\hspace{0.4em}%s\\par" % esc(a["note"]))
    if a.get("fix"):
        body.append("\\textbf{建议}\\hspace{0.4em}%s" % esc(a["fix"]))
    return "\\revcard{%s}{%s}{%%\n%s}" % (color, esc(head), "\n".join(body))


# ---------------------------------------------------------------- figures

def brace_arg(tex, pos):
    """Content of the {...} group starting at `pos`."""
    depth, i = 0, pos
    while i < len(tex):
        if tex[i] == "{":
            depth += 1
        elif tex[i] == "}":
            depth -= 1
            if depth == 0:
                return tex[pos + 1:i], i + 1
        i += 1
    return "", len(tex)


def figure_to_inline(tex):
    """pandoc's float -> a non-float centred graphic (floats are illegal in minipages)."""
    m = re.search(r"\\includegraphics\[[^]]*\]\{([^}]*)\}", tex)
    if not m:
        return tex
    path = m.group(1)
    c = tex.find("\\caption{")
    caption = brace_arg(tex, c + len("\\caption"))[0] if c >= 0 else ""
    return "\\revfigure{%s}{%s}" % (path, caption)


# ---------------------------------------------------------------- assembly

def build(path, paired=True):
    chunks = split_chunks(path.read_text(encoding="utf-8"))
    kept = [(k, t) for k, t in chunks if k != "drop"]

    blocks = [(k, t) for k, t in kept if k != "ann"]          # renderable blocks
    md = "".join(f"{MARKER % i}\n\n{t}\n\n" for i, (_, t) in enumerate(blocks))
    tex_out = pandoc(md)
    parts = MARKER_RE.split(tex_out)
    rendered = {}
    for j in range(1, len(parts), 2):
        rendered[int(parts[j])] = parts[j + 1].strip()

    # annotations attach to the most recent renderable block
    anns_for = {}
    bi = -1
    for k, t in kept:
        if k == "ann":
            anns_for.setdefault(bi, []).append(parse_ann(t))
        else:
            bi += 1

    for i, (kind, _) in enumerate(blocks):          # de-float first: mark offsets
        if kind == "fig" and i in rendered:          # must refer to the final text
            rendered[i] = figure_to_inline(rendered[i])

    # blocks whose text must never be touched: verbatim, tables, raw LaTeX
    protected = {i for i, (k, _) in enumerate(blocks) if k == "raw"}
    protected |= {i for i, tx in rendered.items()
                  if any(e in tx for e in ("\\begin{longtable}", "\\begin{tabular}",
                                           "\\begin{verbatim}", "\\begin{Shaded}"))}

    # place each annotation's quote: its own block first, then nearby ones
    marks = {}
    for bi, anns in sorted(anns_for.items()):
        for a in anns:
            target = a.get("mark") or a.get("quote", "")
            for cand in (bi, bi - 1, bi + 1, bi + 2, bi - 2, bi + 3, bi - 3):
                if cand not in rendered or cand in protected:
                    continue
                spot = locate(rendered[cand], target, [(s, e) for s, e, _, _ in
                                                       marks.get(cand, [])])
                if spot:
                    marks.setdefault(cand, []).append(
                        (spot[0], spot[1], a["id"], a.get("level", "")))
                    a["_marked"] = True
                    break
            if not a.get("_marked") and target.strip() not in ("-", "none"):
                unmatched.append(a["id"])

    out = []
    for i, (kind, _) in enumerate(blocks):
        tex = rendered.get(i, "")
        anns = anns_for.get(i, [])
        if i in marks:
            tex = apply_marks(tex, marks[i])
        # longtable / float cannot live inside a minipage: give them the full width
        if kind in ("head", "raw") or "\\begin{longtable}" in tex or "\\begin{table}" in tex:
            if "\\begin{longtable}" in tex:      # the appendix path tables are wide
                tex = "{\\footnotesize\\setlength{\\tabcolsep}{3pt}\n%s\n}" % tex
            out.append(tex)
            if not anns:
                continue
            tex = ""
        if not paired:
            out.append(tex)
            continue
        cards = [card(a, a.get("_marked", False)) for a in anns]
        rows = [cards[k:k + 2] for k in range(0, len(cards), 2)] or [[]]
        for r, group in enumerate(rows):
            out.append("\\revpair{%s}{%s}" % (tex if r == 0 else "\\mbox{}", "\n".join(group)))
    return "\n\n".join(x for x in out if x.strip())
def main():
    names = sys.argv[1:] or ["00_abstract_intro", "01_setup", "02_unified_benchmark",
                             "03_order_error", "04_test_and_fallback", "05_external_validity",
                             "06_theory", "07_serving_related_conclusion"]
    parts = [build(HERE / "00_front.md", paired=False), "\\clearpage"]
    for n in names:
        parts.append(build(EN / f"{n}.md"))
    sys.stdout.write("\n\n".join(parts) + "\n")
    if unmatched:
        sys.stderr.write("quote not located in its paragraph (card keeps the 原文 line): "
                         + ", ".join(unmatched) + "\n")


main()
