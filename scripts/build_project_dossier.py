"""Build the current handoff DOCX and prompt from the canonical Markdown.

Run with the document workspace Python runtime (python-docx + lxml), not the
application venv. This script only writes its named documentation outputs.
The DOCX still needs a real Office renderer and page-image review afterwards.
"""

from __future__ import annotations

import json
from pathlib import Path
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/PROJECT_DOSSIER.md"
OUT = ROOT / "docs/current-project/援航项目实际实现与协作对接总文档.docx"
PROMPT = ROOT / "prompts/06_CURRENT_PROJECT_HANDOFF.md"


def xml(name, text=None):
    node = OxmlElement(name)
    if text is not None:
        node.text = text
    return node


def math_run(value):
    node = xml("m:r")
    node.append(xml("m:t", value))
    return node


def parse_math(source):
    """Small OMML authoring path for the dossier's explicit equation subset."""
    pos = 0
    commands = {
        "Delta": "Δ", "eta": "η", "rho": "ρ", "geq": "≥",
        "max": "max", "sum": "∑", "quad": "  ",
        "left": "", "right": "", ",": " ", " ": " ",
    }

    def group():
        nonlocal pos
        nodes = []
        while pos < len(source):
            char = source[pos]
            pos += 1
            if char == "}":
                break
            if char == "{":
                nodes.extend(group())
            elif char == "\\":
                match = re.match(r"[A-Za-z]+|.", source[pos:])
                if not match:
                    continue
                name = match.group()
                pos += len(name)
                if name not in commands:
                    raise ValueError(f"Unsupported equation command {name}")
                if commands[name]:
                    nodes.append(math_run(commands[name]))
            elif char in "_^":
                if not nodes:
                    raise ValueError("Missing equation base")
                base = nodes.pop()
                if source[pos] == "{":
                    pos += 1
                    content = group()
                else:
                    content = [math_run(source[pos])]
                    pos += 1
                sub = xml("m:sSub" if char == "_" else "m:sSup")
                e = xml("m:e")
                e.append(base)
                index = xml("m:sub" if char == "_" else "m:sup")
                for item in content:
                    index.append(item)
                sub.append(e)
                sub.append(index)
                nodes.append(sub)
            else:
                nodes.append(math_run(char))
        return nodes

    return group()


def inline(paragraph, text, table=False):
    # Word keeps code paths copyable; discretionary breaks only follow slashes.
    for token in re.split(r"(`[^`]+`|\*\*[^*]+\*\*|\[[^]]+\]\([^)]*\))", text):
        if not token:
            continue
        code = token.startswith("`") and token.endswith("`")
        bold = token.startswith("**") and token.endswith("**")
        if code:
            token = token[1:-1]
        elif bold:
            token = token[2:-2]
        else:
            match = re.fullmatch(r"\[([^]]+)\]\(([^)]*)\)", token)
            if match:
                token = match[1]
        run = paragraph.add_run(token)
        run.bold = bold
        if code:
            run.font.name = "Consolas"
            run.font.size = Pt(9.5 if table else 10)
            run.font.color.rgb = RGBColor.from_string("234C54")


def set_font(style, size, bold=False):
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "微软雅黑")


