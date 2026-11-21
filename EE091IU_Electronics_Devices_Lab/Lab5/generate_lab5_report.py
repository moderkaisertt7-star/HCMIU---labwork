"""
EE091IU Electronics Devices Lab - Lab 5: BJT Biasing in Switching Applications (NPN Transistor)
Generates:
  1. Lab5_BJT_Biasing_Switching_Report.docx (built directly on SEE_LabReportTemplate_ABET.docx)
  2. Lab5_BJT_Biasing_Switching_Report.md   (complete companion Markdown report)
and runs an automated verification suite on both output files.
"""

from pathlib import Path
import re
import subprocess
import zipfile
import pymupdf
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
TEMPLATE_PATH = Path(
    r"C:\Users\LENOVO\OneDrive\Desktop\UNIVERSITY\IU Junior\ED lab\templates\SEE_LabReportTemplate_ABET.docx"
)
OUT_DIR = Path(
    r"C:\Users\LENOVO\OneDrive\Desktop\Javis test\homework\EE091IU_Electronics_Devices_Lab\Lab5"
)
FIG_DIR = OUT_DIR / "figures"
DOCX_OUT = OUT_DIR / "Lab5_BJT_Biasing_Switching_Report.docx"
MD_OUT = OUT_DIR / "Lab5_BJT_Biasing_Switching_Report.md"
AUDIT_DUMP_OUT = OUT_DIR / "_docx_audit_dump.txt"
TEMP_PDF_OUT = OUT_DIR / "_temp_verify_lab5.pdf"

# Single-source verbatim captions (shared identically by LOF/LOT and body)
FIG_CAPTIONS = {
    1: "Bipolar junction transistor circuit symbols and TO-92 physical pinouts: (a) 2N3904 NPN and (b) 2N3906 PNP.",
    2: "NPN BJT switch in saturation: logic HIGH at the base pulls collector output V_{C} LOW.",
    3: "NPN BJT switch in cutoff: logic LOW at the base leaves collector output V_{C} HIGH.",
    4: "Experiment 1 circuit schematic for static biasing and switching of Q1 (2N3904).",
    5: "Experiment 3 circuit schematic for driving a collector-side LED across four R_{B} values.",
    6: "Experiment 2 theoretical waveforms V_{in}(t), V_{B}(t), and V_{C}(t) for a 0-5 V, 1 kHz square wave (D = 50% assumed).",
    7: "Experiment 3 analytical sweep of collector current I_{C}, base current I_{B}, overdrive factor (ODF), and forced gain β_{forced} versus base resistance R_{B}.",
}

TBL_CAPTIONS = {
    1: "NPN BJT operating regions, junction bias states, and typical applications.",
    2: "Experiment 1 static biasing and switching results (V_{CC} = 5 V, R_{C} = 470 Ω, R_{B} = 10 kΩ).",
    3: "Experiment 2 theoretical waveform levels and 2N3904 switching timing summary (1 kHz, D = 50% assumed).",
    4: "Experiment 3 LED driver results across four base resistors (V_{CC} = 5 V, R_{C} = 470 Ω, V_{LED} = 2.0 V assumed, V_{in} = 5 V).",
}

# Verified real page numbers (checked automatically against Word COM rendered PDF)
DEFAULT_PAGE_MAP = {
    "Grading Guideline for Lab Report": "2",
    "Team Contribution": "3",
    "List of Figures": "5",
    "List of Tables": "5",
    "Nomenclature": "6",
    "1. Objectives": "7",
    "2. Theoretical Background": "7",
    "2.1 NPN BJT Operating Regions and Switching Action": "7",
    "2.2 Governing Equations (Sedra & Smith, 6th Edition)": "9",
    "2.3 Step-by-Step Theoretical Calculations": "10",
    "3. Experimental Procedure": "13",
    "3.1 Material and Equipment": "13",
    "3.2 Experiment 1: Static Biasing and Switching": "13",
    "3.3 Experiment 2: Switching Response to Square Wave": "14",
    "3.4 Experiment 3: Driving an LED": "14",
    "4. Experimental Results": "15",
    "4.1 Experiment 1: Static Biasing and Switching": "15",
    "4.2 Experiment 2: Switching Response to Square Wave": "15",
    "4.3 Experiment 3: Driving an LED": "17",
    "5. Discussion of Results": "19",
    "5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)": "19",
    "5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)": "19",
    "5.3 Non-Ideal Deviations and Lab Verification Checklist": "20",
    "5.4 Summary": "21",
    "References": "21",
    "Figure 1": "7",
    "Figure 2": "8",
    "Figure 3": "9",
    "Figure 4": "13",
    "Figure 5": "14",
    "Figure 6": "16",
    "Figure 7": "18",
    "Table 1": "8",
    "Table 2": "15",
    "Table 3": "15",
    "Table 4": "17",
}

# Palette & Typography
NAVY = RGBColor(0x1B, 0x36, 0x5D)
NAVY_HEX = "1B365D"
DARK_TEXT = RGBColor(0x1A, 0x1A, 0x1A)
MUTED_TEXT = RGBColor(0x4A, 0x55, 0x68)
CALC_SHADE = "EEF2F7"
SUBHEADER_SHADE = "DCE6F1"
EQ_SHADE = "F7F9FC"
BORDER_HEX = "B8C4D4"
FONT_NAME = "Times New Roman"


# ---------------------------------------------------------------------------
# Low-level XML & Styling Helpers
# ---------------------------------------------------------------------------
def set_run_font(run, size_pt=12, bold=False, italic=False, color=DARK_TEXT, font_name=FONT_NAME):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), font_name)
    rfonts.set(qn("w:hAnsi"), font_name)
    rfonts.set(qn("w:cs"), font_name)
    rfonts.set(qn("w:eastAsia"), font_name)


def set_cell_shading(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:shd")):
        tc_pr.remove(old)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:tcMar")):
        tc_pr.remove(old)
    tc_mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def set_table_borders(table, color=BORDER_HEX, sz="4", val="single"):
    tbl_pr = table._tbl.tblPr
    for old in tbl_pr.findall(qn("w:tblBorders")):
        tbl_pr.remove(old)
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tbl_pr.append(borders)


def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:tcBorders")):
        tc_pr.remove(old)
    tc_b = OxmlElement("w:tcBorders")
    for side, spec in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        if spec is None:
            continue
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), spec.get("val", "single"))
        if spec.get("val", "single") != "none":
            el.set(qn("w:sz"), str(spec.get("sz", "4")))
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), spec.get("color", BORDER_HEX))
        tc_b.append(el)
    tc_pr.append(tc_b)


def set_row_cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:cantSplit")) is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def set_row_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:tblHeader")) is None:
        tr_pr.append(OxmlElement("w:tblHeader"))


def set_row_height(row, height_pt, rule="atLeast"):
    tr_pr = row._tr.get_or_add_trPr()
    for old in tr_pr.findall(qn("w:trHeight")):
        tr_pr.remove(old)
    el = OxmlElement("w:trHeight")
    el.set(qn("w:val"), str(int(height_pt * 20)))
    el.set(qn("w:hRule"), rule)
    tr_pr.append(el)


def set_col_widths(table, widths_in):
    table.autofit = False
    for row in table.rows:
        for cell, w in zip(row.cells, widths_in):
            cell.width = Inches(w)


# ---------------------------------------------------------------------------
# Rich Inline Text Parser for Word (supports _{sub}, ^{sup}, **bold**, *italic*)
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(
    r"(\*\*[^*]+\*\*|\*[^*]+\*|_\{[^}]+\}|\^\{[^}]+\})"
)


def add_rich_runs(p, text, size_pt=12, bold=False, italic=False, color=DARK_TEXT):
    """Parse lightweight inline tokens into formatted Word runs with true sub/superscripts."""
    if not text:
        return
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            r = p.add_run(text[pos:m.start()])
            set_run_font(r, size_pt=size_pt, bold=bold, italic=italic, color=color)
        tok = m.group(0)
        if tok.startswith("**") and tok.endswith("**"):
            add_rich_runs(p, tok[2:-2], size_pt=size_pt, bold=True, italic=italic, color=color)
        elif tok.startswith("*") and tok.endswith("*"):
            add_rich_runs(p, tok[1:-1], size_pt=size_pt, bold=bold, italic=True, color=color)
        elif tok.startswith("_{") and tok.endswith("}"):
            r = p.add_run(tok[2:-1])
            set_run_font(r, size_pt=size_pt, bold=bold, italic=italic, color=color)
            r.font.subscript = True
        elif tok.startswith("^{") and tok.endswith("}"):
            r = p.add_run(tok[2:-1])
            set_run_font(r, size_pt=size_pt, bold=bold, italic=italic, color=color)
            r.font.superscript = True
        pos = m.end()
    if pos < len(text):
        r = p.add_run(text[pos:])
        set_run_font(r, size_pt=size_pt, bold=bold, italic=italic, color=color)


# ---------------------------------------------------------------------------
# High-Level Document Building Helpers
# ---------------------------------------------------------------------------
def add_heading_1(doc, text, page_break_before=False):
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = page_break_before
    p.paragraph_format.space_before = Pt(14 if not page_break_before else 0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Bottom accent border under major section heading
    p_pr = p._p.get_or_add_pPr()
    p_bdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="3" w:color="{NAVY_HEX}"/>'
        f'</w:pBdr>'
    )
    p_pr.append(p_bdr)
    add_rich_runs(p, text, size_pt=14, bold=True, color=NAVY)
    return p


def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_rich_runs(p, text, size_pt=12, bold=True, color=NAVY)
    return p


def add_heading_3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(7)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_rich_runs(p, text, size_pt=11.5, bold=True, italic=False, color=DARK_TEXT)
    return p


def add_body_p(doc, text, space_after=5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size_pt=12, italic=False, color=DARK_TEXT):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    add_rich_runs(p, text, size_pt=size_pt, italic=italic, color=color)
    return p


def add_bullet_p(doc, text, space_after=3, level=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.32 + 0.22 * level)
    p.paragraph_format.first_line_indent = Inches(-0.18)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    bullet_char = "•  " if level == 0 else "◦  "
    r = p.add_run(bullet_char)
    set_run_font(r, size_pt=12, bold=(level == 0), color=NAVY if level == 0 else DARK_TEXT)
    add_rich_runs(p, text, size_pt=12, color=DARK_TEXT)
    return p


def add_numbered_p(doc, num_str, text, space_after=3):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Inches(0.34)
    p.paragraph_format.first_line_indent = Inches(-0.24)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(f"{num_str} ")
    set_run_font(r, size_pt=12, bold=True, color=NAVY)
    add_rich_runs(p, text, size_pt=12, color=DARK_TEXT)
    return p


def add_equation_block(doc, eq_text, eq_num):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_col_widths(tbl, [6.15, 0.85])
    row = tbl.rows[0]
    set_row_cant_split(row)

    c0, c1 = row.cells[0], row.cells[1]
    for c in (c0, c1):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(c, EQ_SHADE)
        set_cell_margins(c, top=70, bottom=70, left=120, right=100)

    set_cell_borders(
        c0,
        top={"val": "single", "sz": "4", "color": "DCE4EE"},
        bottom={"val": "single", "sz": "4", "color": "DCE4EE"},
        left={"val": "single", "sz": "18", "color": NAVY_HEX},
        right={"val": "none"},
    )
    set_cell_borders(
        c1,
        top={"val": "single", "sz": "4", "color": "DCE4EE"},
        bottom={"val": "single", "sz": "4", "color": "DCE4EE"},
        left={"val": "none"},
        right={"val": "single", "sz": "4", "color": "DCE4EE"},
    )

    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    add_rich_runs(p0, eq_text, size_pt=11.5, color=DARK_TEXT)

    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(0)
    add_rich_runs(p1, f"({eq_num})", size_pt=11, bold=True, color=NAVY)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)


