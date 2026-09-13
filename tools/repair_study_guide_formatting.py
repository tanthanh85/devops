from __future__ import annotations

import copy
import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor


DOCX = Path("/Users/thandoan/Documents/Presentations/DevOps/Network-DevOps-Professional-Study-Guide.docx")
BACKUP = Path("/tmp/Network-DevOps-Professional-Study-Guide-before-publishing-repair.docx")


TABLE_TITLES = {
    492: "Network Automation Component Responsibilities",
    641: "Intended Configured and Operational State Comparison",
    659: "Network Automation Test Types and Evidence",
    705: "Ad Hoc Automation and DevOps Delivery Comparison",
    718: "CALMS Dimensions in Software Delivery",
    733: "CALMS Assessment Questions",
    739: "Manual Ad Hoc and DevOps Delivery Models",
    759: "Testing Boundaries and Required Evidence",
    777: "Delivery Gates Decisions and Evidence",
    840: "DORA Measures for Network Delivery",
    851: "Intent Validation and Delivery Stages",
    895: "Terraform Ansible and Python Responsibility Boundaries",
    1002: "Network Test Environment Options",
    1082: "Containerization Benefits and Operational Tradeoffs",
    1210: "Automation Image Contents and Runtime Inputs",
    1315: "Packaging Failure Modes and Controls",
    1431: "Compose Application Failure Boundaries and Controls",
    1454: "Container Platform Selection Criteria",
    1460: "Protected Runner Compose and Kubernetes Comparison",
    1658: "GitLab Components and Network Automation Responsibilities",
    1698: "Test Environments Capabilities and Limitations",
    1727: "GitLab Runner Executor Tradeoffs",
    1753: "Pipeline Purposes Triggers and Protected Resources",
    1814: "Pipeline Gates and Their Evidence",
    1852: "Intended Configured and Operational State Evidence",
    1899: "Routing Service Predeployment Checks",
    1966: "Deployment Strategies and Network Automation Controls",
    2086: "Delivery Assets Threats and Controls",
    2144: "Security Test Types and Evidence Boundaries",
    2154: "Compromised Runner Response Actions and Evidence",
    2232: "Telemetry Monitoring and Observability Comparison",
    2293: "Metrics Collection Components and Responsibilities",
    2359: "Pipeline Audit Events and Required Context",
}


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tcMar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn("w:tblHeader")) is None:
        trPr.append(OxmlElement("w:tblHeader"))


def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    if trPr.find(qn("w:cantSplit")) is None:
        trPr.append(OxmlElement("w:cantSplit"))


def paragraph_shading(paragraph, fill):
    pPr = paragraph._p.get_or_add_pPr()
    shd = pPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        pPr.append(shd)
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")


