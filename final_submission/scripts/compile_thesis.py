#!/usr/bin/env python3
"""
VayuDrishti — Master IQAC Thesis Compiler (Submission Quality for Final Evaluation)
Compiles all thesis chapters, front matter, figures, tables, appendices, and subject index
into the authoritative CGU IQAC Project_Report.docx and exports Project_Report.pdf.

Enforces:
- Real CGU seal extracted PNG (report_assets/cgu_logo.png) centered on cover page (~3.0 cm)
- Exact Preliminary Pages & Wording per C.V. Raman Global University (CGU) IQAC Template:
  1. Cover Page
  2. BONAFIDE CERTIFICATE
  3. CERTIFICATE OF APPROVAL
  4. DECLARATION
  5. ACKNOWLEDGMENTS
  6. ABSTRACT
  7. TABLE OF CONTENTS (Word Dynamic Field)
  8. LIST OF FIGURES (Word Dynamic Field)
  9. LIST OF TABLES (Word Dynamic Field)
  10. LIST OF SYMBOLS & ABBREVIATIONS
- Exact 5 Academic Chapters per CGU IQAC Format:
  Chapter 1: INTRODUCTION
  Chapter 2: LITERATURE SURVEY
  Chapter 3: METHODOLOGY
  Chapter 4: RESULTS AND DISCUSSION
  Chapter 5: CONCLUSION
- 35 IEEE Formatted References
- Full Appendices (A: Notation, B: Hyperparameters, C: Pytest Test Suite, D: Team Rubrics Matrix)
- Dynamic Subject Index (Word Dynamic Field)
- Strict pagination discipline: widow/orphan control, keep_with_next on all headings/captions,
  cantSplit on table rows, tblHeader on header rows
"""

import os, sys, json
from pathlib import Path

# Enable unbuffered output with utf-8 encoding
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import docx
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml

import latex2mathml.converter
from lxml import etree

ROOT = Path(__file__).resolve().parent.parent.parent
FINAL = ROOT / "final_submission"
RESULTS = FINAL / "results"
ASSETS = FINAL / "report_assets"
THESIS_OUT = FINAL / "thesis"
MODULES_DIR = FINAL / "scripts" / "thesis_modules"
THESIS_OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(MODULES_DIR))

import chap1, chap2, chap3, chap4, chap5_app

# Load MathML to OMML XSLT
xslt_path = r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'
xslt = etree.parse(xslt_path)
mml2omml_transform = etree.XSLT(xslt)

doc = Document()

# Configure page setup: A4, 35mm left/right, 30mm top/bottom per IQAC specification
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3.5)
    section.right_margin = Cm(3.5)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(3.0)

# Configure / ensure custom styles for TOC, LOF, LOT
styles = doc.styles

# Heading 1
try:
    h1_style = styles['Heading 1']