def add_figure(doc, img_path, width_in, caption_text):
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(str(img_path), width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(8)
    add_rich_runs(p_cap, caption_text, size_pt=10.5, italic=True, color=MUTED_TEXT)


def add_table_caption(doc, caption_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    add_rich_runs(p, caption_text, size_pt=10.5, bold=True, color=NAVY)
    return p


def populate_cell(cell, text, size_pt=10.5, bold=False, italic=False, color=DARK_TEXT,
                  align=WD_ALIGN_PARAGRAPH.CENTER, shade=None):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_margins(cell, top=65, bottom=65, left=85, right=85)
    if shade:
        set_cell_shading(cell, shade)
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.08
    if text:
        add_rich_runs(p, text, size_pt=size_pt, bold=bold, italic=italic, color=color)


def add_index_table(doc, rows_data, col_widths=(1.1, 4.9, 1.0)):
    tbl = doc.add_table(rows=len(rows_data), cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_col_widths(tbl, col_widths)
    for ri, (c_left, c_mid, c_right) in enumerate(rows_data):
        row = tbl.rows[ri]
        set_row_cant_split(row)
        is_hdr = (ri == 0)
        for ci, (val, align) in enumerate(
            ((c_left, WD_ALIGN_PARAGRAPH.LEFT), (c_mid, WD_ALIGN_PARAGRAPH.LEFT), (c_right, WD_ALIGN_PARAGRAPH.RIGHT))
        ):
            cell = row.cells[ci]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=45, bottom=45, left=60, right=60)
            if is_hdr:
                set_cell_shading(cell, SUBHEADER_SHADE)
                set_cell_borders(
                    cell,
                    top={"val": "single", "sz": "6", "color": NAVY_HEX},
                    bottom={"val": "single", "sz": "6", "color": NAVY_HEX},
                    left={"val": "none"},
                    right={"val": "none"},
                )
            else:
                set_cell_borders(
                    cell,
                    top={"val": "none"},
                    bottom={"val": "dotted", "sz": "4", "color": "CBD5E0"},
                    left={"val": "none"},
                    right={"val": "none"},
                )
            p = cell.paragraphs[0]
            p.alignment = align
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            add_rich_runs(
                p,
                val,
                size_pt=10.5,
                bold=is_hdr or (ci == 0 and not val.startswith("  ")),
                color=NAVY if is_hdr else DARK_TEXT,
            )


# ---------------------------------------------------------------------------
# Template Front-Matter Preparation
# ---------------------------------------------------------------------------
def prepare_template_front_matter(doc):
    # 1. Update footer text ([Course number] -> EE091IU), fix tab stops (Left / Center / Right across 7.0 in), and standardize font
    for sec in doc.sections:
        for ftr in (sec.footer, sec.first_page_footer, sec.even_page_footer):
            if ftr is None:
                continue
            for pi, p in enumerate(ftr.paragraphs):
                if pi == 0 and any("[Course number]" in r.text for r in p.runs):
                    # Fix tab stops to exact center (3.5 in = 5040 dxa) and right (7.0 in = 10080 dxa)
                    p_pr = p._p.get_or_add_pPr()
                    for old_tabs in p_pr.findall(qn("w:tabs")):
                        p_pr.remove(old_tabs)
                    p_pr.append(
                        parse_xml(
                            f'<w:tabs {nsdecls("w")}>'
                            f'  <w:tab w:val="center" w:pos="5040"/>'
                            f'  <w:tab w:val="right" w:pos="10080"/>'
                            f'</w:tabs>'
                        )
                    )
                    # Remove one redundant tab run before the PAGE field so PAGE lands at center
                    removed_tab = False
                    for r in list(p.runs):
                        if not removed_tab and r.text == "\t" and len(r._r.findall(qn("w:tab"))) == 1:
                            p._p.remove(r._r)
                            removed_tab = True
                for r in p.runs:
                    if "[Course number]" in r.text:
                        r.text = r.text.replace("[Course number]", "EE091IU")
                    set_run_font(r, size_pt=10, italic=bool(r.italic), color=DARK_TEXT)

    # 2. Update cover page paragraphs while preserving layout spacing and page breaks
    def rewrite_p(p, text, size_pt=12, bold=False, align=None, color=DARK_TEXT):
        if align is not None:
            p.alignment = align
        for r in list(p.runs):
            p._p.remove(r._r)
        add_rich_runs(p, text, size_pt=size_pt, bold=bold, color=color)

    rewrite_p(doc.paragraphs[3], "International University", size_pt=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[4], "School of Electrical Engineering", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[7], "ELECTRONICS DEVICES LAB", size_pt=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[8], "Course ID: EE091IU", size_pt=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(
        doc.paragraphs[11],
        "LAB 5: BJT BIASING IN SWITCHING APPLICATIONS (NPN TRANSISTOR)",
        size_pt=18,
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        color=NAVY,
    )
    rewrite_p(doc.paragraphs[12], "Submitted by", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[13], "Name: Nguyễn Lê Minh Sang", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[14], "ID: EEACIU24096", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[15], "Name: Nguyễn Gia Huy", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER)
    rewrite_p(doc.paragraphs[16], "ID: EEACIU24047", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER)

    rewrite_p(doc.paragraphs[24], "\tDate Performed:\t\t21/11/2026", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT)
    rewrite_p(doc.paragraphs[25], "\tDate Submitted:\t\t21/11/2026", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT)
    rewrite_p(doc.paragraphs[26], "\tLab Section:\t\tLab 5", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT)
    rewrite_p(doc.paragraphs[27], "\tCourse Instructor:\t\tLecturer Pham Trung Kien", size_pt=12, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT)

    # Standardize fonts on Grading Guideline & Team Contribution pages (P[28]..P[39] and T[00], T[01])
    for idx in range(28, 40):
        p = doc.paragraphs[idx]
        for r in p.runs:
            if r.text:
                sz = r.font.size.pt if r.font.size else 12
                set_run_font(r, size_pt=sz, bold=bool(r.bold), italic=bool(r.italic), color=DARK_TEXT)

    # Clean punctuation in Team Contribution table (T[01]) for ABET English consistency
    t_contrib = doc.tables[1]
    contrib_clean = {
        (1, 2): "Proofread report; coordinate tasks",
        (2, 1): "Gather components; build the circuits; answer in-class questions",
        (2, 2): "Record data; test the circuits; answer in-class questions",
    }
    for (r_i, c_i), new_txt in contrib_clean.items():
        cell = t_contrib.cell(r_i, c_i)
        # Clear extra paragraphs in the cell if any, rewrite first paragraph cleanly
        for extra_p in list(cell.paragraphs)[1:]:
            extra_p._element.getparent().remove(extra_p._element)
        p0 = cell.paragraphs[0]
        for r in list(p0.runs):
            p0._p.remove(r._r)
        add_rich_runs(p0, new_txt, size_pt=11, color=DARK_TEXT)

    for tbl in doc.tables[:2]:
        for row in tbl.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        if r.text:
                            sz = r.font.size.pt if r.font.size else 11
                            set_run_font(r, size_pt=sz, bold=bool(r.bold), italic=bool(r.italic), color=DARK_TEXT)

    # 3. Remove all body elements after P[39] (the page break after TEAM CONTRIBUTION), preserving sectPr
    body = doc.element.body
    cutoff_el = doc.paragraphs[39]._p
    children = list(body)
    cut_idx = children.index(cutoff_el)
    for el in children[cut_idx + 1:]:
        if el.tag.endswith("sectPr"):
            continue
        body.remove(el)


# ---------------------------------------------------------------------------
# Build Full DOCX Content
# ---------------------------------------------------------------------------
def build_docx(page_map=None):
    if page_map is None:
        page_map = DEFAULT_PAGE_MAP
    doc = docx.Document(str(TEMPLATE_PATH))
    prepare_template_front_matter(doc)

    # Set Normal style baseline to Times New Roman 12pt
    normal_style = doc.styles["Normal"]
    normal_style.font.name = FONT_NAME
    normal_style.font.size = Pt(12)

    # =========================================================================
    # FRONT MATTER: TOC, LIST OF FIGURES, LIST OF TABLES, NOMENCLATURE
    # =========================================================================
    add_heading_1(doc, "Table of Contents", page_break_before=False)
    toc_rows = [
        ("Section", "Title", "Page"),
        ("Front", "Grading Guideline for Lab Report", page_map["Grading Guideline for Lab Report"]),
        ("Front", "Team Contribution", page_map["Team Contribution"]),
        ("Front", "List of Figures", page_map["List of Figures"]),
        ("Front", "List of Tables", page_map["List of Tables"]),
        ("Front", "Nomenclature", page_map["Nomenclature"]),
        ("1", "Objectives", page_map["1. Objectives"]),
        ("2", "Theoretical Background", page_map["2. Theoretical Background"]),
        ("  2.1", "NPN BJT Operating Regions and Switching Action", page_map["2.1 NPN BJT Operating Regions and Switching Action"]),
        ("  2.2", "Governing Equations (Sedra & Smith, 6th Edition)", page_map["2.2 Governing Equations (Sedra & Smith, 6th Edition)"]),
        ("  2.3", "Step-by-Step Theoretical Calculations", page_map["2.3 Step-by-Step Theoretical Calculations"]),
        ("3", "Experimental Procedure", page_map["3. Experimental Procedure"]),
        ("  3.1", "Material and Equipment", page_map["3.1 Material and Equipment"]),
        ("  3.2", "Experiment 1: Static Biasing and Switching", page_map["3.2 Experiment 1: Static Biasing and Switching"]),
        ("  3.3", "Experiment 2: Switching Response to Square Wave", page_map["3.3 Experiment 2: Switching Response to Square Wave"]),
        ("  3.4", "Experiment 3: Driving an LED", page_map["3.4 Experiment 3: Driving an LED"]),
        ("4", "Experimental Results", page_map["4. Experimental Results"]),
        ("  4.1", "Experiment 1: Static Biasing and Switching", page_map["4.1 Experiment 1: Static Biasing and Switching"]),
        ("  4.2", "Experiment 2: Switching Response to Square Wave", page_map["4.2 Experiment 2: Switching Response to Square Wave"]),
        ("  4.3", "Experiment 3: Driving an LED", page_map["4.3 Experiment 3: Driving an LED"]),
        ("5", "Discussion of Results", page_map["5. Discussion of Results"]),
        ("  5.1", "Experiment 2 Switching Waveform Analysis (Lab Question 2c)", page_map["5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)"]),
        ("  5.2", "Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)", page_map["5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)"]),
        ("  5.3", "Non-Ideal Deviations and Lab Verification Checklist", page_map["5.3 Non-Ideal Deviations and Lab Verification Checklist"]),
        ("  5.4", "Summary", page_map["5.4 Summary"]),
        ("Ref.", "References", page_map["References"]),
    ]
    add_index_table(doc, toc_rows, col_widths=(0.80, 5.45, 0.75))
    add_body_p(
        doc,
        "Note: Page numbers above are verified directly against the rendered Word layout of this report. If pagination shifts after pasting oscilloscope screenshots or simulation figures during the lab session, update the corresponding entries in the Page column.",
        space_after=8,
        size_pt=10,
        italic=True,
        color=MUTED_TEXT,
    )

    add_heading_1(doc, "List of Figures", page_break_before=True)
    lof_rows = [("Figure", "Caption", "Page")] + [
        (f"Figure {i}", FIG_CAPTIONS[i], page_map[f"Figure {i}"]) for i in range(1, 8)
    ]
    add_index_table(doc, lof_rows, col_widths=(0.90, 5.40, 0.70))

    add_heading_1(doc, "List of Tables", page_break_before=False)
    lot_rows = [("Table", "Caption", "Page")] + [
        (f"Table {i}", TBL_CAPTIONS[i], page_map[f"Table {i}"]) for i in range(1, 5)
    ]
    add_index_table(doc, lot_rows, col_widths=(0.90, 5.40, 0.70))

    add_heading_1(doc, "Nomenclature", page_break_before=True)
    nom_rows = [
        ("V_{CC}", "DC collector supply voltage (5.0 V in all three experiments)"),
        ("V_{in}", "Input control voltage applied ahead of the base resistor R_{B} (0 V LOW or 5.0 V HIGH)"),
        ("V_{B}, V_{C}, V_{E}", "Node voltages at the base, collector, and emitter terminals relative to ground (V_{E} = 0 V)"),
        ("V_{BE}, V_{BE(on)}", "Base-emitter voltage and its piecewise-linear forward-conduction drop (0.70 V)"),
        ("V_{CE}, V_{CE(sat)}", "Collector-emitter voltage and its saturation value (0.20 V textbook model)"),
        ("V_{LED}", "Forward voltage drop of the collector-side LED (2.0 V assumed nominal; 1.8 V sensitivity check)"),
        ("I_{B}, I_{C}", "DC base current and collector current"),
        ("I_{C(sat)}", "Collector current set by the external supply and load network when Q1 is saturated"),
        ("I_{B(min)}, R_{B(max)}", "Minimum base current and maximum base resistance required to reach the edge of saturation"),
        ("R_{B}, R_{C}", "Base current-limiting resistor and collector load resistor (R_{C} = 470 Ω)"),
        ("β (h_{FE})", "DC common-emitter current gain of the 2N3904 (β_{min} = 100 at 10 mA, β_{typ} = 300)"),
        ("β_{forced}", "Forced current gain in saturation, defined as I_{C(sat)} / I_{B}"),
        ("ODF", "Overdrive factor, defined as I_{B} / I_{B(min)} = β / β_{forced} (values > 1 guarantee saturation)"),
        ("P_{Q}, P_{RC}, P_{RB}", "Steady-state power dissipated by transistor Q1, collector resistor R_{C}, and base resistor R_{B}"),
        ("t_{d}, t_{r}, t_{s}, t_{f}", "Delay time, rise time, storage time, and fall time of the switching transistor"),
    ]
    tbl_nom = doc.add_table(rows=len(nom_rows) + 1, cols=2)
    tbl_nom.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_nom)
    set_col_widths(tbl_nom, [1.55, 5.45])
    set_row_header(tbl_nom.rows[0])
    set_row_cant_split(tbl_nom.rows[0])
    populate_cell(tbl_nom.rows[0].cells[0], "Symbol", size_pt=10.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), shade=NAVY_HEX)
    populate_cell(tbl_nom.rows[0].cells[1], "Definition", size_pt=10.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), align=WD_ALIGN_PARAGRAPH.LEFT, shade=NAVY_HEX)
    for ri, (sym, desc) in enumerate(nom_rows, start=1):
        row = tbl_nom.rows[ri]
        set_row_cant_split(row)
        sh = CALC_SHADE if ri % 2 == 0 else None
        populate_cell(row.cells[0], sym, size_pt=10.5, bold=True, shade=sh)
        populate_cell(row.cells[1], desc, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.LEFT, shade=sh)

    # =========================================================================
    # SECTION 1: OBJECTIVES
    # =========================================================================
    add_heading_1(doc, "1. Objectives", page_break_before=True)
    add_body_p(
        doc,
        "Lab 5 investigates how an NPN bipolar junction transistor (2N3904) behaves when biased strictly as an electronic switch. Instead of amplifying small analog signals, the transistor swings between full cutoff and full saturation under static DC levels, a 1 kHz square wave, and a collector-side LED load.",
    )
    add_bullet_p(doc, "Observe the ON/OFF switching behavior of a 2N3904 NPN BJT driven by digital logic voltage levels (0 V and 5 V).")
    add_bullet_p(doc, "Calculate and verify the biasing conditions required to place the transistor reliably in cutoff and saturation.")
    add_bullet_p(doc, "Design, analyze, and test a basic transistor switching stage driving both a purely resistive load (470 Ω) and a series LED load across four base resistor values.")

    # =========================================================================
    # SECTION 2: THEORETICAL BACKGROUND
    # =========================================================================
    add_heading_1(doc, "2. Theoretical Background")

    add_heading_2(doc, "2.1 NPN BJT Operating Regions and Switching Action")
    add_body_p(
        doc,
        "A bipolar junction transistor contains two p-n junctions: base-emitter (B-E) and base-collector (B-C). How those two junctions are biased determines which of three operating regions the device occupies. Figure 1 shows the standard circuit symbols and TO-92 package pinouts for the 2N3904 NPN transistor used in this lab alongside its PNP complement (2N3906).",
    )
    add_figure(doc, FIG_DIR / "fig1_bjt_symbol_pinout.png", 3.65, f"Figure 1. {FIG_CAPTIONS[1]}")

    add_table_caption(doc, f"Table 1. {TBL_CAPTIONS[1]}")
    t1_data = [
        ("Region", "B-E Junction", "B-C Junction", "Terminal Condition", "Primary Use"),
        ("Cutoff", "Reverse biased", "Reverse biased", "V_{BE} < 0.70 V, I_{B} ≈ 0, I_{C} ≈ 0, V_{CE} ≈ V_{CC}", "Open switch (OFF)"),
        ("Active", "Forward biased", "Reverse biased", "V_{BE} ≈ 0.70 V, I_{C} = βI_{B}, V_{CE} > V_{CE(sat)}", "Linear amplification"),
        ("Saturation", "Forward biased", "Forward biased", "V_{BE} ≈ 0.70 V, V_{CE} ≈ 0.20 V, I_{C} < βI_{B}", "Closed switch (ON)"),
    ]
    tbl1 = doc.add_table(rows=len(t1_data), cols=5)
    tbl1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl1)
    set_col_widths(tbl1, [0.95, 1.15, 1.15, 2.35, 1.40])
    set_row_header(tbl1.rows[0])
    for ri, rdata in enumerate(t1_data):
        row = tbl1.rows[ri]
        set_row_cant_split(row)
        is_hdr = (ri == 0)
        sh = NAVY_HEX if is_hdr else (CALC_SHADE if ri % 2 == 0 else None)
        for ci, val in enumerate(rdata):
            populate_cell(
                row.cells[ci],
                val,
                size_pt=10.5,
                bold=is_hdr or (ci == 0),
                color=RGBColor(0xFF, 0xFF, 0xFF) if is_hdr else DARK_TEXT,
                align=WD_ALIGN_PARAGRAPH.CENTER if (is_hdr or ci < 3) else WD_ALIGN_PARAGRAPH.LEFT,
                shade=sh,
            )

    add_body_p(doc, "", space_after=2)
    add_body_p(
        doc,
        "Switching circuits deliberately skip the active region except during brief transitions. When a logic HIGH (5.0 V) reaches the base through R_{B}, enough base current flows to forward-bias both junctions and drive the 2N3904 into saturation. Collector-to-emitter voltage collapses to V_{CE(sat)} ≈ 0.20 V, so the load connects nearly straight to ground and output V_{C} drops LOW (Figure 2).",
    )
    add_figure(doc, FIG_DIR / "fig2_switch_high.png", 4.0, f"Figure 2. {FIG_CAPTIONS[2]}")
    add_body_p(
        doc,
        "When the base input falls to logic LOW (0 V), V_{BE} drops below the turn-on threshold. Base current stops, collector current falls to near zero, and no voltage drops across R_{C}. The transistor behaves like an open switch, leaving V_{C} pulled HIGH to V_{CC} = 5.0 V (Figure 3). Because HIGH in produces LOW out and LOW in produces HIGH out, this common-emitter stage acts as a digital inverter.",
    )
    add_figure(doc, FIG_DIR / "fig3_switch_low.png", 4.0, f"Figure 3. {FIG_CAPTIONS[3]}")

    add_heading_2(doc, "2.2 Governing Equations (Sedra & Smith, 6th Edition)")
    add_body_p(
        doc,
        "All theoretical predictions in this report follow the piecewise-linear DC BJT model from Adel S. Sedra and Kenneth C. Smith, *Microelectronic Circuits* (6th ed., Chapter 6). For the grounded-emitter 2N3904 stage (V_{E} = 0 V), V_{B} = V_{BE} and V_{C} = V_{CE}. The baseline device parameters used in hand calculations are V_{CC} = 5.0 V, R_{C} = 470 Ω, V_{BE(on)} = 0.70 V, and V_{CE(sat)} = 0.20 V. From the ON Semiconductor 2N3904 datasheet at I_{C} = 10 mA, the minimum guaranteed DC current gain is β_{min} = 100 and the typical gain is β_{typ} = 300.",
    )
    add_body_p(
        doc,
        "In cutoff (V_{in} = 0 V), V_{BE} = 0.00 V < 0.70 V, so I_{B} = 0 mA, I_{C} = 0 mA, and V_{CE} = V_{C} = V_{CC} = 5.00 V. When V_{in} = 5.0 V turns the B-E junction on, Kirchhoff's Voltage Law (KVL) around the base loop gives the base current:",
    )
    add_equation_block(doc, "I_{B}  =  (V_{in} - V_{BE(on)}) / R_{B}", 1)
    add_body_p(
        doc,
        "Assuming saturation, KVL around the collector-emitter loop gives the saturation collector current for a purely resistive load (Experiment 1) and for a series LED plus resistor load (Experiment 3):",
    )
    add_equation_block(doc, "I_{C(sat)}  =  (V_{CC} - V_{CE(sat)}) / R_{C}        [Experiment 1: resistive load]", 2)
    add_equation_block(doc, "I_{C(sat)}  =  (V_{CC} - V_{LED} - V_{CE(sat)}) / R_{C}        [Experiment 3: LED + resistor load]", 3)
    add_body_p(
        doc,
        "Saturation is only valid when the forced current gain β_{forced} stays strictly below the transistor's actual current gain β:",
    )
    add_equation_block(doc, "β_{forced}  =  I_{C(sat)} / I_{B}  <  β", 4)
    add_body_p(
        doc,
        "Setting β_{forced} = β defines the edge-of-saturation limits, namely the minimum required base current I_{B(min)} and the maximum permissible base resistance R_{B(max)}:",
    )
    add_equation_block(doc, "I_{B(min)}  =  I_{C(sat)} / β,        R_{B(max)}  =  (V_{in} - V_{BE(on)}) / I_{B(min)}", 5)
    add_body_p(
        doc,
        "To measure how far the transistor sits past the saturation boundary, we evaluate the overdrive factor (ODF):",
    )
    add_equation_block(doc, "ODF  =  I_{B} / I_{B(min)}  =  β / β_{forced}", 6)
    add_body_p(
        doc,
        "An ODF greater than 1 confirms saturation. Finally, checking power dissipation verifies that neither the 2N3904 (625 mW maximum package rating) nor the standard 0.25 W resistors are thermally stressed:",
    )
    add_equation_block(doc, "P_{Q}  =  V_{CE} I_{C} + V_{BE} I_{B},        P_{RC}  =  I_{C}^{2} R_{C},        P_{RB}  =  I_{B}^{2} R_{B}", 7)
    add_body_p(
        doc,
        "If the transistor ever stalled midway in the active region (at V_{CE} = V_{CC}/2 for a resistive load, or (V_{CC} - V_{LED})/2 with an LED), collector dissipation would peak at P_{C,max} = V_{CC}^{2}/(4R_{C}) or (V_{CC} - V_{LED})^{2}/(4R_{C}).",
    )

    add_heading_2(doc, "2.3 Step-by-Step Theoretical Calculations")

    add_heading_3(doc, "Experiment 1: Static Biasing and Switching (R_{B} = 10 kΩ)")
    add_body_p(
        doc,
        "**State 1: V_{in} = 0 V (Cutoff).** Since V_{in} = 0 V provides zero forward bias to the B-E junction, V_{BE} = V_{B} = 0.00 V and I_{B} = 0.000 mA. With no base current, Q1 stays OFF (I_{C} = 0.00 mA), giving V_{CE} = V_{C} = 5.00 V - (0)(470 Ω) = 5.00 V. All component powers equal 0.00 mW.",
    )
    add_body_p(
        doc,
        "**State 2: V_{in} = 5.0 V (Saturation).** Applying Equations (1) and (2) with R_{B} = 10 kΩ and R_{C} = 470 Ω:",
    )
    add_bullet_p(doc, "Base current: I_{B} = (5.0 - 0.70) / 10,000 = 4.30 / 10,000 = **0.430 mA** (430.0 μA).")
    add_bullet_p(doc, "Saturation collector current: I_{C(sat)} = (5.0 - 0.20) / 470 = 4.80 / 470 = **10.2128 mA ≈ 10.21 mA**.")
    add_bullet_p(doc, "Node voltages: V_{B} = V_{BE} = **0.70 V**; V_{C} = V_{CE} = **0.20 V**.")
    add_bullet_p(doc, "Saturation verification: β_{forced} = 10.2128 / 0.430 = **23.75**. Because 23.75 < β_{min} = 100, Q1 is solidly saturated even for a worst-case 2N3904.")
    add_bullet_p(doc, "Boundary limits: At β_{min} = 100, I_{B(min)} = 10.2128 mA / 100 = **102.13 μA**, R_{B(max)} = 4.30 / 102.13 μA = **42.10 kΩ**, and ODF_{100} = 430.0 / 102.13 = **4.21**. At β_{typ} = 300, I_{B(min)} = **34.04 μA**, R_{B(max)} = **126.31 kΩ**, and ODF_{300} = **12.63**.")
    add_bullet_p(doc, "Power dissipation: P_{Q} = (0.20)(10.2128 mA) + (0.70)(0.430 mA) = 2.04 + 0.30 = **2.34 mW** (far below the 625 mW rating). Resistor dissipations are P_{RC} = (10.2128 mA)^{2}(470 Ω) = **49.02 mW** and P_{RB} = (0.430 mA)^{2}(10 kΩ) = **1.85 mW**. Even the worst-case active-region collector peak is only P_{C,max} = 5.0^{2} / (4 × 470) = **13.30 mW**.")

    add_heading_3(doc, "Experiment 2: Switching Response to a 1 kHz Square Wave")
    add_body_p(
        doc,
        "The circuit stays identical to Experiment 1, while the signal generator drives V_{in}(t) with a 0-5 V square wave at f = 1 kHz. Assuming a standard 50% duty cycle (D = 50%), the period is T = 1/f = **1.00 ms**, split evenly into T_{HIGH} = T_{LOW} = **0.50 ms** (500 μs).",
    )
    add_bullet_p(doc, "Base waveform V_{B}(t): Swings from **0.00 V** (when V_{in} = 0 V) to **0.70 V** (when V_{in} = 5.0 V), remaining **in phase (0°)** with V_{in}(t). It never reaches 5.0 V because the forward-biased B-E diode clamps V_{B} near 0.70 V while R_{B} drops the remaining 4.30 V.")
    add_bullet_p(doc, "Collector waveform V_{C}(t): Swings from **5.00 V** (cutoff) down to **0.20 V** (saturation), shifted by **180°** relative to V_{in}(t).")
    add_bullet_p(doc, "Switching timing check: Per the ON Semiconductor 2N3904 datasheet, t_{d} ≤ 35 ns, t_{r} ≤ 35 ns (t_{on} = t_{d} + t_{r} ≤ **70 ns**), t_{s} ≤ 200 ns, and t_{f} ≤ 50 ns (t_{off} = t_{s} + t_{f} ≤ **250 ns**). Combined switching time is at most 320 ns, or at most **0.064%** of the 500 μs half-period. Even without a negative turn-off pulse on a lab breadboard (where stored base charge bleeds passively through 10 kΩ and t_{s} can expand to roughly 0.5-2 μs), total transition delay stays below 0.5% of T/2. Transitions therefore look virtually vertical at 1 kHz.")

    add_heading_3(doc, "Experiment 3: Driving a Collector-Side LED across Four Base Resistors")
    add_body_p(
        doc,
        "Inserting a standard indicator LED in series with R_{C} = 470 Ω removes V_{LED} from the collector loop voltage headroom. Because the lab manual does not specify LED color, we assume a nominal **V_{LED} = 2.0 V** (typical red/yellow indicator LED) and also run a sensitivity check at **V_{LED} = 1.8 V**. When V_{in} = 0 V, Q1 is in cutoff, I_{C} = 0 mA, and the LED stays OFF. When V_{in} = 5.0 V, Equation (3) gives:",
    )
    add_bullet_p(doc, "Saturation collector current (V_{LED} = 2.0 V): I_{C(sat)} = (5.0 - 2.0 - 0.20) / 470 = 2.80 / 470 = **5.9574 mA ≈ 5.96 mA**.")
    add_bullet_p(doc, "Collector-branch power: P_{RC} = (5.9574 mA)^{2}(470 Ω) = **16.68 mW**; P_{LED} = (2.0 V)(5.9574 mA) = **11.91 mW**; active-region collector peak P_{C,max} = (5.0 - 2.0)^{2} / (4 × 470) = **4.79 mW**.")
    add_bullet_p(doc, "Saturation limits at β_{min} = 100: I_{B(min)} = 5.9574 mA / 100 = **59.57 μA**, R_{B(max)} = 4.30 / 59.57 μA = **72.18 kΩ**.")
    add_bullet_p(doc, "Saturation limits at β_{typ} = 300: I_{B(min)} = 5.9574 mA / 300 = **19.86 μA**, R_{B(max)} = 4.30 / 19.86 μA = **216.54 kΩ**.")
    add_bullet_p(doc, "Standard switching design rule (β_{forced} = 10): I_{B} ≈ 0.60 mA, corresponding to R_{B} ≈ **7.22 kΩ** (sits directly between the lab's 4.7 kΩ and 10 kΩ resistors).")
    add_bullet_p(doc, "Sensitivity check (V_{LED} = 1.8 V): I_{C(sat)} increases by +7.14% to **6.38 mA**, shifting I_{B(min,100)} to **63.83 μA** and R_{B(max,100)} to **67.37 kΩ**. All four test resistors still sit below 67.37 kΩ, so saturation still holds.")

    add_body_p(
        doc,
        "Evaluating Equations (1), (4), (6), and (7) across the four assigned base resistors at V_{in} = 5.0 V (with V_{BE} = 0.70 V, V_{CE} = 0.20 V, I_{C} = 5.96 mA):",
    )
    add_bullet_p(doc, "**R_{B} = 4.7 kΩ:** I_{B} = 4.30 / 4.7 kΩ = **0.915 mA**; β_{forced} = **6.51**; ODF_{100} = **15.36**; ODF_{300} = **46.07**; P_{Q} = **1.83 mW**; P_{RB} = **3.93 mW** (Deep Saturation).")
    add_bullet_p(doc, "**R_{B} = 10 kΩ:** I_{B} = 4.30 / 10 kΩ = **0.430 mA**; β_{forced} = **13.85**; ODF_{100} = **7.22**; ODF_{300} = **21.65**; P_{Q} = **1.49 mW**; P_{RB} = **1.85 mW** (Saturation).")
    add_bullet_p(doc, "**R_{B} = 22 kΩ:** I_{B} = 4.30 / 22 kΩ = **0.195 mA** (0.1955 mA); β_{forced} = **30.48**; ODF_{100} = **3.28**; ODF_{300} = **9.84**; P_{Q} = **1.33 mW**; P_{RB} = **0.84 mW** (Saturation).")
    add_bullet_p(doc, "**R_{B} = 47 kΩ:** I_{B} = 4.30 / 47 kΩ = **0.0915 mA**; β_{forced} = **65.12**; ODF_{100} = **1.54**; ODF_{300} = **4.61**; P_{Q} = **1.26 mW**; P_{RB} = **0.39 mW** (Soft Saturation).")

    # =========================================================================
    # SECTION 3: EXPERIMENTAL PROCEDURE
    # =========================================================================
    add_heading_1(doc, "3. Experimental Procedure", page_break_before=True)

    add_heading_2(doc, "3.1 Material and Equipment")
    equip = [
        "Dual-channel Digital Storage Oscilloscope (with 10× probes)",
        "DC Power Supply (set to V_{CC} = 5.0 V with current limit near 100 mA)",
        "Function / Signal Generator (capable of 0-5 V unipolar 1 kHz square wave)",
        "Solderless breadboard and jumper wires",
        "Digital Multimeter (DMM) for DC voltage, current, and resistance checks",
        "NPN Bipolar Junction Transistor: 2N3904 (TO-92 package; flat face toward viewer reads E-B-C from left to right)",
        "Resistors (0.25 W): R_{C} = 470 Ω; R_{B} ∈ {4.7 kΩ, 10 kΩ, 22 kΩ, 47 kΩ} and a standard indicator LED",
    ]
    for idx, item in enumerate(equip, start=1):
        add_numbered_p(doc, f"{idx}.", item, space_after=2.5)

    add_heading_2(doc, "3.2 Experiment 1: Static Biasing and Switching")
    add_body_p(
        doc,
        "Wire the grounded-emitter switching circuit shown in Figure 4 on the breadboard using V_{CC} = 5.0 V, R_{C} = 470 Ω, R_{B} = 10 kΩ, and Q1 = 2N3904. Confirm the TO-92 emitter, base, and collector pin orientation before applying power.",
    )
    add_figure(doc, FIG_DIR / "fig4_exp1_circuit.png", 3.7, f"Figure 4. {FIG_CAPTIONS[4]}")
    add_numbered_p(doc, "1.", "Connect the input node V_{in} directly to ground (0 V) for the cutoff test.")
    add_numbered_p(doc, "2.", "Measure V_{BE}, V_{CE}, V_{C}, and V_{B} with the DMM in DC voltage mode. Measure I_{B} and I_{C} by placing the DMM ammeter in series with the base and collector branches (or compute them from the measured drops across R_{B} and R_{C} to eliminate ammeter burden voltage).")
    add_numbered_p(doc, "3.", "Move V_{in} to the +5.0 V rail for the saturation test, repeat all six measurements, and enter both simulation and bench readings into Table 2.")

    add_heading_2(doc, "3.3 Experiment 2: Switching Response to Square Wave")
    add_numbered_p(doc, "1.", "Keep the Experiment 1 breadboard circuit unchanged (V_{CC} = 5.0 V, R_{C} = 470 Ω, R_{B} = 10 kΩ).")
    add_numbered_p(doc, "2.", "Configure the signal generator for a 1 kHz square wave toggling between 0 V (LOW) and 5.0 V (HIGH) at 50% duty cycle. Check the generator's output-load setting (High-Z vs 50 Ω) with the oscilloscope first so the actual amplitude at the breadboard is 0-5 V rather than 0-10 V.")
    add_numbered_p(doc, "3.", "Connect the generator output to V_{in} and tie its ground clip to the circuit ground.")
    add_numbered_p(doc, "4.", "Set both oscilloscope channels to DC coupling with a shared 0 V reference baseline. Probe V_{B} on Channel 1 and V_{C} on Channel 2, trigger on the rising edge of Channel 1, and capture the steady-state waveforms for Section 4.2.")

    add_heading_2(doc, "3.4 Experiment 3: Driving an LED")
    add_body_p(
        doc,
        "Modify the collector branch of Experiment 1 by inserting an LED in series with R_{C} = 470 Ω (anode toward R_{C}, cathode toward the 2N3904 collector), as illustrated in Figure 5.",
    )
    add_figure(doc, FIG_DIR / "fig5_exp3_led_circuit.png", 5.5, f"Figure 5. {FIG_CAPTIONS[5]}")
    add_numbered_p(doc, "1.", "Start with R_{B} = 10 kΩ. Toggle V_{in} between LOW (0 V) and HIGH (5.0 V) using a jumper wire, push button, or low-frequency square wave, and confirm that the LED switches cleanly OFF and ON.")
    add_numbered_p(doc, "2.", "Hold V_{in} at HIGH (5.0 V) and measure V_{BE}, V_{CE}, I_{B}, and I_{C} (plus the LED forward drop V_{LED} for reference).")
    add_numbered_p(doc, "3.", "Power down briefly between resistor swaps and repeat the V_{in} = 5.0 V measurements for R_{B} = 4.7 kΩ, 22 kΩ, and 47 kΩ. Record all simulation and bench values in Table 4 and note any visual brightness change in the bench observation log.")

    # =========================================================================
    # SECTION 4: EXPERIMENTAL RESULTS
    # =========================================================================
    add_heading_1(doc, "4. Experimental Results", page_break_before=True)
    add_body_p(
        doc,
        "The tables below hold all verified hand calculations in the shaded *Calculation* rows. Every *Simulation* row, *Measurement* row, oscilloscope frame, and bench observation entry is intentionally left blank so experimental data can be filled in directly during LTspice simulation and laboratory testing.",
    )

    # --- 4.1 Experiment 1 ---
    add_heading_2(doc, "4.1 Experiment 1: Static Biasing and Switching")
    add_table_caption(doc, f"Table 2. {TBL_CAPTIONS[2]}")

    t2_headers = ["V_{in}", "Mode", "V_{BE} (V)", "V_{CE} (V)", "V_{C} (V)", "V_{B} (V)", "I_{B} (mA)", "I_{C} (mA)"]
    t2_rows = [
        ("0 V", "Calculation", "0.00", "5.00", "5.00", "0.00", "0.000", "0.00"),
        ("0 V", "Simulation",  "",     "",     "",     "",     "",      ""),
        ("0 V", "Measurement", "",     "",     "",     "",     "",      ""),
        ("5 V", "Calculation", "0.70", "0.20", "0.20", "0.70", "0.430", "10.21"),
        ("5 V", "Simulation",  "",     "",     "",     "",     "",      ""),
        ("5 V", "Measurement", "",     "",     "",     "",     "",      ""),
    ]
    tbl2 = doc.add_table(rows=1 + len(t2_rows), cols=8)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl2)
    set_col_widths(tbl2, [0.58, 1.12, 0.88, 0.88, 0.88, 0.88, 0.89, 0.89])
    set_row_header(tbl2.rows[0])
    set_row_cant_split(tbl2.rows[0])
    set_row_height(tbl2.rows[0], 24)
    for ci, h in enumerate(t2_headers):
        populate_cell(tbl2.rows[0].cells[ci], h, size_pt=10.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), shade=NAVY_HEX)

    for ri, rvals in enumerate(t2_rows, start=1):
        row = tbl2.rows[ri]
        set_row_cant_split(row)
        set_row_height(row, 22)
        is_calc = (rvals[1] == "Calculation")
        sh = CALC_SHADE if is_calc else None
        for ci, val in enumerate(rvals):
            if ci == 0:
                continue
            populate_cell(
                row.cells[ci],
                val,
                size_pt=10.5,
                bold=(ci == 1 and is_calc),
                align=WD_ALIGN_PARAGRAPH.LEFT if ci == 1 else WD_ALIGN_PARAGRAPH.CENTER,
                shade=sh,
            )
    # Merge V_in vertical cells (0 V: rows 1-3; 5 V: rows 4-6)
    tbl2.cell(1, 0).merge(tbl2.cell(3, 0))
    tbl2.cell(4, 0).merge(tbl2.cell(6, 0))
    populate_cell(tbl2.cell(1, 0), "0 V", size_pt=10.5, bold=True)
    populate_cell(tbl2.cell(4, 0), "5 V", size_pt=10.5, bold=True)

    # --- 4.2 Experiment 2 ---
    add_heading_2(doc, "4.2 Experiment 2: Switching Response to Square Wave")
    add_table_caption(doc, f"Table 3. {TBL_CAPTIONS[3]}")

    t3_rows = [
        ("Parameter", "Theoretical Prediction", "Measured / Observed (Lab)"),
        ("Input V_{in}(t) levels & period", "0.00 V to 5.00 V; T = 1.00 ms (T/2 = 0.50 ms)", ""),
        ("Base voltage V_{B}(t) levels", "0.00 V (OFF) to 0.70 V (clamped ON)", ""),
        ("Base phase relative to V_{in}(t)", "0° (in phase)", ""),
        ("Collector voltage V_{C}(t) levels", "5.00 V (cutoff) to 0.20 V (saturation)", ""),
        ("Collector phase relative to V_{in}(t)", "180° (logic inversion)", ""),
        ("2N3904 switching times (datasheet)", "t_{on} ≤ 70 ns, t_{off} ≤ 250 ns (≤ 0.064% of T/2)", ""),
    ]
    tbl3 = doc.add_table(rows=len(t3_rows), cols=3)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl3)
    set_col_widths(tbl3, [2.15, 2.85, 2.00])
    set_row_header(tbl3.rows[0])
    for ri, rvals in enumerate(t3_rows):
        row = tbl3.rows[ri]
        set_row_cant_split(row)
        set_row_height(row, 22)
        is_hdr = (ri == 0)
        for ci, val in enumerate(rvals):
            sh = NAVY_HEX if is_hdr else (CALC_SHADE if ci == 1 else None)
            populate_cell(
                row.cells[ci],
                val,
                size_pt=10.5,
                bold=is_hdr or (ci == 0),
                color=RGBColor(0xFF, 0xFF, 0xFF) if is_hdr else DARK_TEXT,
                align=WD_ALIGN_PARAGRAPH.CENTER if is_hdr else WD_ALIGN_PARAGRAPH.LEFT,
                shade=sh,
            )

    add_figure(doc, FIG_DIR / "fig6_exp2_theoretical_waveforms.png", 5.6, f"Figure 6. {FIG_CAPTIONS[6]}")

    # Oscilloscope screenshot placeholder box
    tbl_scope = doc.add_table(rows=1, cols=1)
    tbl_scope.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_col_widths(tbl_scope, [6.6])
    set_row_cant_split(tbl_scope.rows[0])
    set_row_height(tbl_scope.rows[0], 175, rule="atLeast")
    sc_cell = tbl_scope.cell(0, 0)
    sc_cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_margins(sc_cell, top=140, bottom=140, left=160, right=160)
    set_cell_borders(
        sc_cell,
        top={"val": "dashed", "sz": "8", "color": NAVY_HEX},
        bottom={"val": "dashed", "sz": "8", "color": NAVY_HEX},
        left={"val": "dashed", "sz": "8", "color": NAVY_HEX},
        right={"val": "dashed", "sz": "8", "color": NAVY_HEX},
    )
    p_sc = sc_cell.paragraphs[0]
    p_sc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_rich_runs(
        p_sc,
        "[Oscilloscope Capture Area - Experiment 2]\nPaste measured CH1 (V_{B}) and CH2 (V_{C}) oscilloscope screenshots here during the lab session.",
        size_pt=10.5,
        italic=True,
        color=MUTED_TEXT,
    )

    # --- 4.3 Experiment 3 ---
    add_heading_2(doc, "4.3 Experiment 3: Driving an LED")
    add_table_caption(doc, f"Table 4. {TBL_CAPTIONS[4]}")

    t4_headers = ["R_{B}", "Mode", "V_{BE} (V)", "V_{CE} (V)", "I_{B} (mA)", "I_{C} (mA)"]
    t4_blocks = [
        ("4.7 kΩ", ("0.70", "0.20", "0.915", "5.96")),
        ("10 kΩ",  ("0.70", "0.20", "0.430", "5.96")),
        ("22 kΩ",  ("0.70", "0.20", "0.195", "5.96")),
        ("47 kΩ",  ("0.70", "0.20", "0.0915", "5.96")),
    ]
    tbl4 = doc.add_table(rows=1 + len(t4_blocks) * 3, cols=6)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl4)
    set_col_widths(tbl4, [0.95, 1.25, 1.20, 1.20, 1.20, 1.20])
    set_row_header(tbl4.rows[0])
    set_row_cant_split(tbl4.rows[0])
    set_row_height(tbl4.rows[0], 24)
    for ci, h in enumerate(t4_headers):
        populate_cell(tbl4.rows[0].cells[ci], h, size_pt=10.5, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), shade=NAVY_HEX)

    for bi, (rb_label, calc_vals) in enumerate(t4_blocks):
        base_r = 1 + bi * 3
        modes = [
            ("Calculation", calc_vals),
            ("Simulation",  ("", "", "", "")),
            ("Measurement", ("", "", "", "")),
        ]
        for mi, (mode_name, vals) in enumerate(modes):
            ri = base_r + mi
            row = tbl4.rows[ri]
            set_row_cant_split(row)
            set_row_height(row, 21)
            is_calc = (mode_name == "Calculation")
            sh = CALC_SHADE if is_calc else None
            populate_cell(
                row.cells[1],
                mode_name,
                size_pt=10.5,
                bold=is_calc,
                align=WD_ALIGN_PARAGRAPH.LEFT,
                shade=sh,
            )
            for vi, val in enumerate(vals):
                populate_cell(row.cells[2 + vi], val, size_pt=10.5, shade=sh)
        tbl4.cell(base_r, 0).merge(tbl4.cell(base_r + 2, 0))
        populate_cell(tbl4.cell(base_r, 0), rb_label, size_pt=10.5, bold=True)

    add_body_p(doc, "", space_after=2)
    add_body_p(doc, "**Bench Observation Log (Experiment 3 - Fill In During Lab):**", space_after=3, size_pt=11)
    log_rows = [
        ("Observation Item", "Recorded Bench Value / Notes"),
        ("LED color and measured forward drop V_{LED} (V)", ""),
        ("LED ON/OFF behavior at V_{in} = 0 V vs. 5 V (R_{B} = 10 kΩ)", ""),
        ("Measured DC current gain h_{FE} (β) of bench 2N3904", ""),
        ("Visual LED brightness trend from R_{B} = 4.7 kΩ to 47 kΩ", ""),
    ]
    tbl_log = doc.add_table(rows=len(log_rows), cols=2)
    tbl_log.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_log)
    set_col_widths(tbl_log, [3.55, 3.45])
    set_row_header(tbl_log.rows[0])
    for ri, (k, v) in enumerate(log_rows):
        row = tbl_log.rows[ri]
        set_row_cant_split(row)
        set_row_height(row, 22)
        is_hdr = (ri == 0)
        populate_cell(
            row.cells[0],
            k,
            size_pt=10.5,
            bold=is_hdr or True,
            color=RGBColor(0xFF, 0xFF, 0xFF) if is_hdr else DARK_TEXT,
            align=WD_ALIGN_PARAGRAPH.LEFT,
            shade=NAVY_HEX if is_hdr else CALC_SHADE,
        )
        populate_cell(
            row.cells[1],
            v,
            size_pt=10.5,
            bold=is_hdr,
            color=RGBColor(0xFF, 0xFF, 0xFF) if is_hdr else DARK_TEXT,
            align=WD_ALIGN_PARAGRAPH.LEFT,
            shade=NAVY_HEX if is_hdr else None,
        )

    add_figure(doc, FIG_DIR / "fig7_exp3_rb_sweep.png", 5.7, f"Figure 7. {FIG_CAPTIONS[7]}")

    # =========================================================================
    # SECTION 5: DISCUSSION OF RESULTS
    # =========================================================================
    add_heading_1(doc, "5. Discussion of Results", page_break_before=True)

    add_heading_2(doc, "5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)")
    add_body_p(
        doc,
        "Driving the 2N3904 base with a 0-5 V, 1 kHz square wave exposes two clear features on the oscilloscope. First, collector voltage V_{C}(t) is a 180° inverted copy of V_{in}(t). When the input jumps to 5.0 V, base current rises to 0.430 mA, Q1 saturates, and V_{C} drops to roughly 0.20 V. When the input returns to 0 V, Q1 cuts off and R_{C} pulls V_{C} back up to 5.00 V. The stage functions directly as a single-transistor digital NOT gate.",
    )
    add_body_p(
        doc,
        "Second, base voltage V_{B}(t) never climbs to 5.0 V. Instead, it tracks V_{in}(t) in phase (0° shift) while remaining clamped between 0.00 V and roughly 0.70 V. Why? Because the forward-biased base-emitter junction behaves like a silicon diode connected straight to ground. Its exponential I-V curve locks V_{B} near 0.70 V, forcing the 10 kΩ base resistor to absorb the remaining 4.30 V.",
    )
    add_body_p(
        doc,
        "At 1 kHz, the half-period is 500 μs. Against that window, the 2N3904's datasheet turn-on time (t_{on} ≤ 70 ns) and turn-off time (t_{off} ≤ 250 ns) occupy at most 0.064% of one pulse. Transitions therefore appear sharp and vertical on a standard timebase. On an actual breadboard without a negative turn-off bias, excess minority carriers stored in the base during saturation must discharge passively through R_{B} = 10 kΩ. That passive discharge stretches storage time t_{s} to roughly 0.5-2 μs, which is still tiny at 1 kHz (< 0.5% of T/2) but would visibly distort the falling-to-rising collector edge if frequency were pushed into the hundreds of kilohertz.",
    )

    add_heading_2(doc, "5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)")

    add_heading_3(doc, "When is the transistor in cutoff or saturation?")
    add_body_p(
        doc,
        "An NPN transistor enters **cutoff** when both the B-E and B-C junctions are reverse-biased (or zero-biased). Practically, that occurs whenever V_{BE} falls below the turn-on threshold (~0.5-0.7 V), cutting off base current (I_{B} ≈ 0) and collector current (I_{C} ≈ 0). In Experiment 1, the collector node voltage rises to V_{CC} (5.00 V); in Experiment 3, the LED enters its non-conducting off state with zero collector current.",
    )
    add_body_p(
        doc,
        "The transistor enters **saturation** when both the B-E and B-C junctions are forward-biased. Two linked conditions confirm saturation: the base current exceeds the threshold I_{B(min)} = I_{C(sat)} / β (equivalently, β_{forced} = I_{C(sat)} / I_{B} < β), and the collector-emitter voltage drops to a small residual value V_{CE(sat)} ≈ 0.20 V (often 0.07-0.15 V on a real 2N3904 at 6-10 mA). Once saturated, I_{C} stops tracking βI_{B} and is instead fixed by the supply voltage and collector load.",
    )

    add_heading_3(doc, "What is the minimum base current required to drive the transistor into saturation?")
    add_body_p(
        doc,
        "The exact threshold depends on the collector saturation current and the transistor's actual β. In **Experiment 1** (I_{C(sat)} = 10.21 mA), reaching the edge of saturation requires I_{B(min)} = **102.13 μA** at the datasheet worst-case β_{min} = 100 (corresponding to R_{B(max)} = 42.10 kΩ), or **34.04 μA** at a typical β_{typ} = 300 (R_{B(max)} = 126.31 kΩ).",
    )
    add_body_p(
        doc,
        "In **Experiment 3** with the series LED (I_{C(sat)} = 5.96 mA at V_{LED} = 2.0 V), the minimum base current drops to **59.57 μA** at β_{min} = 100 (R_{B(max)} = 72.18 kΩ) and **19.86 μA** at β_{typ} = 300 (R_{B(max)} = 216.54 kΩ). If the lab LED is a lower-drop red unit with V_{LED} = 1.8 V, I_{C(sat)} rises to 6.38 mA and I_{B(min,100)} shifts slightly up to **63.83 μA** (R_{B(max,100)} = 67.37 kΩ). Because individual 2N3904 units vary widely in β and β falls at cold temperatures, designers rarely bias right at I_{B(min)}. Applying the standard forced-gain rule β_{forced} = 10 gives a robust target of I_{B} ≈ **0.60 mA** (R_{B} ≈ 7.22 kΩ), which matches the 4.7 kΩ to 10 kΩ range tested here.",
    )

    add_heading_3(doc, "What happens if R_{B} is too large or too small?")
    add_body_p(
        doc,
        "**If R_{B} is too large (R_{B} > R_{B(max)}):** Base current drops below I_{B(min)} and the transistor slips out of saturation into the active region. Collector current is no longer set by the load line; it falls proportionally as I_{C} = βI_{B}, causing V_{CE} to climb well above 0.20 V. As Figure 7 illustrates, crossing R_{B(max)} initiates an active-region roll-off where the LED grows dimmer and transistor heat dissipation P_{Q} = V_{CE}I_{C} rises toward the load-line maximum (4.79 mW in Experiment 3, or 13.30 mW in Experiment 1). Across our four lab values (4.7 kΩ to 47 kΩ), Q1 stays inside the guaranteed saturation zone, so theoretical I_{C} stays flat at 5.96 mA. At 47 kΩ, however, the overdrive margin shrinks to ODF_{100} = 1.54 (β_{forced} = 65.12), placing a low-β device in soft saturation where V_{CE} begins creeping upward.",
    )
    add_body_p(
        doc,
        "**If R_{B} is too small (R_{B} ≪ R_{B(max)}):** Base current rises sharply without increasing collector current at all, because I_{C} is already pinned by V_{CC}, V_{LED}, and R_{C}. LED brightness does not improve. Instead, three drawbacks appear: (1) unnecessary current loads down the logic output or signal generator, (2) excess power is wasted as heat across R_{B} and the B-E junction (and removing R_{B} or making it very small can burn out the B-E junction once I_{B} exceeds the 2N3904 current limit), and (3) heavier base overdrive packs extra minority charge into the base region, lengthening storage time t_{s} and slowing turn-off during high-frequency switching.",
    )

    add_heading_2(doc, "5.3 Non-Ideal Deviations and Lab Verification Checklist")
    add_body_p(
        doc,
        "Piecewise-linear hand math keeps equations clean, yet real silicon transistors and SPICE models follow continuous exponential physics (Ebers-Moll). When comparing Table 2 and Table 4 measurements against the Calculation rows, three systematic differences should be expected:",
    )
    add_bullet_p(doc, "**Weak V_{BE} shift in saturation:** Rather than staying frozen at 0.70 V, actual V_{BE} drops by only about 10-15 mV (from roughly 0.73 V down to 0.71 V) across the full decade from R_{B} = 4.7 kΩ to 47 kΩ. The textbook ~60 mV/decade rule applies to forward junction current I_{F} ≈ I_{E}, not to R_{B} or I_{B} while I_{C} is pinned by the collector load; because I_{E} = I_{C} + I_{B} stays dominated by the nearly constant I_{C} ≈ 6.1 mA, V_{BE} barely moves. Instead, the logarithmic variation with I_{B} shifts primarily into the forward-biased base-collector junction (V_{BC} decreases as saturation overdrive drops), pushing V_{CE(sat)} = V_{BE} - V_{BC} upward.")
    add_bullet_p(doc, "**Lower real V_{CE(sat)} and gentle rise with R_{B}:** At 6-10 mA, a real 2N3904 typically saturates between 0.07 V and 0.15 V rather than the conservative 0.20 V textbook bound. Ebers-Moll modeling at β = 100 predicts V_{CE(sat)} rising gradually from about 0.073 V at R_{B} = 4.7 kΩ to 0.153 V at R_{B} = 47 kΩ as overdrive tapers off.")
    add_bullet_p(doc, "**Slightly higher measured I_{C}:** Because actual V_{CE(sat)} is roughly 0.05-0.13 V lower than the textbook 0.20 V assumption, measured collector current typically sits 2-4.5% above hand calculation (around 10.40 mA in Experiment 1 and 6.06-6.23 mA in Experiment 3), superimposed with actual LED color forward voltage and ±5% carbon-film resistor tolerances.")

    add_body_p(doc, "**Practical Lab Verification Checklist (Before Recording Final Readings):**", space_after=3)
    add_bullet_p(doc, "Verify 2N3904 TO-92 orientation (flat face toward you: Emitter left, Base center, Collector right) to prevent inverted-mode low-gain operation.")
    add_bullet_p(doc, "Check the signal generator load mode (High-Z vs. 50 Ω) on the oscilloscope before connecting to the base in Experiment 2.")
    add_bullet_p(doc, "Measure actual resistor values with the DMM and confirm LED anode/cathode polarity before logging Experiment 3.")
    add_bullet_p(doc, "Record the bench LED color and measured V_{LED} in the Section 4.3 log so percentage error calculations reflect the real diode drop.")

    add_heading_2(doc, "5.4 Summary")
    add_body_p(
        doc,
        "The analytical design confirms that a 2N3904 NPN common-emitter stage switches cleanly between cutoff (V_{C} = 5.00 V, I_{C} = 0 mA) and saturation (V_{C} ≈ 0.20 V, I_{C} = 10.21 mA resistive or 5.96 mA with a 2.0 V LED) under a 0-5 V control signal. All four Experiment 3 base resistors (4.7 kΩ, 10 kΩ, 22 kΩ, and 47 kΩ) sit below the worst-case saturation limit of 72.18 kΩ, holding collector current steady while varying overdrive margin from deep saturation (ODF_{100} = 15.36) down to soft saturation (ODF_{100} = 1.54). Once LTspice simulations and bench measurements are entered into Tables 2 through 4 and the Experiment 2 oscilloscope frame, direct percentage-error checks against these predictions will complete the experimental verification.",
    )

    # =========================================================================
    # REFERENCES
    # =========================================================================
    add_heading_1(doc, "References")
    add_numbered_p(doc, "[1]", "A. S. Sedra and K. C. Smith, *Microelectronic Circuits*, 6th ed. New York, NY: Oxford University Press, 2010.")
    add_numbered_p(doc, "[2]", "ON Semiconductor, *2N3904 / MMBT3904 / PZT3904 NPN General-Purpose Amplifier Datasheet*, Rev. 8, 2014.")
    add_numbered_p(doc, "[3]", "School of Electrical Engineering, International University (HCMIU), *EE091IU Electronics Devices Lab: Lab 5 Manual - BJT Biasing in Switching Applications (NPN Transistor)*, 2026.")

    doc.save(str(DOCX_OUT))
    print(f"Saved DOCX: {DOCX_OUT}")