def make_doc():
    source = SOURCE.read_text(encoding="utf-8")
    match = re.search(r"## 21 .*?```text\n(.*?)\n```", source, re.S)
    if not match or len(match[1]) < 1000:
        raise ValueError("The full teammate prompt was not found")
    PROMPT.write_text(
        "# 援航当前版本无记忆接手提示词\n\n"
        "配套主文档：[实际实现与协作对接总文档](../docs/PROJECT_DOSSIER.md)。"
        "在队友自己的仓库根目录使用，最后填写本次具体任务。\n\n"
        "```text\n" + match[1] + "\n```\n", encoding="utf-8",
    )
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin, section.bottom_margin = Inches(.72), Inches(.7)
    section.left_margin = section.right_margin = Inches(.78)
    section.footer_distance = Inches(.3)
    set_font(doc.styles["Normal"], 11)
    normal = doc.styles["Normal"].paragraph_format
    normal.line_spacing = 1.17
    normal.space_after = Pt(7)
    normal.widow_control = True
    # OOXML wordWrap=off enables character-level line breaks in long Latin
    # identifiers, without inserting invisible characters into copyable paths.
    # Microsoft Learn: Wordprocessing.WordWrap, ISO/IEC 29500 remarks.
    wrapping = xml("w:wordWrap")
    wrapping.set(qn("w:val"), "off")
    doc.styles["Normal"].element.get_or_add_pPr().append(wrapping)
    for name, size in [("Title", 24), ("Heading 1", 16), ("Heading 2", 12.5)]:
        set_font(doc.styles[name], size, True)
        f = doc.styles[name].paragraph_format
        f.space_before = Pt(14 if name != "Title" else 0)
        f.space_after = Pt(8)
        f.keep_with_next = True
    set_font(doc.styles["Caption"], 10)
    set_font(doc.styles["List Bullet"], 11)
    set_font(doc.styles["List Number"], 11)
    # No decorative title rules or shaded callouts.
    for name in ["Title", "Subtitle"]:
        ppr = doc.styles[name].element.find(qn("w:pPr"))
        if ppr is not None:
            for border in list(ppr.findall(qn("w:pBdr"))):
                ppr.remove(border)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    page = footer.add_run()
    field = xml("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    page._r.addnext(field)
    page.font.size = Pt(9)
    doc.core_properties.title = "援航项目实际实现与协作对接总文档"
    doc.core_properties.subject = "V4实际算法工程功能与两人协作交接"
    doc.core_properties.author = "援航项目组"
    doc.core_properties.keywords = "无人机 调度 通信 地形 业务仿真 项目对接"
    doc.core_properties.comments = "主源 docs/PROJECT_DOSSIER.md V4核心基线3ff456e及后续修复"

    lines, i, equations, tables = source.splitlines(), 0, 0, 0
    in_contents = False
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line.startswith("# "):
            doc.add_paragraph(line[2:], "Title")
        elif line.startswith("## "):
            heading = line[3:]
            in_contents = heading == "阅读目录"
            if heading.startswith("1 项目"):
                doc.add_page_break()
            doc.add_heading(heading, level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=2)
        elif line.startswith("$$") and line.endswith("$$"):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(8)
            root = xml("m:oMathPara")
            equation = xml("m:oMath")
            for node in parse_math(line[2:-2]):
                equation.append(node)
            root.append(equation)
            p._p.append(root)
            following = next((row.strip() for row in lines[i:] if row.strip()), "")
            p.paragraph_format.keep_with_next = following.startswith("$$")
            equations += 1
        elif line.startswith("```"):
            language = line[3:]
            body = []
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            for row_index, row in enumerate(body):
                if not row:
                    doc.add_paragraph().paragraph_format.space_after = Pt(0)
                    continue
                p = doc.add_paragraph()
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                if len(body) < 20:
                    p.paragraph_format.keep_with_next = row_index < len(body) - 1
                run = p.add_run(row)
                run.font.name = "Consolas" if language != "text" else "Arial"
                run.font.size = Pt(9.5 if language != "text" else 10.5)
                run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "微软雅黑")
        elif line.startswith("|"):
            rows = [line]
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            data = [[v.strip() for v in row.strip("|").split("|")] for row in rows]
            data = [row for row in data if not all(re.fullmatch(r":?-+:?", cell) for cell in row)]
            count = len(data[0])
            table = doc.add_table(rows=1, cols=count)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.style = "Table Grid"
            # Numeric evidence has seven narrow columns; other prose tables
            # allocate most width to the explanation, never shrink body to fit.
            widths = {
                3: [1.2, 2.8, 2.94],
                4: [1.15, 1.9, 1.95, 1.94],
                7: [1.2, .54, .78, 1.1, 1.1, 1.12, 1.1],
            }.get(count, [6.94 / count] * count)
            if count == 2 and data[0][0] in {"用途", "工作"}:
                widths = [1.2, 5.74]
            table.autofit = False
            for col, width in zip(table.columns, widths):
                col.width = Inches(width)
            for row_index, values in enumerate(data):
                cells = table.rows[0].cells if row_index == 0 else table.add_row().cells
                for col_index, (cell, value) in enumerate(zip(cells, values)):
                    cell.width = Inches(widths[col_index])
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(3)
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.line_spacing = 1.08
                    if row_index == 0:
                        p.paragraph_format.keep_with_next = True
                    inline(p, value, table=True)
                    for run in p.runs:
                        run.font.size = Pt(10 if count < 7 else 9.5)
                        if row_index == 0:
                            run.bold = True
                    if row_index == 0:
                        shade = xml("w:shd")
                        shade.set(qn("w:fill"), "EAF0F0")
                        cell._tc.get_or_add_tcPr().append(shade)
                if row_index == 0:
                    repeat = xml("w:tblHeader")
                    table.rows[0]._tr.get_or_add_trPr().append(repeat)
                no_split = xml("w:cantSplit")
                table.rows[-1]._tr.get_or_add_trPr().append(no_split)
            doc.add_paragraph().paragraph_format.space_after = Pt(1)
            tables += 1
        elif re.match(r"\d+\. ", line):
            if in_contents:
                entries = [line]
                while i < len(lines):
                    candidate = lines[i].strip()
                    if not candidate:
                        i += 1
                        continue
                    if not re.match(r"\d+\. ", candidate):
                        break
                    entries.append(candidate)
                    i += 1
                half = (len(entries) + 1) // 2
                toc = doc.add_table(rows=half, cols=2)
                toc.autofit = False
                for col in toc.columns:
                    col.width = Inches(3.47)
                for index, entry in enumerate(entries):
                    cell = toc.rows[index % half].cells[index // half]
                    cell.width = Inches(3.47)
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(3)
                    p.paragraph_format.line_spacing = 1.05
                    inline(p, entry)
                in_contents = False
                continue
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(.16)
            p.paragraph_format.first_line_indent = Inches(-.16)
            inline(p, line)
        elif line.startswith("- "):
            inline(doc.add_paragraph(style="List Bullet"), line[2:])
        else:
            p = doc.add_paragraph()
            inline(p, line)
            following = next((row.strip() for row in lines[i:] if row.strip()), "")
            if following.startswith("$$"):
                p.paragraph_format.keep_with_next = True
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(json.dumps({
        "docx": str(OUT), "source_chars": len(source), "equations": equations,
        "tables": tables, "paragraphs": len(doc.paragraphs),
        "prompt_chars": len(match[1]),
    }, ensure_ascii=False))


if __name__ == "__main__":
    make_doc()
