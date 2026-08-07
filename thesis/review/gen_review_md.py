#!/usr/bin/env python3
"""Regenerate the per-chapter review checklists and SUMMARY.md from the REV blocks.

The annotations in thesis/en/*.md (and review/00_abstract.md) are the single source of
truth; these markdown files are a generated index.  Re-run after editing annotations:

    python3 gen_review_md.py
"""
import pathlib
import re

HERE = pathlib.Path(__file__).parent
EN = HERE.parent / "en"

SOURCES = [
    ("摘要", HERE / "00_abstract.md", "00_abstract.review.md",
     "源文件是 `thesis/latex/meta.yaml` 的 `abstract:` 块（中文版在 `meta_zh.yaml`）；"
     "`review/00_abstract.md` 只是批注用的副本，改定稿请改 meta.yaml。"),
    ("第 1 章 Introduction", EN / "01_introduction.md", "01_introduction.review.md", ""),
    ("第 6 章 Test-and-Fallback in Depth", EN / "06_test_and_fallback.md",
     "06_test_and_fallback.review.md", ""),
    ("第 10 章 Conclusion and Future Work", EN / "11_conclusion.md",
     "11_conclusion.review.md", "文件名是 `11_conclusion.md`，但在论文里是第 10 章。"),
]

LEVEL_MARK = {"必改": "🔴", "建议": "🟡", "可选": "⚪"}
LEVEL_ORDER = {"必改": 0, "建议": 1, "可选": 2}
BLOCK = re.compile(r"<!--REV\n(.*?)\n-->", re.S)
FIELDS = ("id", "role", "level", "kind", "quote", "note", "fix")


def parse(path):
    text = path.read_text(encoding="utf-8")
    line_of = {m.start(): text[: m.start()].count("\n") + 1 for m in BLOCK.finditer(text)}
    out = []
    for m in BLOCK.finditer(text):
        fields, key = {"_line": line_of[m.start()]}, None
        for line in m.group(1).splitlines():
            k = re.match(r"\s*(" + "|".join(FIELDS) + r")\s*:\s*(.*)$", line)
            if k:
                key, fields[k.group(1)] = k.group(1), k.group(2).strip()
            elif key and line.strip():
                fields[key] += " " + line.strip()
        out.append(fields)
    return out


def entry_md(a, relpath):
    mark = LEVEL_MARK.get(a.get("level", ""), "")
    head = f"### {a['id']} · {mark} {a.get('level','')} · {a.get('role','')} · {a.get('kind','')}"
    body = [head, "", f"`{relpath}:{a['_line']}`", ""]
    if a.get("quote"):
        body += [f"> {a['quote']}", ""]
    if a.get("note"):
        body += [f"**问题** {a['note']}", ""]
    if a.get("fix"):
        body += [f"**建议** {a['fix']}", ""]
    return "\n".join(body)


def main():
    all_ann = []
    for title, src, outname, note in SOURCES:
        anns = parse(src)
        rel = src.relative_to(HERE.parent).as_posix()
        counts = {lv: sum(1 for a in anns if a.get("level") == lv) for lv in LEVEL_MARK}
        head = [f"# {title} — 审读批注", "",
                f"共 {len(anns)} 条：🔴 必改 {counts['必改']} · 🟡 建议 {counts['建议']} · ⚪ 可选 {counts['可选']}。", "",
                f"批注原件在 `{rel}` 中，以 `<!--REV -->` 注释形式内联；正式构建会剥掉。"]
        if note:
            head += ["", note]
        head += ["", "---", ""]
        (HERE / outname).write_text(
            "\n".join(head) + "\n\n".join(entry_md(a, rel) for a in anns) + "\n", encoding="utf-8")
        for a in anns:
            a["_file"], a["_title"], a["_out"] = rel, title, outname
        all_ann += anns
        print(f"wrote {outname} ({len(anns)} entries)")

    # ---- SUMMARY.md ----
    roles = sorted({a.get("role", "") for a in all_ann})
    lines = ["# 审读总表", "",
             f"四个单元（摘要 / Ch1 / Ch6 / Ch10）共 **{len(all_ann)} 条**批注，六个视角。", "",
             "按视角与严重度：", "",
             "| 视角 | 🔴 必改 | 🟡 建议 | ⚪ 可选 | 合计 |", "|---|---|---|---|---|"]
    for r in roles:
        sub = [a for a in all_ann if a.get("role") == r]
        c = [sum(1 for a in sub if a.get("level") == lv) for lv in ("必改", "建议", "可选")]
        lines.append(f"| {r} | {c[0]} | {c[1]} | {c[2]} | {len(sub)} |")
    tot = [sum(1 for a in all_ann if a.get("level") == lv) for lv in ("必改", "建议", "可选")]
    lines += [f"| **合计** | **{tot[0]}** | **{tot[1]}** | **{tot[2]}** | **{len(all_ann)}** |", ""]

    lines += ["按单元：", "", "| 单元 | 🔴 | 🟡 | ⚪ | 清单 |", "|---|---|---|---|---|"]
    for title, src, outname, _ in SOURCES:
        sub = [a for a in all_ann if a["_out"] == outname]
        c = [sum(1 for a in sub if a.get("level") == lv) for lv in ("必改", "建议", "可选")]
        lines.append(f"| {title} | {c[0]} | {c[1]} | {c[2]} | [{outname}]({outname}) |")
    lines += ["", "---", ""]

    for lv in ("必改", "建议", "可选"):
        sub = [a for a in all_ann if a.get("level") == lv]
        lines += [f"## {LEVEL_MARK[lv]} {lv}（{len(sub)} 条）", ""]
        for a in sorted(sub, key=lambda x: (x["_out"], x["_line"])):
            lines.append(f"- **{a['id']}** {a.get('kind','')} · {a.get('role','')} — "
                         f"{a.get('note','')[:60]}… （`{a['_file']}:{a['_line']}`）")
        lines.append("")
    (HERE / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote SUMMARY.md ({len(all_ann)} entries, {tot[0]} 必改)")


main()