# ---------------------------------------------------------------------------
# Build Companion Markdown Report
# ---------------------------------------------------------------------------
def build_markdown():
    md = """# EE091IU Electronics Devices Lab - Lab 5 Report

**International University - School of Electrical Engineering**  
**Course:** Electronics Devices Lab (`EE091IU`)  
**Title:** LAB 5: BJT Biasing in Switching Applications (NPN Transistor)  
**Submitted by:** Nguyễn Lê Minh Sang (`EEACIU24096`), Nguyễn Gia Huy (`EEACIU24047`)  
**Date Performed:** 21/11/2026 | **Date Submitted:** 21/11/2026  
**Lab Section:** Lab 5 | **Course Instructor:** Lecturer Pham Trung Kien  

---

## Table of Contents

- [List of Figures](#list-of-figures)
- [List of Tables](#list-of-tables)
- [Nomenclature](#nomenclature)
- [1. Objectives](#1-objectives)
- [2. Theoretical Background](#2-theoretical-background)
  - [2.1 NPN BJT Operating Regions and Switching Action](#21-npn-bjt-operating-regions-and-switching-action)
  - [2.2 Governing Equations (Sedra & Smith, 6th Edition)](#22-governing-equations-sedra--smith-6th-edition)
  - [2.3 Step-by-Step Theoretical Calculations](#23-step-by-step-theoretical-calculations)
- [3. Experimental Procedure](#3-experimental-procedure)
  - [3.1 Material and Equipment](#31-material-and-equipment)
  - [3.2 Experiment 1: Static Biasing and Switching](#32-experiment-1-static-biasing-and-switching)
  - [3.3 Experiment 2: Switching Response to Square Wave](#33-experiment-2-switching-response-to-square-wave)
  - [3.4 Experiment 3: Driving an LED](#34-experiment-3-driving-an-led)
- [4. Experimental Results](#4-experimental-results)
  - [4.1 Experiment 1: Static Biasing and Switching](#41-experiment-1-static-biasing-and-switching)
  - [4.2 Experiment 2: Switching Response to Square Wave](#42-experiment-2-switching-response-to-square-wave)
  - [4.3 Experiment 3: Driving an LED](#43-experiment-3-driving-an-led)
- [5. Discussion of Results](#5-discussion-of-results)
  - [5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)](#51-experiment-2-switching-waveform-analysis-lab-question-2c)
  - [5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)](#52-experiment-3-biasing-minimum-base-current-and-base-resistor-tradeoffs-lab-questions-3d)
  - [5.3 Non-Ideal Deviations and Lab Verification Checklist](#53-non-ideal-deviations-and-lab-verification-checklist)
  - [5.4 Summary](#54-summary)
- [References](#references)

---

## List of Figures

1. **Figure 1.** Bipolar junction transistor circuit symbols and TO-92 physical pinouts: (a) 2N3904 NPN and (b) 2N3906 PNP (`figures/fig1_bjt_symbol_pinout.png`).
2. **Figure 2.** NPN BJT switch in saturation: logic HIGH at the base pulls collector output $V_C$ LOW (`figures/fig2_switch_high.png`).
3. **Figure 3.** NPN BJT switch in cutoff: logic LOW at the base leaves collector output $V_C$ HIGH (`figures/fig3_switch_low.png`).
4. **Figure 4.** Experiment 1 circuit schematic for static biasing and switching of Q1 (2N3904) (`figures/fig4_exp1_circuit.png`).
5. **Figure 5.** Experiment 3 circuit schematic for driving a collector-side LED across four $R_B$ values (`figures/fig5_exp3_led_circuit.png`).
6. **Figure 6.** Experiment 2 theoretical waveforms $V_{in}(t)$, $V_B(t)$, and $V_C(t)$ for a 0-5 V, 1 kHz square wave ($D = 50\\%$ assumed) (`figures/fig6_exp2_theoretical_waveforms.png`).
7. **Figure 7.** Experiment 3 analytical sweep of collector current $I_C$, base current $I_B$, overdrive factor (ODF), and forced gain $\\beta_{\\text{forced}}$ versus base resistance $R_B$ (`figures/fig7_exp3_rb_sweep.png`).

## List of Tables

1. **Table 1.** NPN BJT operating regions, junction bias states, and typical applications.
2. **Table 2.** Experiment 1 static biasing and switching results ($V_{CC} = 5\\text{ V}$, $R_C = 470\\ \\Omega$, $R_B = 10\\text{ k}\\Omega$).
3. **Table 3.** Experiment 2 theoretical waveform levels and 2N3904 switching timing summary (1 kHz, $D = 50\\%$ assumed).
4. **Table 4.** Experiment 3 LED driver results across four base resistors ($V_{CC} = 5\\text{ V}$, $R_C = 470\\ \\Omega$, $V_{LED} = 2.0\\text{ V}$ assumed, $V_{in} = 5\\text{ V}$).

## Nomenclature

| Symbol | Definition |
|---|---|
| $V_{CC}$ | DC collector supply voltage ($5.0\\text{ V}$ in all three experiments) |
| $V_{in}$ | Input control voltage applied ahead of $R_B$ ($0\\text{ V}$ LOW or $5.0\\text{ V}$ HIGH) |
| $V_B, V_C, V_E$ | Node voltages at base, collector, and emitter relative to ground ($V_E = 0\\text{ V}$) |
| $V_{BE}, V_{BE(\\text{on})}$ | Base-emitter voltage and forward-conduction drop ($0.70\\text{ V}$) |
| $V_{CE}, V_{CE(\\text{sat})}$ | Collector-emitter voltage and saturation drop ($0.20\\text{ V}$ textbook model) |
| $V_{LED}$ | Forward voltage drop of collector-side LED ($2.0\\text{ V}$ assumed nominal; $1.8\\text{ V}$ sensitivity check) |
| $I_B, I_C$ | DC base current and collector current |
| $I_{C(\\text{sat})}$ | Saturation collector current fixed by the external supply and load branch |
| $I_{B(\\min)}, R_{B(\\max)}$ | Minimum base current and maximum base resistance at the edge of saturation |
| $R_B, R_C$ | Base current-limiting resistor and collector load resistor ($R_C = 470\\ \\Omega$) |
| $\\beta\\ (h_{FE})$ | DC common-emitter current gain of the 2N3904 ($\\beta_{\\min} = 100$ at $10\\text{ mA}$, $\\beta_{\\text{typ}} = 300$) |
| $\\beta_{\\text{forced}}$ | Forced current gain in saturation, $I_{C(\\text{sat})} / I_B$ |
| $ODF$ | Overdrive factor, $I_B / I_{B(\\min)} = \\beta / \\beta_{\\text{forced}}$ |
| $P_Q, P_{RC}, P_{RB}$ | Steady-state power dissipated by Q1, $R_C$, and $R_B$ |
| $t_d, t_r, t_s, t_f$ | Delay, rise, storage, and fall times of the switching transistor |

---

## 1. Objectives

Lab 5 investigates how an NPN bipolar junction transistor (2N3904) behaves when biased strictly as an electronic switch. Instead of amplifying small analog signals, the transistor swings between full cutoff and full saturation under static DC levels, a 1 kHz square wave, and a collector-side LED load.

- Observe the ON/OFF switching behavior of a 2N3904 NPN BJT driven by digital logic voltage levels ($0\\text{ V}$ and $5\\text{ V}$).
- Calculate and verify the biasing conditions required to place the transistor reliably in cutoff and saturation.
- Design, analyze, and test a basic transistor switching stage driving both a purely resistive load ($470\\ \\Omega$) and a series LED load across four base resistor values.

---

## 2. Theoretical Background

### 2.1 NPN BJT Operating Regions and Switching Action

A bipolar junction transistor contains two p-n junctions: base-emitter (B-E) and base-collector (B-C). How those two junctions are biased determines which of three operating regions the device occupies. Figure 1 shows the circuit symbols and TO-92 physical pinouts for the 2N3904 NPN transistor alongside its PNP complement (2N3906).

![Figure 1: BJT symbol and pinout](figures/fig1_bjt_symbol_pinout.png)

**Table 1.** NPN BJT operating regions, junction bias states, and typical applications.

| Region | B-E Junction | B-C Junction | Terminal Condition | Primary Use |
|---|---|---|---|---|
| **Cutoff** | Reverse biased | Reverse biased | $V_{BE} < 0.70\\text{ V}$, $I_B \\approx 0$, $I_C \\approx 0$, $V_{CE} \\approx V_{CC}$ | Open switch (OFF) |
| **Active** | Forward biased | Reverse biased | $V_{BE} \\approx 0.70\\text{ V}$, $I_C = \\beta I_B$, $V_{CE} > V_{CE(\\text{sat})}$ | Linear amplification |
| **Saturation** | Forward biased | Forward biased | $V_{BE} \\approx 0.70\\text{ V}$, $V_{CE} \\approx 0.20\\text{ V}$, $I_C < \\beta I_B$ | Closed switch (ON) |

Switching circuits deliberately skip the active region except during brief transitions. When logic HIGH ($5.0\\text{ V}$) reaches the base through $R_B$, sufficient base current flows to forward-bias both junctions and drive Q1 into saturation. Collector-emitter voltage drops to $V_{CE(\\text{sat})} \\approx 0.20\\text{ V}$, pulling output $V_C$ LOW (Figure 2).

![Figure 2: Switch HIGH (Saturation)](figures/fig2_switch_high.png)

When the base input falls to logic LOW ($0\\text{ V}$), $V_{BE}$ drops below the turn-on threshold. Base and collector currents vanish, zero voltage drops across $R_C$, and Q1 acts as an open switch so $V_C$ stays HIGH at $V_{CC} = 5.0\\text{ V}$ (Figure 3). Because HIGH in produces LOW out and LOW in produces HIGH out, this common-emitter stage operates as a digital inverter.

![Figure 3: Switch LOW (Cutoff)](figures/fig3_switch_low.png)

### 2.2 Governing Equations (Sedra & Smith, 6th Edition)

All hand calculations follow the piecewise-linear DC BJT model from Adel S. Sedra and Kenneth C. Smith, *Microelectronic Circuits* (6th ed., Chapter 6). For the grounded-emitter 2N3904 ($V_E = 0\\text{ V}$), $V_B = V_{BE}$ and $V_C = V_{CE}$. Baseline parameters are $V_{CC} = 5.0\\text{ V}$, $R_C = 470\\ \\Omega$, $V_{BE(\\text{on})} = 0.70\\text{ V}$, $V_{CE(\\text{sat})} = 0.20\\text{ V}$, datasheet minimum gain $\\beta_{\\min} = 100$ at $I_C = 10\\text{ mA}$, and typical gain $\\beta_{\\text{typ}} = 300$.

$$I_B = \\frac{V_{in} - V_{BE(\\text{on})}}{R_B} \\tag{1}$$

$$I_{C(\\text{sat})} = \\frac{V_{CC} - V_{CE(\\text{sat})}}{R_C} \\quad [\\text{Experiment 1: resistive load}] \\tag{2}$$

$$I_{C(\\text{sat})} = \\frac{V_{CC} - V_{LED} - V_{CE(\\text{sat})}}{R_C} \\quad [\\text{Experiment 3: LED + resistor load}] \\tag{3}$$

$$\\beta_{\\text{forced}} = \\frac{I_{C(\\text{sat})}}{I_B} < \\beta \\tag{4}$$

$$I_{B(\\min)} = \\frac{I_{C(\\text{sat})}}{\\beta}, \\qquad R_{B(\\max)} = \\frac{V_{in} - V_{BE(\\text{on})}}{I_{B(\\min)}} \\tag{5}$$

$$ODF = \\frac{I_B}{I_{B(\\min)}} = \\frac{\\beta}{\\beta_{\\text{forced}}} \\tag{6}$$

$$P_Q = V_{CE} I_C + V_{BE} I_B, \\qquad P_{RC} = I_C^2 R_C, \\qquad P_{RB} = I_B^2 R_B \\tag{7}$$

Worst-case active-region collector dissipation on the DC load line is $P_{C,\\max} = V_{CC}^2 / (4 R_C)$ (Experiment 1) or $(V_{CC} - V_{LED})^2 / (4 R_C)$ (Experiment 3).

### 2.3 Step-by-Step Theoretical Calculations

#### Experiment 1: Static Biasing and Switching ($R_B = 10\\text{ k}\\Omega$)

- **State 1 ($V_{in} = 0\\text{ V}$, Cutoff):** $V_{BE} = V_B = 0.00\\text{ V} < 0.70\\text{ V}$, $I_B = 0.000\\text{ mA}$, $I_C = 0.00\\text{ mA}$, $V_{CE} = V_C = 5.00\\text{ V}$, $P_Q = P_{RC} = P_{RB} = 0.00\\text{ mW}$.
- **State 2 ($V_{in} = 5.0\\text{ V}$, Saturation):**
  - $I_B = (5.0 - 0.70) / 10\\text{ k}\\Omega = \\mathbf{0.430\\text{ mA}}$ ($430.0\\ \\mu\\text{A}$).
  - $I_{C(\\text{sat})} = (5.0 - 0.20) / 470\\ \\Omega = \\mathbf{10.2128\\text{ mA} \\approx 10.21\\text{ mA}}$.
  - $V_B = V_{BE} = \\mathbf{0.70\\text{ V}}$; $V_C = V_{CE} = \\mathbf{0.20\\text{ V}}$.
  - Saturation check: $\\beta_{\\text{forced}} = 10.2128 / 0.430 = \\mathbf{23.75} < \\beta_{\\min} = 100$.
  - Boundaries: At $\\beta_{\\min} = 100$, $I_{B(\\min)} = \\mathbf{102.13\\ \\mu\\text{A}}$, $R_{B(\\max)} = \\mathbf{42.10\\text{ k}\\Omega}$, $ODF_{100} = \\mathbf{4.21}$. At $\\beta_{\\text{typ}} = 300$, $I_{B(\\min)} = \\mathbf{34.04\\ \\mu\\text{A}}$, $R_{B(\\max)} = \\mathbf{126.31\\text{ k}\\Omega}$, $ODF_{300} = \\mathbf{12.63}$.
  - Power check: $P_Q = 2.34\\text{ mW} \\ll 625\\text{ mW}$, $P_{RC} = 49.02\\text{ mW}$, $P_{RB} = 1.85\\text{ mW}$. Active-region collector peak $P_{C,\\max} = 13.30\\text{ mW}$.

#### Experiment 2: Switching Response to a 1 kHz Square Wave

- Input: $0\\text{-}5\\text{ V}$ square wave at $f = 1\\text{ kHz}$ with assumed duty cycle $D = 50\\%$, giving $T = 1.00\\text{ ms}$ and $T_{\\text{HIGH}} = T_{\\text{LOW}} = 0.50\\text{ ms} = 500\\ \\mu\\text{s}$.
- $V_B(t)$: clamped between $0.00\\text{ V}$ and $0.70\\text{ V}$, in phase ($0^\\circ$) with $V_{in}(t)$.
- $V_C(t)$: inverted ($180^\\circ$ phase shift) between $5.00\\text{ V}$ (cutoff) and $0.20\\text{ V}$ (saturation).
- Datasheet 2N3904 switching times: $t_d \\le 35\\text{ ns}$, $t_r \\le 35\\text{ ns}$ ($t_{\\text{on}} \\le 70\\text{ ns}$), $t_s \\le 200\\text{ ns}$, $t_f \\le 50\\text{ ns}$ ($t_{\\text{off}} \\le 250\\text{ ns}$). Ratio $(t_{\\text{on}} + t_{\\text{off}})/(T/2) \\le 0.064\\%$. Even with passive turn-off storage delay ($t_s \\approx 0.5\\text{-}2\\ \\mu\\text{s}$), total delay stays below $0.5\\%$ of $T/2$.

#### Experiment 3: Driving a Collector-Side LED across Four Base Resistors

- Assumed LED forward drop: $V_{LED} = 2.0\\text{ V}$ (nominal).
- $I_{C(\\text{sat})} = (5.0 - 2.0 - 0.20) / 470 = \\mathbf{5.9574\\text{ mA} \\approx 5.96\\text{ mA}}$.
- Collector-branch power: $P_{RC} = 16.68\\text{ mW}$, $P_{LED} = 11.91\\text{ mW}$, active-region peak $P_{C,\\max} = 4.79\\text{ mW}$.
- Saturation limits: $\\beta_{\\min} = 100 \\Rightarrow I_{B(\\min)} = 59.57\\ \\mu\\text{A},\\ R_{B(\\max)} = 72.18\\text{ k}\\Omega$; $\\beta_{\\text{typ}} = 300 \\Rightarrow I_{B(\\min)} = 19.86\\ \\mu\\text{A},\\ R_{B(\\max)} = 216.54\\text{ k}\\Omega$. Rule-of-thumb $\\beta_{\\text{forced}} = 10 \\Rightarrow I_B \\approx 0.60\\text{ mA},\\ R_B \\approx 7.22\\text{ k}\\Omega$.
- Sensitivity ($V_{LED} = 1.8\\text{ V}$): $I_{C(\\text{sat})} = 6.38\\text{ mA}$ ($+7.14\\%$), $I_{B(\\min,100)} = 63.83\\ \\mu\\text{A}$, $R_{B(\\max,100)} = 67.37\\text{ k}\\Omega$ (all four lab resistors still saturate).
- Per-resistor summary at $V_{in} = 5.0\\text{ V}$ ($V_{BE} = 0.70\\text{ V}$, $V_{CE} = 0.20\\text{ V}$, $I_C = 5.96\\text{ mA}$):
  - $R_B = 4.7\\text{ k}\\Omega$: $I_B = 0.915\\text{ mA}$, $\\beta_{\\text{forced}} = 6.51$, $ODF_{100} = 15.36$, $ODF_{300} = 46.07$, $P_Q = 1.83\\text{ mW}$, $P_{RB} = 3.93\\text{ mW}$ (Deep Saturation).
  - $R_B = 10\\text{ k}\\Omega$: $I_B = 0.430\\text{ mA}$, $\\beta_{\\text{forced}} = 13.85$, $ODF_{100} = 7.22$, $ODF_{300} = 21.65$, $P_Q = 1.49\\text{ mW}$, $P_{RB} = 1.85\\text{ mW}$ (Saturation).
  - $R_B = 22\\text{ k}\\Omega$: $I_B = 0.195\\text{ mA}$, $\\beta_{\\text{forced}} = 30.48$, $ODF_{100} = 3.28$, $ODF_{300} = 9.84$, $P_Q = 1.33\\text{ mW}$, $P_{RB} = 0.84\\text{ mW}$ (Saturation).
  - $R_B = 47\\text{ k}\\Omega$: $I_B = 0.0915\\text{ mA}$, $\\beta_{\\text{forced}} = 65.12$, $ODF_{100} = 1.54$, $ODF_{300} = 4.61$, $P_Q = 1.26\\text{ mW}$, $P_{RB} = 0.39\\text{ mW}$ (Soft Saturation).

---

## 3. Experimental Procedure

### 3.1 Material and Equipment

1. Dual-channel Digital Storage Oscilloscope (with 10x probes)
2. DC Power Supply ($V_{CC} = 5.0\\text{ V}$, current limit ~100 mA)
3. Function / Signal Generator (0-5 V, 1 kHz square wave)
4. Solderless breadboard and jumper wires
5. Digital Multimeter (DMM)
6. NPN Transistor 2N3904 (TO-92 pinout: E-B-C from left to right with flat face forward)
7. Resistors ($470\\ \\Omega$, $4.7\\text{ k}\\Omega$, $10\\text{ k}\\Omega$, $22\\text{ k}\\Omega$, $47\\text{ k}\\Omega$) and a standard indicator LED

### 3.2 Experiment 1: Static Biasing and Switching

![Figure 4: Experiment 1 Circuit](figures/fig4_exp1_circuit.png)

1. Assemble Figure 4 with $V_{CC} = 5.0\\text{ V}$, $R_C = 470\\ \\Omega$, $R_B = 10\\text{ k}\\Omega$, and Q1 = 2N3904.
2. Connect $V_{in}$ to $0\\text{ V}$, then measure $V_{BE}$, $V_{CE}$, $V_C$, $V_B$, $I_B$, and $I_C$.
3. Move $V_{in}$ to $+5.0\\text{ V}$, repeat all six measurements, and record simulation and bench values in Table 2.

### 3.3 Experiment 2: Switching Response to Square Wave

1. Keep the Experiment 1 circuit intact.
2. Set the signal generator to a $0\\text{-}5\\text{ V}$, $1\\text{ kHz}$ square wave ($D = 50\\%$), verifying the High-Z vs. $50\\ \\Omega$ load setting on the oscilloscope first.
3. Connect the generator to $V_{in}$ and tie grounds together.
4. Probe $V_B$ (CH1) and $V_C$ (CH2) using DC coupling, align 0 V baselines, and capture oscilloscope screenshots.

### 3.4 Experiment 3: Driving an LED

![Figure 5: Experiment 3 LED Circuit](figures/fig5_exp3_led_circuit.png)

1. Insert the LED (anode toward $R_C$, cathode toward Q1 collector) in series with $R_C = 470\\ \\Omega$ as in Figure 5.
2. With $R_B = 10\\text{ k}\\Omega$, toggle $V_{in}$ between $0\\text{ V}$ and $5\\text{ V}$ and verify LED OFF/ON switching.
3. Hold $V_{in} = 5\\text{ V}$ and measure $V_{BE}$, $V_{CE}$, $I_B$, and $I_C$ for $R_B = 4.7\\text{ k}\\Omega$, $10\\text{ k}\\Omega$, $22\\text{ k}\\Omega$, and $47\\text{ k}\\Omega$. Record results in Table 4.

---

## 4. Experimental Results

All **Calculation** rows below contain verified theoretical predictions. All **Simulation** and **Measurement** rows, the Experiment 2 oscilloscope capture area, and the Experiment 3 bench observation log are left blank for completion during lab execution.

### 4.1 Experiment 1: Static Biasing and Switching

**Table 2.** Experiment 1 static biasing and switching results ($V_{CC} = 5\\text{ V}$, $R_C = 470\\ \\Omega$, $R_B = 10\\text{ k}\\Omega$).

| $V_{in}$ | Mode | $V_{BE}$ (V) | $V_{CE}$ (V) | $V_C$ (V) | $V_B$ (V) | $I_B$ (mA) | $I_C$ (mA) |
|---|---|---|---|---|---|---|---|
| 0 V | **Calculation** | 0.00 | 5.00 | 5.00 | 0.00 | 0.000 | 0.00 |
| 0 V | Simulation | | | | | | |
| 0 V | Measurement | | | | | | |
| 5 V | **Calculation** | 0.70 | 0.20 | 0.20 | 0.70 | 0.430 | 10.21 |
| 5 V | Simulation | | | | | | |
| 5 V | Measurement | | | | | | |

### 4.2 Experiment 2: Switching Response to Square Wave

**Table 3.** Experiment 2 theoretical waveform levels and 2N3904 switching timing summary (1 kHz, $D = 50\\%$ assumed).

| Parameter | Theoretical Prediction | Measured / Observed (Lab) |
|---|---|---|
| Input $V_{in}(t)$ levels & period | 0.00 V to 5.00 V; $T = 1.00\\text{ ms}$ ($T/2 = 0.50\\text{ ms}$) | |
| Base voltage $V_B(t)$ levels | 0.00 V (OFF) to 0.70 V (clamped ON) | |
| Base phase relative to $V_{in}(t)$ | $0^\\circ$ (in phase) | |
| Collector voltage $V_C(t)$ levels | 5.00 V (cutoff) to 0.20 V (saturation) | |
| Collector phase relative to $V_{in}(t)$ | $180^\\circ$ (logic inversion) | |
| 2N3904 switching times (datasheet) | $t_{\\text{on}} \\le 70\\text{ ns}$, $t_{\\text{off}} \\le 250\\text{ ns}$ ($\\le 0.064\\%$ of $T/2$) | |

![Figure 6: Experiment 2 Theoretical Waveforms](figures/fig6_exp2_theoretical_waveforms.png)

> **[Oscilloscope Capture Area - Experiment 2]**  
> *Paste measured CH1 ($V_B$) and CH2 ($V_C$) oscilloscope screenshots here during the lab session.*

### 4.3 Experiment 3: Driving an LED

**Table 4.** Experiment 3 LED driver results across four base resistors ($V_{CC} = 5\\text{ V}$, $R_C = 470\\ \\Omega$, $V_{LED} = 2.0\\text{ V}$ assumed, $V_{in} = 5\\text{ V}$).

| $R_B$ | Mode | $V_{BE}$ (V) | $V_{CE}$ (V) | $I_B$ (mA) | $I_C$ (mA) |
|---|---|---|---|---|---|
| 4.7 kΩ | **Calculation** | 0.70 | 0.20 | 0.915 | 5.96 |
| 4.7 kΩ | Simulation | | | | |
| 4.7 kΩ | Measurement | | | | |
| 10 kΩ | **Calculation** | 0.70 | 0.20 | 0.430 | 5.96 |
| 10 kΩ | Simulation | | | | |
| 10 kΩ | Measurement | | | | |
| 22 kΩ | **Calculation** | 0.70 | 0.20 | 0.195 | 5.96 |
| 22 kΩ | Simulation | | | | |
| 22 kΩ | Measurement | | | | |
| 47 kΩ | **Calculation** | 0.70 | 0.20 | 0.0915 | 5.96 |
| 47 kΩ | Simulation | | | | |
| 47 kΩ | Measurement | | | | |

**Bench Observation Log (Experiment 3 - Fill In During Lab):**

| Observation Item | Recorded Bench Value / Notes |
|---|---|
| LED color and measured forward drop $V_{LED}$ (V) | |
| LED ON/OFF behavior at $V_{in} = 0\\text{ V}$ vs. $5\\text{ V}$ ($R_B = 10\\text{ k}\\Omega$) | |
| Measured DC current gain $h_{FE}$ ($\\beta$) of bench 2N3904 | |
| Visual LED brightness trend from $R_B = 4.7\\text{ k}\\Omega$ to $47\\text{ k}\\Omega$ | |

![Figure 7: Experiment 3 Base Resistor Sweep](figures/fig7_exp3_rb_sweep.png)

---

## 5. Discussion of Results

### 5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)

Driving the 2N3904 base with a 0-5 V, 1 kHz square wave exposes two clear features on the oscilloscope. First, collector voltage $V_C(t)$ is a $180^\\circ$ inverted copy of $V_{in}(t)$. When the input jumps to $5.0\\text{ V}$, base current rises to $0.430\\text{ mA}$, Q1 saturates, and $V_C$ drops to roughly $0.20\\text{ V}$. When the input returns to $0\\text{ V}$, Q1 cuts off and $R_C$ pulls $V_C$ back up to $5.00\\text{ V}$. The stage functions directly as a single-transistor digital NOT gate.

Second, base voltage $V_B(t)$ never climbs to $5.0\\text{ V}$. Instead, it tracks $V_{in}(t)$ in phase ($0^\\circ$ shift) while remaining clamped between $0.00\\text{ V}$ and roughly $0.70\\text{ V}$. Why? Because the forward-biased base-emitter junction behaves like a silicon diode connected straight to ground. Its exponential I-V curve locks $V_B$ near $0.70\\text{ V}$, forcing the $10\\text{ k}\\Omega$ base resistor to absorb the remaining $4.30\\text{ V}$.

At 1 kHz, the half-period is $500\\ \\mu\\text{s}$. Against that window, the 2N3904's datasheet turn-on time ($t_{\\text{on}} \\le 70\\text{ ns}$) and turn-off time ($t_{\\text{off}} \\le 250\\text{ ns}$) occupy at most $0.064\\%$ of one pulse. Transitions therefore appear sharp and vertical on a standard timebase. On an actual breadboard without a negative turn-off bias, excess minority carriers stored in the base during saturation must discharge passively through $R_B = 10\\text{ k}\\Omega$. That passive discharge stretches storage time $t_s$ to roughly $0.5\\text{-}2\\ \\mu\\text{s}$, which is still tiny at 1 kHz ($< 0.5\\%$ of $T/2$) but would visibly distort the collector turn-off edge if frequency were pushed into the hundreds of kilohertz.

### 5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)

**When is the transistor in cutoff or saturation?**  
An NPN transistor enters **cutoff** when both the B-E and B-C junctions are reverse-biased (or zero-biased). Practically, that occurs whenever $V_{BE}$ falls below the turn-on threshold (~0.5-0.7 V), cutting off base current ($I_B \\approx 0$) and collector current ($I_C \\approx 0$). In Experiment 1, the collector node voltage rises to $V_{CC}$ ($5.00\\text{ V}$); in Experiment 3, the LED enters its non-conducting off state with zero collector current.

The transistor enters **saturation** when both the B-E and B-C junctions are forward-biased. Two linked conditions confirm saturation: the base current exceeds $I_{B(\\min)} = I_{C(\\text{sat})} / \\beta$ (equivalently, $\\beta_{\\text{forced}} = I_{C(\\text{sat})} / I_B < \\beta$), and $V_{CE}$ collapses to $V_{CE(\\text{sat})} \\approx 0.20\\text{ V}$ (often $0.07\\text{-}0.15\\text{ V}$ on a real 2N3904 at 6-10 mA). Once saturated, $I_C$ stops tracking $\\beta I_B$ and is instead fixed by the supply voltage and collector load.

**What is the minimum base current required to drive the transistor into saturation?**  
In **Experiment 1** ($I_{C(\\text{sat})} = 10.21\\text{ mA}$), reaching the edge of saturation requires $I_{B(\\min)} = \\mathbf{102.13\\ \\mu\\text{A}}$ at worst-case $\\beta_{\\min} = 100$ ($R_{B(\\max)} = 42.10\\text{ k}\\Omega$), or $\\mathbf{34.04\\ \\mu\\text{A}}$ at typical $\\beta_{\\text{typ}} = 300$ ($R_{B(\\max)} = 126.31\\text{ k}\\Omega$).

In **Experiment 3** ($I_{C(\\text{sat})} = 5.96\\text{ mA}$ at $V_{LED} = 2.0\\text{ V}$), the minimum base current drops to $\\mathbf{59.57\\ \\mu\\text{A}}$ at $\\beta_{\\min} = 100$ ($R_{B(\\max)} = 72.18\\text{ k}\\Omega$) and $\\mathbf{19.86\\ \\mu\\text{A}}$ at $\\beta_{\\text{typ}} = 300$ ($R_{B(\\max)} = 216.54\\text{ k}\\Omega$). If a red LED with $V_{LED} = 1.8\\text{ V}$ is used, $I_{C(\\text{sat})}$ rises to $6.38\\text{ mA}$ and $I_{B(\\min,100)}$ shifts to $\\mathbf{63.83\\ \\mu\\text{A}}$ ($R_{B(\\max,100)} = 67.37\\text{ k}\\Omega$). Using the standard forced-gain rule $\\beta_{\\text{forced}} = 10$ gives a practical target of $I_B \\approx \\mathbf{0.60\\text{ mA}}$ ($R_B \\approx 7.22\\text{ k}\\Omega$).

**What happens if $R_B$ is too large or too small?**  
- **If $R_B$ is too large ($R_B > R_{B(\\max)}$):** Base current drops below $I_{B(\\min)}$ and the transistor slips out of saturation into the active region. Collector current falls as $I_C = \\beta I_B$, $V_{CE}$ climbs above $0.20\\text{ V}$, the LED dims, and transistor dissipation $P_Q = V_{CE} I_C$ rises toward the load-line peak ($4.79\\text{ mW}$ in Experiment 3, $13.30\\text{ mW}$ in Experiment 1). Across our four lab resistors ($4.7\\text{ k}\\Omega$ to $47\\text{ k}\\Omega$), Q1 stays saturated, though $47\\text{ k}\\Omega$ sits in soft saturation ($ODF_{100} = 1.54$, $\\beta_{\\text{forced}} = 65.12$).
- **If $R_B$ is too small ($R_B \\ll R_{B(\\max)}$):** Base current rises sharply without making the LED any brighter because $I_C$ is already capped at $I_{C(\\text{sat})}$. Instead, the input source is loaded down, excess power is wasted as heat across $R_B$ and the B-E junction (risking damage if $I_B$ exceeds device limits), and excess minority charge stored in the base lengthens storage time $t_s$, slowing turn-off at higher switching frequencies.

### 5.3 Non-Ideal Deviations and Lab Verification Checklist

Piecewise-linear hand math keeps equations clean, yet real silicon transistors and SPICE models follow continuous exponential physics (Ebers-Moll). Three systematic differences should be expected when comparing simulation and measurement against the Calculation rows:

- **Weak $V_{BE}$ shift in saturation:** Rather than staying frozen at $0.70\\text{ V}$, actual $V_{BE}$ drops by only about $10\\text{-}15\\text{ mV}$ (from roughly $0.73\\text{ V}$ down to $0.71\\text{ V}$) across the full decade from $R_B = 4.7\\text{ k}\\Omega$ to $47\\text{ k}\\Omega$. The textbook $\\approx 60\\text{ mV/decade}$ rule applies to forward junction current $I_F \\approx I_E$, not to $R_B$ or $I_B$ while $I_C$ is pinned by the collector load; because $I_E = I_C + I_B$ stays dominated by the nearly constant $I_C \\approx 6.1\\text{ mA}$, $V_{BE}$ barely moves. Instead, the logarithmic variation with $I_B$ shifts primarily into the forward-biased base-collector junction ($V_{BC}$ decreases as saturation overdrive drops), pushing $V_{CE(\\text{sat})} = V_{BE} - V_{BC}$ upward.
- **Lower real $V_{CE(\\text{sat})}$ and gentle rise with $R_B$:** Real 2N3904 saturation voltage at 6-10 mA typically measures $0.07\\text{-}0.15\\text{ V}$ rather than the conservative $0.20\\text{ V}$ textbook bound. Ebers-Moll modeling at $\\beta = 100$ predicts $V_{CE(\\text{sat})}$ rising from $0.073\\text{ V}$ at $4.7\\text{ k}\\Omega$ to $0.153\\text{ V}$ at $47\\text{ k}\\Omega$ as overdrive tapers off.
- **Slightly higher measured $I_C$:** Because actual $V_{CE(\\text{sat})}$ is smaller than $0.20\\text{ V}$, real collector current tends to sit $2\\text{-}4.5\\%$ above hand calculation (around $10.40\\text{ mA}$ in Experiment 1 and $6.06\\text{-}6.23\\text{ mA}$ in Experiment 3), plus any offset from actual LED forward voltage and $\\pm 5\\%$ resistor tolerances.

**Practical Lab Verification Checklist:**

- Confirm 2N3904 TO-92 orientation (flat face forward: E-B-C left to right).
- Check signal generator load mode (High-Z vs. $50\\ \\Omega$) before applying the 1 kHz square wave in Experiment 2.
- Measure actual resistor values and verify LED polarity before logging Experiment 3.
- Record the bench LED color and measured $V_{LED}$ in Section 4.3 before computing percentage error.

### 5.4 Summary

The analytical design confirms that a 2N3904 NPN common-emitter stage switches cleanly between cutoff ($V_C = 5.00\\text{ V}$, $I_C = 0\\text{ mA}$) and saturation ($V_C \\approx 0.20\\text{ V}$, $I_C = 10.21\\text{ mA}$ resistive or $5.96\\text{ mA}$ with a $2.0\\text{ V}$ LED) under a $0\\text{-}5\\text{ V}$ control signal. All four Experiment 3 base resistors ($4.7\\text{ k}\\Omega$, $10\\text{ k}\\Omega$, $22\\text{ k}\\Omega$, and $47\\text{ k}\\Omega$) sit below the worst-case saturation limit of $72.18\\text{ k}\\Omega$, holding collector current steady while varying overdrive margin from deep saturation ($ODF_{100} = 15.36$) down to soft saturation ($ODF_{100} = 1.54$). Once LTspice simulations and bench measurements are entered into Tables 2 through 4 and the Experiment 2 oscilloscope frame, direct percentage-error checks against these predictions will complete the experimental verification.

---

## References

1. A. S. Sedra and K. C. Smith, *Microelectronic Circuits*, 6th ed. New York, NY: Oxford University Press, 2010.
2. ON Semiconductor, *2N3904 / MMBT3904 / PZT3904 NPN General-Purpose Amplifier Datasheet*, Rev. 8, 2014.
3. School of Electrical Engineering, International University (HCMIU), *EE091IU Electronics Devices Lab: Lab 5 Manual - BJT Biasing in Switching Applications (NPN Transistor)*, 2026.
"""
    MD_OUT.write_text(md, encoding="utf-8")
    print(f"Saved MD:   {MD_OUT}")