def paragraph_border(paragraph, *, top=None, bottom=None, left=None, right=None):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    for side, color in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        if color:
            el = OxmlElement(f"w:{side}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "8" if side == "left" else "4")
            el.set(qn("w:space"), "5")
            el.set(qn("w:color"), color)
            pBdr.append(el)


def restart_list_numbering(doc: Document):
    numbering = doc.part.numbering_part.element
    num_ids = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
    next_id = max(num_ids or [0]) + 1
    list_num_style = doc.styles["List Number"]
    style_num_pr = list_num_style.element.pPr.numPr
    base_num_id = int(style_num_pr.numId.val)
    base_num = next(n for n in numbering.findall(qn("w:num")) if int(n.get(qn("w:numId"))) == base_num_id)
    abstract_id = base_num.find(qn("w:abstractNumId")).get(qn("w:val"))

    previous_was_number = False
    current_id = None
    for p in doc.paragraphs:
        is_number = p.style.name == "List Number"
        if is_number and not previous_was_number:
            current_id = next_id
            next_id += 1
            num = OxmlElement("w:num")
            num.set(qn("w:numId"), str(current_id))
            abstract = OxmlElement("w:abstractNumId")
            abstract.set(qn("w:val"), abstract_id)
            num.append(abstract)
            override = OxmlElement("w:lvlOverride")
            override.set(qn("w:ilvl"), "0")
            start = OxmlElement("w:startOverride")
            start.set(qn("w:val"), "1")
            override.append(start)
            num.append(override)
            numbering.append(num)
        if is_number:
            pPr = p._p.get_or_add_pPr()
            numPr = pPr.find(qn("w:numPr"))
            if numPr is None:
                numPr = OxmlElement("w:numPr")
                pPr.append(numPr)
            for child in list(numPr):
                numPr.remove(child)
            ilvl = OxmlElement("w:ilvl"); ilvl.set(qn("w:val"), "0")
            numId = OxmlElement("w:numId"); numId.set(qn("w:val"), str(current_id))
            numPr.extend([ilvl, numId])
        previous_was_number = is_number


def add_or_get_style(doc, name, base="Normal"):
    try:
        return doc.styles[name]
    except KeyError:
        style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles[base]
        return style


def clean_heading_text(text):
    text = re.sub(r"^\s*#{1,6}\s*", "", text)
    text = re.sub(r"^\s*\d+(?:\.\d+){1,}\.?\s+", "", text)
    return text.strip()


def main():
    shutil.copy2(DOCX, BACKUP)
    doc = Document(DOCX)

    # A4, single-sided, consistent margins.
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)
        section.left_margin = Mm(22)
        section.right_margin = Mm(22)
        section.gutter = Mm(0)
        sectPr = section._sectPr
        mirror = sectPr.find(qn("w:mirrorMargins"))
        if mirror is not None:
            sectPr.remove(mirror)

    # Typography and heading behavior.
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"; normal.font.size = Pt(10.5); normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.08
    for level, size in ((1, 22), (2, 17), (3, 13), (4, 11)):
        style = doc.styles[f"Heading {level}"]
        style.font.name = "Arial"; style.font.size = Pt(size); style.font.bold = True; style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(14 if level <= 2 else 10)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.keep_together = True
        pPr = style.element.get_or_add_pPr()
        numPr = pPr.find(qn("w:numPr"))
        if numPr is not None: pPr.remove(numPr)

    # Module titles become Heading 1; internal hierarchy shifts down one level.
    in_module = False
    for p in doc.paragraphs:
        if p.style.name == "Title" and p.text.strip() in {
            "Network Automation Review", "Introducing the DevOps Model",
            "Infrastructure as Code and On-Demand Environments", "Packaging and Operating Applications",
            "Continuous Integration Delivery and Deployment Validation", "Security and Observability",
        }:
            in_module = True
            p.style = doc.styles["Heading 1"]
        elif in_module:
            if p.style.name == "Heading 1": p.style = doc.styles["Heading 2"]
            elif p.style.name == "Heading 2": p.style = doc.styles["Heading 3"]
            elif p.style.name == "Heading 3": p.style = doc.styles["Heading 4"]

    for p in doc.paragraphs:
        if p.style.name.startswith("Heading"):
            cleaned = clean_heading_text(p.text)
            if cleaned != p.text:
                p.text = cleaned
            pPr = p._p.get_or_add_pPr()
            numPr = pPr.find(qn("w:numPr"))
            if numPr is not None: pPr.remove(numPr)

    # Lists: genuine numbered sequences remain numbered but restart at one.
    restart_list_numbering(doc)
    for name in ("List Bullet", "List Number"):
        s = doc.styles[name]
        s.font.name = "Arial"; s.font.size = Pt(10.5); s.font.color.rgb = RGBColor(0, 0, 0)
        s.paragraph_format.space_after = Pt(3)
        s.paragraph_format.keep_together = True

    # Consistent editable code presentation.
    code = doc.styles["Code Block"]
    code.font.name = "Consolas"; code.font.size = Pt(9); code.font.color.rgb = RGBColor(0, 0, 0)
    code.paragraph_format.left_indent = Mm(5)
    code.paragraph_format.right_indent = Mm(3)
    code.paragraph_format.space_before = Pt(5)
    code.paragraph_format.space_after = Pt(7)
    code.paragraph_format.keep_together = True
    for p in doc.paragraphs:
        if p.style.name == "Code Block":
            paragraph_shading(p, "F2F2F2")
            for r in p.runs:
                r.font.name = "Consolas"; r.font.size = Pt(9)

    # Turn raw callout markers into compact professional callouts.
    callout_labels = {"DESIGN INSIGHT", "KEY POINT", "VERIFICATION", "FAILURE SCENARIO", "OPERATIONAL CONSIDERATION"}
    for i, p in enumerate(doc.paragraphs):
        label = p.text.strip().strip("*").strip().upper()
        if label in callout_labels:
            p.text = label.title()
            for r in p.runs:
                r.bold = True; r.font.name = "Arial"; r.font.size = Pt(10); r.font.color.rgb = RGBColor(0, 76, 135)
            p.paragraph_format.space_before = Pt(8); p.paragraph_format.space_after = Pt(2)
            paragraph_shading(p, "EAF3F8")
            paragraph_border(p, top="9ECAE1", left="2B7EA1", right="9ECAE1")
            if i + 1 < len(doc.paragraphs):
                body = doc.paragraphs[i + 1]
                paragraph_shading(body, "F5FAFC")
                paragraph_border(body, bottom="9ECAE1", left="2B7EA1", right="9ECAE1")
                body.paragraph_format.left_indent = Mm(4)
                body.paragraph_format.right_indent = Mm(3)

    # Module-based figure and table numbering, plus descriptive table titles.
    figure_caption_style = add_or_get_style(doc, "Figure Caption", "Caption")
    table_caption_style = add_or_get_style(doc, "Table Caption", "Caption")
    module = "I"
    figure_no = table_no = 0
    module_by_title = {
        "Network Automation Review": "0", "Introducing the DevOps Model": "1",
        "Infrastructure as Code and On-Demand Environments": "2", "Packaging and Operating Applications": "3",
        "Continuous Integration Delivery and Deployment Validation": "4", "Security and Observability": "5",
    }
    for idx, p in enumerate(doc.paragraphs):
        if p.text.strip() in module_by_title:
            module = module_by_title[p.text.strip()]
            figure_no = table_no = 0
        if p.style.name == "Caption":
            text = p.text.strip()
            if text.startswith("Figure "):
                figure_no += 1
                desc = re.sub(r"^Figure\s+(?:[A-Z0-9]+-)?\d+\.\s*", "", text)
                p.text = f"Figure {module}-{figure_no}. {desc}"
                p.style = figure_caption_style
            elif text.startswith("Table "):
                table_no += 1
                desc = TABLE_TITLES.get(idx)
                if desc is None:
                    desc = re.sub(r"^Table\s+(?:[A-Z0-9]+-)?\d+\.\s*", "", text)
                p.text = f"Table {module}-{table_no}. {desc}"
                p.style = table_caption_style
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(9)
            p.paragraph_format.keep_together = True

    # Center image paragraphs and keep each visual with its following caption.
    for i, p in enumerate(doc.paragraphs):
        if p._p.xpath(".//w:drawing"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if i + 1 < len(doc.paragraphs) and doc.paragraphs[i + 1].style.name == "Caption":
                p.paragraph_format.keep_with_next = True

    # Table readability and stable pagination.
    for table in doc.tables:
        if table.rows:
            set_repeat_header(table.rows[0])
        for row in table.rows:
            prevent_row_split(row)
            for cell in row.cells:
                set_cell_margins(cell)
                for p in cell.paragraphs:
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.0

    # Request a full field refresh when opened in Word.
    settings = doc.settings.element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")

    # Lists of figures and tables are style-based so module-prefixed captions
    # remain stable without artificial heading numbering.
    for instr in doc.element.body.xpath(".//w:instrText"):
        value = instr.text or ""
        if 'TOC \\c "Figure"' in value:
            instr.text = 'TOC \\t "Figure Caption,1" \\h \\z'
        elif 'TOC \\c "Table"' in value:
            instr.text = 'TOC \\t "Table Caption,1" \\h \\z'

    doc.save(DOCX)
    print(DOCX)
    print(BACKUP)


if __name__ == "__main__":
    main()