except KeyError:
    h1_style = styles.add_style('Heading 1', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
h1_style.font.name = 'Times New Roman'
h1_style.font.size = Pt(16)
h1_style.font.bold = True
h1_style.font.color.rgb = RGBColor(0, 0, 0)
h1_style.paragraph_format.keep_with_next = True
h1_style.paragraph_format.widow_control = True

# Heading 2
try:
    h2_style = styles['Heading 2']
except KeyError:
    h2_style = styles.add_style('Heading 2', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
h2_style.font.name = 'Times New Roman'
h2_style.font.size = Pt(13.5)
h2_style.font.bold = True
h2_style.font.color.rgb = RGBColor(0, 0, 0)
h2_style.paragraph_format.keep_with_next = True
h2_style.paragraph_format.widow_control = True

# Heading 3
try:
    h3_style = styles['Heading 3']
except KeyError:
    h3_style = styles.add_style('Heading 3', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
h3_style.font.name = 'Times New Roman'
h3_style.font.size = Pt(12)
h3_style.font.bold = True
h3_style.font.color.rgb = RGBColor(0, 0, 0)
h3_style.paragraph_format.keep_with_next = True
h3_style.paragraph_format.widow_control = True

# Heading 4
try:
    h4_style = styles['Heading 4']
except KeyError:
    h4_style = styles.add_style('Heading 4', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
h4_style.font.name = 'Times New Roman'
h4_style.font.size = Pt(11.5)
h4_style.font.bold = True
h4_style.font.italic = True
h4_style.font.color.rgb = RGBColor(0, 0, 0)
h4_style.paragraph_format.keep_with_next = True
h4_style.paragraph_format.widow_control = True

# Custom FigureCaption style
try:
    fig_style = styles.add_style('FigureCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
except Exception:
    fig_style = styles['FigureCaption']
fig_style.base_style = styles['Normal']
fig_style.font.name = 'Times New Roman'
fig_style.font.size = Pt(10)
fig_style.font.italic = True
fig_style.font.color.rgb = RGBColor(0, 0, 0)
fig_style.paragraph_format.keep_with_next = True
fig_style.paragraph_format.widow_control = True

# Custom TableCaption style
try:
    tbl_style = styles.add_style('TableCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
except Exception:
    tbl_style = styles['TableCaption']
tbl_style.base_style = styles['Normal']
tbl_style.font.name = 'Times New Roman'
tbl_style.font.size = Pt(10)
tbl_style.font.italic = True
tbl_style.font.color.rgb = RGBColor(0, 0, 0)
tbl_style.paragraph_format.keep_with_next = True
tbl_style.paragraph_format.widow_control = True

# Tighten TOC entry styles
for toc_name in ['TOC 1', 'TOC 2', 'TOC 3']:
    try:
        t_style = styles[toc_name]
    except Exception:
        try:
            t_style = styles.add_style(toc_name, docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
        except Exception:
            continue
    t_style.font.name = 'Times New Roman'
    t_style.font.size = Pt(10.5)
    t_style.paragraph_format.line_spacing = 1.10
    t_style.paragraph_format.space_before = Pt(1)
    t_style.paragraph_format.space_after = Pt(1)
    t_style.paragraph_format.widow_control = True

def set_cell_shading(cell, color_hex):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), color_hex)
    shading.set(qn('w:val'), 'clear')
    cell._tc.get_or_add_tcPr().append(shading)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:cantSplit'))

def tbl_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:tblHeader'))

def add_field(p, field_str):
    r = p.add_run()
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = field_str
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'separate')
    f3 = OxmlElement('w:fldChar')
    f3.set(qn('w:fldCharType'), 'end')
    r._r.append(f1)
    r._r.append(it)
    r._r.append(f2)
    r._r.append(f3)

def add_index_entry(p, term):
    r = p.add_run()
    f1 = OxmlElement('w:fldChar')
    f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText')
    it.set(qn('xml:space'), 'preserve')
    it.text = f'XE "{term}"'
    f2 = OxmlElement('w:fldChar')
    f2.set(qn('w:fldCharType'), 'end')
    r._r.append(f1)
    r._r.append(it)
    r._r.append(f2)

from scientific_formatter import add_formatted_runs, format_cell_text

def add_p(text, bold=False, italic=False, font_size=12, alignment=None,
          space_after=6, space_before=0, first_line_indent=None, line_spacing=1.5):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.widow_control = True
    if alignment:
        pf.alignment = alignment
    if first_line_indent:
        pf.first_line_indent = Cm(first_line_indent)
    pf.line_spacing = line_spacing
    add_formatted_runs(p, text, base_font_size=font_size, base_bold=bold, base_italic=italic, base_font_name='Times New Roman')
    return p

def add_body(text, indent=True):
    return add_p(text, font_size=12, space_after=6, first_line_indent=1.27 if indent else None, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

def add_h1(chap_num, title):
    doc.add_page_break()
    p = doc.add_paragraph(style='Heading 1')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.widow_control = True
    add_formatted_runs(p, f"Chapter {chap_num}\n{title.upper()}", base_font_size=16, base_bold=True, base_font_name='Times New Roman')
    return p

def add_h2(num, title):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.widow_control = True
    add_formatted_runs(p, f"{num} {title}", base_font_size=13.5, base_bold=True, base_font_name='Times New Roman')
    return p

def add_h3(num, title):
    p = doc.add_paragraph(style='Heading 3')
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.widow_control = True
    add_formatted_runs(p, f"{num} {title}", base_font_size=12, base_bold=True, base_font_name='Times New Roman')
    return p

def add_h4(num, title):
    p = doc.add_paragraph(style='Heading 4')
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.widow_control = True
    add_formatted_runs(p, f"{num} {title}", base_font_size=11.5, base_bold=True, base_italic=True, base_font_name='Times New Roman')
    return p

def add_eq(eq_text, eq_num):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cant_split(table.rows[0])
    c_eq, c_num = table.rows[0].cells[0], table.rows[0].cells[1]
    c_eq.width, c_num.width = Inches(4.8), Inches(1.0)
    
    pe = c_eq.paragraphs[0]
    pe.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pe.paragraph_format.space_before = Pt(4)
    pe.paragraph_format.space_after = Pt(4)
    pe.paragraph_format.widow_control = True
    
    try:
        mathml = latex2mathml.converter.convert(eq_text)
        tree = etree.fromstring(mathml.encode('utf-8'))
        omml = mml2omml_transform(tree)
        omml_str = etree.tostring(omml, encoding='unicode')
        omml_elem = parse_xml(omml_str.encode('utf-8'))
        pe._p.append(omml_elem)
    except Exception as e:
        re = pe.add_run(eq_text)
        re.font.name = 'Cambria Math'
        re.font.size = Pt(11)
        re.italic = True
    
    pn = c_num.paragraphs[0]
    pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pn.paragraph_format.space_before = Pt(4)
    pn.paragraph_format.space_after = Pt(4)
    pn.paragraph_format.widow_control = True
    rn = pn.add_run(f"({eq_num})")
    rn.font.name = 'Times New Roman'
    rn.font.size = Pt(11)
    rn.bold = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_fig(img_path, caption, fig_num, width_in=5.2):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        p_img.paragraph_format.widow_control = True
        r = p_img.add_run()
        r.add_picture(str(img_path), width=Inches(width_in))
        
        cap = doc.add_paragraph(style='FigureCaption')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(10)
        cap.paragraph_format.keep_with_next = False
        cap.paragraph_format.widow_control = True
        add_formatted_runs(cap, f"Figure {fig_num}: {caption}", base_font_size=10, base_italic=True, base_font_name='Times New Roman')

def add_tbl(headers, rows, table_num, caption):
    cap = doc.add_paragraph(style='TableCaption')
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(10)
    cap.paragraph_format.space_after = Pt(4)
    cap.paragraph_format.keep_with_next = True
    cap.paragraph_format.widow_control = True
    add_formatted_runs(cap, f"Table {table_num}: {caption}", base_font_size=10, base_italic=True, base_font_name='Times New Roman')

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    tbl_header(table.rows[0])
    for row in table.rows:
        cant_split(row)

    for i, h in enumerate(headers):
        c = table.rows[0].cells[i]
        set_cell_margins(c, 80, 80, 100, 100)
        set_cell_shading(c, 'D9E2F3')
        format_cell_text(c, h, base_font_size=9, base_bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            c = table.rows[r_idx + 1].cells[c_idx]
            set_cell_margins(c, 60, 60, 80, 80)
            format_cell_text(c, str(val), base_font_size=8.5, alignment=WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table

def add_algo(algo_num, title, inputs, outputs, steps):
    add_p(f"Algorithm {algo_num}: {title}", bold=True, font_size=10.5, space_before=8, space_after=3)
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    cant_split(table.rows[0])
    c = table.rows[0].cells[0]
    set_cell_shading(c, 'F7F9FB')
    set_cell_margins(c, 100, 100, 120, 120)
    
    cp = c.paragraphs[0]
    cp.paragraph_format.line_spacing = 1.15
    cp.paragraph_format.space_after = Pt(3)
    cp.paragraph_format.widow_control = True
    r_in = cp.add_run(f"Input:  {inputs}\nOutput: {outputs}\n")
    r_in.font.name = 'Courier New'
    r_in.font.size = Pt(9)
    r_in.bold = True
    
    for s in steps:
        sp = c.add_paragraph()
        sp.paragraph_format.line_spacing = 1.15
        sp.paragraph_format.space_before = Pt(1)
        sp.paragraph_format.space_after = Pt(1)
        sp.paragraph_format.widow_control = True
        rs = sp.add_run(s)
        rs.font.name = 'Courier New'
        rs.font.size = Pt(8.5)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

print("Starting Master Thesis Compilation strictly according to CGU IQAC Template...")

# ═══════════════════════════════════════════════════════════════════════════════
# COVER PAGE (CGU IQAC Template Format with Real CGU Seal Centered)
# ═══════════════════════════════════════════════════════════════════════════════
add_p("", space_after=2)
add_p("AI-DRIVEN AIR QUALITY FORECASTING AND PUBLIC HEALTH\nRISK ALERT SYSTEM FOR INDIAN METROPOLITAN CITIES",
      bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

add_p("A PROJECT REPORT", bold=True, font_size=13,
      alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
add_p("Submitted in partial fulfillment of the requirements\nfor the award of the degree of",
      font_size=11, italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
add_p("BACHELOR OF TECHNOLOGY\nIN\nCOMPUTER SCIENCE AND ENGINEERING",
      bold=True, font_size=12.5, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

# Real CGU Emblem Centered (~3.0 cm)
cgu_logo_path = ASSETS / "cgu_logo.png"
if cgu_logo_path.exists():
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(2)
    p_logo.paragraph_format.space_after = Pt(6)
    p_logo.paragraph_format.keep_with_next = True
    p_logo.paragraph_format.widow_control = True
    r_logo = p_logo.add_run()
    r_logo.add_picture(str(cgu_logo_path), width=Inches(1.18)) # ~3.0 cm
else:
    print("WARNING: cgu_logo.png not found!")

add_p("Submitted by", italic=True, font_size=11.5, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)

team_table = doc.add_table(rows=5, cols=2)
team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
team_table.autofit = False
for r in team_table.rows:
    cant_split(r)
team_members = [
    ("Name of Student", "Registration No."),
    ("SATYAPRAKASH ROUT (7th Sem)", "2301020206"),
    ("LIKUNA SWAIN (7th Sem)", "2301020252"),
    ("CH SAIPRIYA PATRA (7th Sem)", "2301020205"),
    ("ARPEET BARIK (7th Sem)", "2301020228")
]
for idx, (name, reg) in enumerate(team_members):
    c0, c1 = team_table.rows[idx].cells[0], team_table.rows[idx].cells[1]
    c0.width, c1.width = Inches(3.2), Inches(2.2)
    set_cell_margins(c0, 20, 20, 50, 50)
    set_cell_margins(c1, 20, 20, 50, 50)
    p0, p1 = c0.paragraphs[0], c1.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(0)
    p0.paragraph_format.line_spacing = 1.05
    p1.paragraph_format.line_spacing = 1.05
    r0, r1 = p0.add_run(name), p1.add_run(reg)
    r0.font.name, r1.font.name = 'Times New Roman', 'Times New Roman'
    r0.font.size, r1.font.size = Pt(9.5), Pt(9.5)
    if idx == 0:
        r0.bold, r1.bold = True, True
        set_cell_shading(c0, 'EAECEE')
        set_cell_shading(c1, 'EAECEE')

add_p("Under the guidance of", italic=True, font_size=11, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=1)
add_p("PROF. SOUMYA SAHOO", bold=True, font_size=12.5, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=1)
add_p("Assistant Professor, Department of Computer Science & Engineering", font_size=10, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

add_p("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\nC.V. RAMAN GLOBAL UNIVERSITY\nBHUBANESWAR, ODISHA, 752054\nOCTOBER 2026",
      bold=True, font_size=11, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: BONAFIDE CERTIFICATE (Matching CGU Template Order and Text)
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("C.V. RAMAN GLOBAL UNIVERSITY\nBHUBANESWAR - ODISHA - 752054", bold=True, font_size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
add_p("BONAFIDE CERTIFICATE", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("Certified that this project report \"AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities\" is bonafide work submitted by Satyaprakash Rout (2301020206), Likuna Swain (2301020252), Ch Saipriya Patra (2301020205), and Arpeet Barik (2301020228), 7th Semester, CGU-Odisha, Bhubaneswar who carried out the project under my supervision.")
add_body("To the best of our knowledge, the work reported herein does not form part of any other thesis or dissertation on the basis of which a degree or award was conferred on an earlier occasion on this or any other candidate.")

add_p("", space_after=40)
bon_table = doc.add_table(rows=1, cols=2)
bon_table.alignment = WD_TABLE_ALIGNMENT.CENTER
for r in bon_table.rows:
    cant_split(r)
c_b1, c_b2 = bon_table.rows[0].cells[0], bon_table.rows[0].cells[1]
c_b1.width, c_b2.width = Inches(3.0), Inches(3.0)

pb1 = c_b1.paragraphs[0]
pb1.add_run("_________________________\nProf. Soumya Sahoo\nProject Supervisor\nDept. of CSE, CGU").font.name = 'Times New Roman'
pb2 = c_b2.paragraphs[0]
pb2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r_hod = pb2.add_run("_________________________\nDr. Debendra Muduli\nHead of the Department\nDepartment of CSE & AIML\nCGU, Bhubaneswar")
r_hod.font.name = 'Times New Roman'
r_hod.bold = True

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3: CERTIFICATE OF APPROVAL (Matching CGU Template Order and Text)
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("C.V. RAMAN GLOBAL UNIVERSITY\nBHUBANESWAR - ODISHA - 752054", bold=True, font_size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
add_p("CERTIFICATE OF APPROVAL", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("This is to certify that we have examined the project entitled \"AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities\" is bonafide work submitted by Satyaprakash Rout (2301020206), Likuna Swain (2301020252), Ch Saipriya Patra (2301020205), and Arpeet Barik (2301020228), 7th Semester, CGU-Odisha, Bhubaneswar.")
add_body("We hereby accord our approval of it as a major project work carried out and presented in a manner required for its acceptance for the partial fulfillment for Bachelor Degree of Computer Science and Engineering for which it has been submitted. This approval does not necessarily endorse or accept every statement made, opinion expressed, or conclusions drawn as recorded in this major project, it only signifies the acceptance of the major project for the purpose it has been submitted.")

add_p("", space_after=40)
sig_table = doc.add_table(rows=1, cols=2)
sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
for r in sig_table.rows:
    cant_split(r)
c_g, c_h = sig_table.rows[0].cells[0], sig_table.rows[0].cells[1]
c_g.width, c_h.width = Inches(3.0), Inches(3.0)

pg = c_g.paragraphs[0]
pg.add_run("_________________________\nSUPERVISOR\nProf. Soumya Sahoo\nDept. of CSE, CGU").font.name = 'Times New Roman'
ph = c_h.paragraphs[0]
ph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
ph.add_run("_________________________\nEXTERNAL EXAMINER\nBoard of Evaluators\nCGU, Bhubaneswar").font.name = 'Times New Roman'

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4: DECLARATION (Matching CGU Template Order and Text)
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("DECLARATION", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("We declare that this project report titled \"AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities\" submitted in partial fulfillment of the degree of B. Tech in Computer Science and Engineering is a record of original work carried out by us under the supervision of Prof. Soumya Sahoo, and has not formed the basis for the award of any other degree or diploma, in this or any other Institution or University. In keeping with the ethical practice in reporting scientific information, due acknowledgements have been made wherever the findings of others have been cited.")

add_p("", space_after=24)
dec_tbl = doc.add_table(rows=5, cols=3)
dec_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
for r in dec_tbl.rows:
    cant_split(r)
dec_members = [
    ("Candidate Name", "Registration No.", "Signature"),
    ("Satyaprakash Rout", "2301020206", "_________________"),
    ("Likuna Swain", "2301020252", "_________________"),
    ("Ch Saipriya Patra", "2301020205", "_________________"),
    ("Arpeet Barik", "2301020228", "_________________")
]
for idx, (name, reg, sig) in enumerate(dec_members):
    c0, c1, c2 = dec_tbl.rows[idx].cells[0], dec_tbl.rows[idx].cells[1], dec_tbl.rows[idx].cells[2]
    c0.width, c1.width, c2.width = Inches(2.5), Inches(1.8), Inches(1.8)
    p0, p1, p2 = c0.paragraphs[0], c1.paragraphs[0], c2.paragraphs[0]
    p0.alignment, p1.alignment, p2.alignment = WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER
    r0, r1, r2 = p0.add_run(name), p1.add_run(reg), p2.add_run(sig)
    r0.font.name, r1.font.name, r2.font.name = 'Times New Roman', 'Times New Roman', 'Times New Roman'
    if idx == 0:
        r0.bold, r1.bold, r2.bold = True, True, True
        set_cell_shading(c0, 'EAECEE')
        set_cell_shading(c1, 'EAECEE')
        set_cell_shading(c2, 'EAECEE')

add_p("", space_after=12)
add_p("Bhubaneswar - 752054\nDate: October 10, 2026", font_size=11, space_after=6)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5: ACKNOWLEDGMENTS (Candidate Names at end without signature per CGU)
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("ACKNOWLEDGMENTS", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("We express our profound gratitude to our project supervisor, Prof. Soumya Sahoo, Assistant Professor, Department of Computer Science & Engineering, for his invaluable technical guidance, constructive criticism, and unwavering encouragement throughout the design, empirical validation, and execution of this major project. His high standards for scientific rigor directly shaped the methodology and verification protocols of this work.")
add_body("We extend our sincere thanks to Dr. Sukant Kishoro Bisoy, Associate Professor and Dean, the Head of the Department of Computer Science & Engineering, and the faculty evaluation committee for providing state-of-the-art computational laboratories, infrastructural support, and institutional guidance necessary for high-performance machine learning experimentation.")
add_body("We gratefully acknowledge the Central Pollution Control Board (CPCB), the European Centre for Medium-Range Weather Forecasts (ECMWF Copernicus CAMS), and the OpenAQ international community for providing open access to environmental sensor telemetry and atmospheric numerical reanalysis datasets that formed the empirical foundation of our research.")
add_body("We extend our sincere thanks to one and all of the CGU family for their continuous moral support and encouragement throughout the demanding course of this major project.")

add_p("", space_after=24)
add_p("Satyaprakash Rout\nLikuna Swain\nCh Saipriya Patra\nArpeet Barik", bold=True, font_size=11, space_after=6)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6: ABSTRACT
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("ABSTRACT", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

def add_ab(text):
    return add_p(text, font_size=10.5, space_after=5, first_line_indent=1.0, line_spacing=1.2, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

add_ab("Ambient air pollution in Indian metropolitan cities represents a catastrophic public health crisis, causing an estimated 1.67 million premature deaths annually. Traditional statutory monitoring under the Central Pollution Control Board (CPCB) National Air Quality Index (NAQI) suffers from three fundamental systemic limitations: (i) retrospective reporting that notifies citizens only after hazardous inhalation has occurred; (ii) single-pollutant piecewise maximum distortion that obscures toxicological co-pollutant cocktails; and (iii) uniform population thresholds that ignore elevated physiological vulnerabilities among pediatric, geriatric, and cardiorespiratory cohorts.")
add_ab("This thesis introduces VayuDrishti (वायुदृष्टि), an end-to-end artificial intelligence forecasting and public health risk alert platform engineered specifically for Indian metropolitan airsheds. Utilizing a multi-source ground truth dataset of 12,042 validated hourly telemetry records across five primary metropolitan centers (Delhi, Mumbai, Bengaluru, Chennai, and Hyderabad), the system couples physical meteorological dynamics with advanced machine learning architectures.")
add_ab("To resolve severe sensor missingness (averaging 8.4% and peaking at 18.4%), we deploy Multivariate Imputation by Chained Equations (MICE), achieving an imputation RMSE of 0.0061—a 75.6% error reduction over standard KNN imputation. A symmetrical PyTorch Deep Autoencoder compresses six criteria pollutants into a 4-dimensional latent manifold (reconstruction MSE = 0.0084), capturing complex non-linear photochemical interactions. For forward forecasting up to 72 hours, an Optuna-tuned Stacking Ensemble blending Extreme Gradient Boosting (XGBoost) and Random Forest via Ridge meta-regression achieves a peak test R² of 0.9248, an RMSE of 13.84 AQI points, MAE of 9.12 AQI points, and a continuous regression accuracy of 91.42% (baseline un-tuned stacking R² = 0.9014, RMSE = 16.64, accuracy = 87.02%) on held-out test data, significantly outperforming standalone models (p = 0.0002 on paired t-test; p = 3.003e-5 on Wilcoxon signed-rank test). We openly document the exclusion of Deep LSTM architectures (R² = 0.8312, RMSE = 21.68) which overfit on daily tabular lag structures.")
add_ab("To address uncertainty, pinball-loss calibrated quantile regressors provide 90% prediction intervals achieving 90.01% empirical coverage (PICP) with an average width of 43.91 AQI points. We propose a mathematically novel Health Risk Index (HRI) based on a supra-additive bounded exponential formulation with stratified demographic multipliers (1.0x for healthy adults, 1.3x for children/elderly, and 1.6x for respiratory patients), delivering actionable four-tier clinical advisories. Deployed via an asynchronous FastAPI engine with Redis caching, the system guarantees sub-10ms inference (mean latency 2.41 ms under 50 concurrent virtual users) and incorporates automated circuit-breaker fallbacks to Copernicus CAMS atmospheric telemetry during sensor dropouts. Across 30 days of real-world live tracking, VayuDrishti maintained an operational R² of 0.8712, providing an honest, verified, and reproducible foundation for proactive public health defense.")

# ═══════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (Word Dynamic Field: TOC \o "1-3" \h \z \u)
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("TABLE OF CONTENTS", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
p_toc = doc.add_paragraph()
p_toc.paragraph_format.space_after = Pt(4)
add_field(p_toc, r'TOC \o "1-3" \h \z \u')

# ═══════════════════════════════════════════════════════════════════════════
# LIST OF FIGURES (Word Dynamic Field: TOC \t "FigureCaption" \h \z)
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("LIST OF FIGURES", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
p_lof = doc.add_paragraph()
p_lof.paragraph_format.space_after = Pt(4)
add_field(p_lof, r'TOC \t "FigureCaption" \h \z')

# ═══════════════════════════════════════════════════════════════════════════
# LIST OF TABLES (Word Dynamic Field: TOC \t "TableCaption" \h \z)
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("LIST OF TABLES", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
p_lot = doc.add_paragraph()
p_lot.paragraph_format.space_after = Pt(4)
add_field(p_lot, r'TOC \t "TableCaption" \h \z')

# ═══════════════════════════════════════════════════════════════════════════
# LIST OF SYMBOLS & ABBREVIATIONS
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("LIST OF SYMBOLS & ABBREVIATIONS", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
abbreviations = [
    ("AE", "Deep Autoencoder"),
    ("API", "Application Programming Interface"),
    ("AQI", "Air Quality Index"),
    ("ASGI", "Asynchronous Server Gateway Interface"),
    ("BLH / PBLH", "Planetary Boundary Layer Height"),
    ("CAAQMS", "Continuous Ambient Air Quality Monitoring Station"),
    ("CAMS", "Copernicus Atmosphere Monitoring Service"),
    ("CO", "Carbon Monoxide"),
    ("CPCB", "Central Pollution Control Board (Government of India)"),
    ("CRPS", "Continuous Ranked Probability Score"),
    ("ECMWF", "European Centre for Medium-Range Weather Forecasts"),
    ("EDA", "Exploratory Data Analysis"),
    ("ERA5", "ECMWF Reanalysis v5 Atmospheric Dataset"),
    ("FCS", "Fully Conditional Specification"),
    ("GRU", "Gated Recurrent Unit"),
    ("HRI", "Health Risk Index"),
    ("IMD", "India Meteorological Department"),
    ("KNN", "K-Nearest Neighbors"),
    ("LOCF", "Last Observation Carried Forward"),
    ("LOCO", "Leave-One-City-Out Cross-Validation"),
    ("LSTM", "Long Short-Term Memory"),
    ("MAE", "Mean Absolute Error"),
    ("MAR", "Missing at Random"),
    ("MCAR", "Missing Completely at Random"),
    ("MICE", "Multivariate Imputation by Chained Equations"),
    ("MI-MMA", "Multi-Imputation Multi-Modal Autoencoder"),
    ("MNAR", "Missing Not at Random"),
    ("MPIW", "Mean Prediction Interval Width"),
    ("MSE", "Mean Squared Error"),
    ("NAAQS", "National Ambient Air Quality Standards"),
    ("NAQI", "National Air Quality Index"),
    ("NO2", "Nitrogen Dioxide"),
    ("O3", "Ground-Level Ozone"),
    ("PICP", "Prediction Interval Coverage Probability"),
    ("PM10", "Particulate Matter ≤ 10 μm"),
    ("PM2.5", "Particulate Matter ≤ 2.5 μm"),
    ("R²", "Coefficient of Determination"),
    ("RF", "Random Forest"),
    ("RMSE", "Root Mean Square Error"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("SLA", "Service Level Agreement"),
    ("SO2", "Sulfur Dioxide"),
    ("SVD", "Singular Value Decomposition"),
    ("TPE", "Tree-structured Parzen Estimator (Optuna)"),
    ("VI", "Ventilation Index (PBLH × Wind Speed)"),
    ("WHO", "World Health Organization"),
    ("XGBoost", "Extreme Gradient Boosting")
]
add_tbl(["Abbreviation / Symbol", "Full Expanded Meaning / Scientific Description"], abbreviations, "0.1", "Standard Abbreviations, Acronyms, and Mathematical Symbols")

print("Front matter generated. Building Chapter 1: INTRODUCTION...")
chap1.build_chapter_1(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_p, add_index_entry=add_index_entry)

print("Building Chapter 2: LITERATURE SURVEY...")
chap2.build_chapter_2(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_fig, add_algo, add_index_entry=add_index_entry, ASSETS=ASSETS)

print("Building Chapter 3: METHODOLOGY (Data Provenance, MICE, Autoencoder, Stacking & 7 Diagrams)...")
chap3.build_chapter_3(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_fig, add_algo, add_index_entry=add_index_entry, ASSETS=ASSETS)

print("Building Chapter 4: RESULTS AND DISCUSSION (Ablations, Hypothesis Tests, LOCO, TreeSHAP, Latency)...")
chap4.build_chapter_4(doc, add_h1, add_h2, add_h3, add_body, add_eq, add_tbl, add_fig, ASSETS=ASSETS, add_index_entry=add_index_entry)

print("Building Chapter 5: CONCLUSION, 35 IEEE REFERENCES & APPENDICES A-D...")
chap5_app.build_chapter_5_and_appendices(doc, add_h1, add_h2, add_h3, add_body, add_tbl, add_p, add_index_entry=add_index_entry)

# ═══════════════════════════════════════════════════════════════════════════════
# SUBJECT INDEX (Word Dynamic Field: INDEX \c "2" \z "1033")
# ═══════════════════════════════════════════════════════════════════════════
doc.add_page_break()
add_p("SUBJECT INDEX", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
add_body("Alphabetical index of key technical terms, algorithmic methodologies, and statutory standards discussed across this thesis.", indent=False)
p_idx = doc.add_paragraph()
p_idx.paragraph_format.space_after = Pt(12)
add_field(p_idx, r'INDEX \c "2" \z "1033"')

output_path = THESIS_OUT / "Project_Report.docx"
print(f"Saving compiled thesis to: {output_path}...")
doc.save(str(output_path))
print("DOCX SAVED SUCCESSFULLY!")

# ═══════════════════════════════════════════════════════════════════════════════
# AUTOMATED WORD COM UPDATE & PDF EXPORT
# ═══════════════════════════════════════════════════════════════════════════
print("Launching Microsoft Word via COM to update all dynamic fields and export PDF...")
try:
    import win32com.client
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0  # wdAlertsNone: suppress all modal alert popups
    doc_path_abs = str(output_path.resolve())
    pdf_path_abs = str((THESIS_OUT / "Project_Report.pdf").resolve())

    wdoc = word.Documents.Open(doc_path_abs)
    
    # Update all fields in the document body
    print("Updating Word dynamic fields (TOC, LOF, LOT, INDEX)...")
    for field in wdoc.Fields:
        field.Update()

    for i in range(1, wdoc.TablesOfContents.Count + 1):
        toc = wdoc.TablesOfContents(i)
        toc.Update()
        try:
            toc.Range.ParagraphFormat.SpaceBefore = 0
            toc.Range.ParagraphFormat.SpaceAfter = 1
            toc.Range.ParagraphFormat.LineSpacingRule = 0  # wdLineSpaceSingle
        except Exception as te:
            print(f"Note on TOC formatting: {te}")

    if wdoc.Indexes.Count > 0:
        wdoc.Indexes(1).Update()

    wdoc.Save()
    print("Docx updated and saved.")

    # Export to PDF
    print(f"Exporting to PDF: {pdf_path_abs}...")
    # FileFormat=17 is wdFormatPDF
    wdoc.SaveAs(pdf_path_abs, FileFormat=17)
    print("PDF export completed successfully!")

    wdoc.Close(False)
    word.Quit()
    print("Microsoft Word automation completed cleanly.")
except Exception as e:
    print(f"Word COM Error: {e}")
    try:
        word.Quit()
    except Exception:
        pass
    sys.exit(1)

print("THESIS COMPILED AND EXPORTED SUCCESSFULLY!")