# ---------------------------------------------------------------------------
# Automated Self-Verification Suite
# ---------------------------------------------------------------------------
def verify_outputs():
    print("\n" + "=" * 72)
    print("AUTOMATED VERIFICATION SUITE")
    print("=" * 72)

    # 1. Inspect DOCX XML + python-docx text
    doc = docx.Document(str(DOCX_OUT))
    docx_texts = []
    for p in doc.paragraphs:
        docx_texts.append(p.text)
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                docx_texts.append(c.text)
    for s in doc.sections:
        for ftr in (s.footer, s.header):
            for p in ftr.paragraphs:
                docx_texts.append(p.text)
    full_docx_text = "\n".join(docx_texts)
    full_md_text = MD_OUT.read_text(encoding="utf-8")

    # Also check raw XML inside the DOCX zip for footer/header/body remnants
    xml_all = []
    media_files = []
    with zipfile.ZipFile(str(DOCX_OUT)) as z:
        for name in z.namelist():
            if name.startswith("word/media/"):
                media_files.append(name)
            if name.endswith(".xml"):
                xml_all.append(z.read(name).decode("utf-8", errors="ignore"))
    full_xml_text = "\n".join(xml_all)

    # Check A: Zero em dash (U+2014) anywhere
    assert "\u2014" not in full_docx_text, "Em dash found in DOCX text!"
    assert "\u2014" not in full_xml_text, "Em dash found in DOCX XML!"
    assert "\u2014" not in full_md_text, "Em dash found in MD text!"
    print("[PASS] 0 em dashes (U+2014) in DOCX text, DOCX XML, and MD.")

    # Check B: Zero leftover template artifacts
    forbidden_template = [
        "Operational Amplifiers",
        "Lab 2",
        "[Course number]",
        "Vref",
        "Iref",
        "Vos = Vo",
        "Figure X",
        "meanning",
        "What happen ",
        "COURSE’S",
    ]
    for bad in forbidden_template:
        assert bad not in full_docx_text, f"Leftover template string in DOCX: {bad!r}"
        assert bad not in full_xml_text, f"Leftover template string in DOCX XML: {bad!r}"
        assert bad not in full_md_text, f"Leftover template string in MD: {bad!r}"
    print("[PASS] 0 leftover template strings in DOCX/XML/MD.")

    # Check C: Zero raw LaTeX / raw markdown markers in DOCX
    for bad_docx in ("\\frac", "\\text", "$", "**", "##", "_{", "^{"):
        assert bad_docx not in full_docx_text, f"Raw markup/LaTeX leaked into DOCX: {bad_docx!r}"
    print("[PASS] 0 raw LaTeX or Markdown tokens in DOCX.")

    # Check D: Humanizer AI blacklist check
    ai_blacklist = [
        "delve", "tapestry", "testament", "beacon", "landscape",
        "pivotal", "profound", "foster", "in conclusion", "not only",
        "but also", "crucial", "dynamic", "realm", "harness",
    ]
    for word in ai_blacklist:
        pat = r"\b" + re.escape(word) + r"\b"
        assert not re.search(pat, full_docx_text, flags=re.IGNORECASE), f"AI cliché in DOCX: {word!r}"
        assert not re.search(pat, full_md_text, flags=re.IGNORECASE), f"AI cliché in MD: {word!r}"
    print("[PASS] 0 Humanizer AI-blacklist words in DOCX and MD.")

    # Check E: Embedded figures count (must have all 7 PNG figures)
    png_media = [m for m in media_files if m.lower().endswith(".png")]
    assert len(png_media) == 7, f"Expected 7 embedded PNG figures, found {len(png_media)}: {png_media}"
    print(f"[PASS] All 7 PNG figures embedded in DOCX ({len(png_media)} PNGs).")

    # Check F: Verify Experiment 1 (Table 2) & Experiment 3 (Table 4) blank Simulation/Measurement rows and exact Calculation values
    # Locate Table 2 (8 cols, header starts with 'Vin') and Table 4 (6 cols, header starts with 'RB')
    exp1_tbl = None
    exp3_tbl = None
    exp2_tbl = None
    log_tbl = None
    for tbl in doc.tables:
        if len(tbl.columns) == 8 and tbl.rows[0].cells[1].text.strip() == "Mode":
            exp1_tbl = tbl
        elif len(tbl.columns) == 6 and tbl.rows[0].cells[1].text.strip() == "Mode":
            exp3_tbl = tbl
        elif len(tbl.columns) == 3 and "Measured / Observed" in tbl.rows[0].cells[2].text:
            exp2_tbl = tbl
        elif len(tbl.columns) == 2 and "Recorded Bench Value" in tbl.rows[0].cells[1].text:
            log_tbl = tbl

    assert exp1_tbl is not None, "Experiment 1 table not found!"
    assert exp2_tbl is not None, "Experiment 2 summary table not found!"
    assert exp3_tbl is not None, "Experiment 3 table not found!"
    assert log_tbl is not None, "Experiment 3 bench log table not found!"

    # Verify Exp 1 merged V_in labels, Calculation values, and blank Sim/Meas
    assert exp1_tbl.cell(1, 0).text.strip() == "0 V", f"Exp 1 merged V_in 0V mismatch: {exp1_tbl.cell(1, 0).text!r}"
    assert exp1_tbl.cell(4, 0).text.strip() == "5 V", f"Exp 1 merged V_in 5V mismatch: {exp1_tbl.cell(4, 0).text!r}"
    exp1_calc_0 = [c.text.strip() for c in exp1_tbl.rows[1].cells[2:]]
    exp1_calc_5 = [c.text.strip() for c in exp1_tbl.rows[4].cells[2:]]
    assert exp1_calc_0 == ["0.00", "5.00", "5.00", "0.00", "0.000", "0.00"], f"Exp 1 0V calc mismatch: {exp1_calc_0}"
    assert exp1_calc_5 == ["0.70", "0.20", "0.20", "0.70", "0.430", "10.21"], f"Exp 1 5V calc mismatch: {exp1_calc_5}"
    for r_idx in (2, 3, 5, 6):
        mode = exp1_tbl.rows[r_idx].cells[1].text.strip()
        vals = [c.text.strip() for c in exp1_tbl.rows[r_idx].cells[2:]]
        assert mode in ("Simulation", "Measurement"), f"Unexpected Exp 1 row {r_idx} mode: {mode}"
        assert all(v == "" for v in vals), f"Exp 1 row {r_idx} ({mode}) not blank: {vals}"
    print("[PASS] Experiment 1 (Table 2): Calculation rows exact, Simulation & Measurement 100% blank.")

    # Verify Exp 2 Observed column is 100% blank
    for r_idx in range(1, len(exp2_tbl.rows)):
        assert exp2_tbl.rows[r_idx].cells[2].text.strip() == "", f"Exp 2 row {r_idx} observed cell not blank!"
    print("[PASS] Experiment 2 (Table 3): Measured / Observed column 100% blank.")

    # Verify Exp 3 Calculation values and blank Sim/Meas
    expected_exp3_calc = {
        1:  ["0.70", "0.20", "0.915", "5.96"],
        4:  ["0.70", "0.20", "0.430", "5.96"],
        7:  ["0.70", "0.20", "0.195", "5.96"],
        10: ["0.70", "0.20", "0.0915", "5.96"],
    }
    for r_idx, exp_vals in expected_exp3_calc.items():
        got = [c.text.strip() for c in exp3_tbl.rows[r_idx].cells[2:]]
        assert got == exp_vals, f"Exp 3 row {r_idx} calc mismatch: {got} != {exp_vals}"
        for blank_r in (r_idx + 1, r_idx + 2):
            mode = exp3_tbl.rows[blank_r].cells[1].text.strip()
            vals = [c.text.strip() for c in exp3_tbl.rows[blank_r].cells[2:]]
            assert mode in ("Simulation", "Measurement"), f"Unexpected Exp 3 row {blank_r} mode: {mode}"
            assert all(v == "" for v in vals), f"Exp 3 row {blank_r} ({mode}) not blank: {vals}"
    print("[PASS] Experiment 3 (Table 4): Calculation rows exact, Simulation & Measurement 100% blank.")

    # Verify Exp 3 bench log column is 100% blank
    for r_idx in range(1, len(log_tbl.rows)):
        assert log_tbl.rows[r_idx].cells[1].text.strip() == "", f"Bench log row {r_idx} not blank!"
    print("[PASS] Experiment 3 Bench Observation Log: 100% blank.")

    # Check G: Grading Guideline and Team Contribution preserved + clean punctuation
    assert "GRADING GUIDELINE FOR LAB REPORT" in full_docx_text
    assert "TEAM CONTRIBUTION" in full_docx_text
    assert "…" not in doc.tables[1].cell(1, 2).text, "Ellipsis still present in Team Contribution!"
    assert "Nguyễn Lê Minh Sang" in full_docx_text and "EEACIU24096" in full_docx_text
    assert "Nguyễn Gia Huy" in full_docx_text and "EEACIU24047" in full_docx_text
    assert "EE091IU" in full_docx_text
    print("[PASS] ABET Front Matter (Cover, Grading Guideline, Team Contribution, Footer EE091IU) preserved and cleaned.")

    # Check H: Verbatim TOC / LOF / LOT synchronization assertions
    toc_tbl = doc.tables[2]
    lof_tbl = doc.tables[3]
    lot_tbl = doc.tables[4]
    assert toc_tbl.rows[0].cells[2].text.strip() == "Page", "TOC col 3 header must be Page"
    assert lof_tbl.rows[0].cells[2].text.strip() == "Page", "LOF col 3 header must be Page"
    assert lot_tbl.rows[0].cells[2].text.strip() == "Page", "LOT col 3 header must be Page"
    body_para_texts = [p.text.strip() for p in doc.paragraphs]
    for i in range(1, 8):
        lof_cap = lof_tbl.rows[i].cells[1].text.strip()
        expected_body = f"Figure {i}. {lof_cap}"
        assert expected_body in body_para_texts, f"LOF caption mismatch for Figure {i}: {expected_body!r}"
    for i in range(1, 5):
        lot_cap = lot_tbl.rows[i].cells[1].text.strip()
        expected_body = f"Table {i}. {lot_cap}"
        assert expected_body in body_para_texts, f"LOT caption mismatch for Table {i}: {expected_body!r}"
    print("[PASS] Verbatim LOF (7/7) and LOT (4/4) caption synchronization verified.")

    print("=" * 72)
    print("ALL STATIC VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 72)


def export_pdf_via_word(docx_path, pdf_path):
    ps_cmd = (
        f"$w = New-Object -ComObject Word.Application; "
        f"$w.Visible = $false; "
        f"$d = $w.Documents.Open('{docx_path}', $false, $true); "
        f"$d.SaveAs([ref]'{pdf_path}', [ref]17); "
        f"$d.Close($false); "
        f"$w.Quit();"
    )
    res = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True,
        text=True,
        timeout=90,
    )
    if res.returncode != 0:
        raise RuntimeError(f"Word COM PDF export failed: {res.stderr}")


def extract_actual_page_map(pdf_path):
    pdf = pymupdf.open(str(pdf_path))
    total_pages = len(pdf)
    page_texts = [page.get_text("text") for page in pdf]
    pdf.close()

    def find_page(needle, min_page=1):
        norm_needle = re.sub(r"\s+", " ", needle).strip()
        for pno in range(min_page, total_pages + 1):
            norm_page = re.sub(r"\s+", " ", page_texts[pno - 1])
            if norm_needle in norm_page:
                return str(pno)
        raise RuntimeError(f"Could not locate {needle!r} in rendered PDF (min_page={min_page})")

    actual = {
        "Grading Guideline for Lab Report": find_page("GRADING GUIDELINE FOR LAB REPORT", 2),
        "Team Contribution": find_page("TEAM CONTRIBUTION", 2),
        "List of Figures": find_page("List of Figures", 5),
        "List of Tables": find_page("List of Tables", 5),
        "Nomenclature": find_page("Nomenclature", 5),
        "1. Objectives": find_page("1. Objectives", 6),
        "2. Theoretical Background": find_page("2. Theoretical Background", 6),
        "2.1 NPN BJT Operating Regions and Switching Action": find_page("2.1 NPN BJT Operating Regions and Switching Action", 6),
        "2.2 Governing Equations (Sedra & Smith, 6th Edition)": find_page("2.2 Governing Equations (Sedra & Smith, 6th Edition)", 6),
        "2.3 Step-by-Step Theoretical Calculations": find_page("2.3 Step-by-Step Theoretical Calculations", 6),
        "3. Experimental Procedure": find_page("3. Experimental Procedure", 6),
        "3.1 Material and Equipment": find_page("3.1 Material and Equipment", 6),
        "3.2 Experiment 1: Static Biasing and Switching": find_page("3.2 Experiment 1: Static Biasing and Switching", 6),
        "3.3 Experiment 2: Switching Response to Square Wave": find_page("3.3 Experiment 2: Switching Response to Square Wave", 6),
        "3.4 Experiment 3: Driving an LED": find_page("3.4 Experiment 3: Driving an LED", 6),
        "4. Experimental Results": find_page("4. Experimental Results", 6),
        "4.1 Experiment 1: Static Biasing and Switching": find_page("4.1 Experiment 1: Static Biasing and Switching", 6),
        "4.2 Experiment 2: Switching Response to Square Wave": find_page("4.2 Experiment 2: Switching Response to Square Wave", 6),
        "4.3 Experiment 3: Driving an LED": find_page("4.3 Experiment 3: Driving an LED", 6),
        "5. Discussion of Results": find_page("5. Discussion of Results", 6),
        "5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)": find_page("5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)", 6),
        "5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)": find_page("5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)", 6),
        "5.3 Non-Ideal Deviations and Lab Verification Checklist": find_page("5.3 Non-Ideal Deviations and Lab Verification Checklist", 6),
        "5.4 Summary": find_page("5.4 Summary", 6),
        "References": find_page("References", 15),
        "Figure 1": find_page("Figure 1. Bipolar junction transistor", 6),
        "Figure 2": find_page("Figure 2. NPN BJT switch in saturation", 6),
        "Figure 3": find_page("Figure 3. NPN BJT switch in cutoff", 6),
        "Figure 4": find_page("Figure 4. Experiment 1 circuit schematic", 6),
        "Figure 5": find_page("Figure 5. Experiment 3 circuit schematic", 6),
        "Figure 6": find_page("Figure 6. Experiment 2 theoretical waveforms", 6),
        "Figure 7": find_page("Figure 7. Experiment 3 analytical sweep", 6),
        "Table 1": find_page("Table 1. NPN BJT operating regions", 6),
        "Table 2": find_page("Table 2. Experiment 1 static biasing", 6),
        "Table 3": find_page("Table 3. Experiment 2 theoretical waveform", 6),
        "Table 4": find_page("Table 4. Experiment 3 LED driver results", 6),
    }
    return actual, total_pages


def write_audit_dump(actual_page_map, total_pages):
    doc = docx.Document(str(DOCX_OUT))
    lines = []
    lines.append(f"Paragraphs: {len(doc.paragraphs)}, Tables: {len(doc.tables)}, Rendered PDF Pages: {total_pages}")
    for si, s in enumerate(doc.sections):
        hdrs = [p.text for p in s.header.paragraphs if p.text.strip()]
        ftrs = [p.text for p in s.footer.paragraphs if p.text.strip()]
        lines.append(f"Section {si} Header: {hdrs}")
        lines.append(f"Section {si} Footer: {ftrs}")

    lines.append("\n=== PARAGRAPHS ===")
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip():
            lines.append(f"P[{i:03d}] ({p.style.name}): {p.text}")

    lines.append("\n=== TABLES ===")
    for ti, t in enumerate(doc.tables):
        lines.append(f"\n--- TABLE {ti} ({len(t.rows)}x{len(t.columns)}) ---")
        for ri, r in enumerate(t.rows):
            vals = [c.text.strip().replace("\n", " / ") for c in r.cells]
            lines.append(f"  R{ri:02d}: {vals}")

    lines.append("\n=== PDF PAGE NUMBER VERIFICATION (WORD COM) ===")
    lines.append(f"Total Rendered Pages: {total_pages}")
    for k, v in actual_page_map.items():
        lines.append(f"  [VERIFIED MATCH] {k} -> Page {v}")

    AUDIT_DUMP_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved Audit Dump: {AUDIT_DUMP_OUT}")


def run_full_pipeline():
    # Pass 1: Build with DEFAULT_PAGE_MAP and export temporary PDF via Word COM
    build_docx(DEFAULT_PAGE_MAP)
    build_markdown()
    export_pdf_via_word(DOCX_OUT, TEMP_PDF_OUT)
    actual_map, total_pages = extract_actual_page_map(TEMP_PDF_OUT)

    # Pass 2: If any page differs from DEFAULT_PAGE_MAP, rebuild DOCX and re-verify via Word COM
    if actual_map != DEFAULT_PAGE_MAP:
        print("Detected page shifts; rebuilding DOCX with exact Word COM page numbers...")
        for k in DEFAULT_PAGE_MAP:
            if DEFAULT_PAGE_MAP[k] != actual_map[k]:
                print(f"  Updated {k}: {DEFAULT_PAGE_MAP[k]} -> {actual_map[k]}")
        build_docx(actual_map)
        export_pdf_via_word(DOCX_OUT, TEMP_PDF_OUT)
        verified_map, total_pages = extract_actual_page_map(TEMP_PDF_OUT)
        assert verified_map == actual_map, f"Page numbers shifted after Pass 2: {verified_map} != {actual_map}"
        actual_map = verified_map

    # Confirm DOCX TOC/LOF/LOT cells match actual_map 100%
    doc = docx.Document(str(DOCX_OUT))
    toc_tbl, lof_tbl, lot_tbl = doc.tables[2], doc.tables[3], doc.tables[4]
    toc_keys = [
        "Grading Guideline for Lab Report", "Team Contribution", "List of Figures",
        "List of Tables", "Nomenclature", "1. Objectives", "2. Theoretical Background",
        "2.1 NPN BJT Operating Regions and Switching Action",
        "2.2 Governing Equations (Sedra & Smith, 6th Edition)",
        "2.3 Step-by-Step Theoretical Calculations", "3. Experimental Procedure",
        "3.1 Material and Equipment", "3.2 Experiment 1: Static Biasing and Switching",
        "3.3 Experiment 2: Switching Response to Square Wave",
        "3.4 Experiment 3: Driving an LED", "4. Experimental Results",
        "4.1 Experiment 1: Static Biasing and Switching",
        "4.2 Experiment 2: Switching Response to Square Wave",
        "4.3 Experiment 3: Driving an LED", "5. Discussion of Results",
        "5.1 Experiment 2 Switching Waveform Analysis (Lab Question 2c)",
        "5.2 Experiment 3 Biasing, Minimum Base Current, and Base Resistor Tradeoffs (Lab Questions 3d)",
        "5.3 Non-Ideal Deviations and Lab Verification Checklist",
        "5.4 Summary", "References",
    ]
    for ri, key in enumerate(toc_keys, start=1):
        got = toc_tbl.rows[ri].cells[2].text.strip()
        assert got == actual_map[key], f"TOC page mismatch for {key}: {got} != {actual_map[key]}"
    for i in range(1, 8):
        got = lof_tbl.rows[i].cells[2].text.strip()
        assert got == actual_map[f"Figure {i}"], f"LOF page mismatch for Figure {i}: {got} != {actual_map[f'Figure {i}']}"
    for i in range(1, 5):
        got = lot_tbl.rows[i].cells[2].text.strip()
        assert got == actual_map[f"Table {i}"], f"LOT page mismatch for Table {i}: {got} != {actual_map[f'Table {i}']}"
    print(f"[PASS] 100% of TOC (25/25), LOF (7/7), and LOT (4/4) page numbers match rendered Word PDF ({total_pages} pages).")

    # Delete temporary PDF to keep Lab5 folder clean
    if TEMP_PDF_OUT.exists():
        TEMP_PDF_OUT.unlink()

    verify_outputs()
    write_audit_dump(actual_map, total_pages)
    print("\nFINAL VERIFIED PAGE MAP:", actual_map)


if __name__ == "__main__":
    run_full_pipeline()
