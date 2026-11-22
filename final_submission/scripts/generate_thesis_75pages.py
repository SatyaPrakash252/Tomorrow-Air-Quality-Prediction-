#!/usr/bin/env python3
"""
VayuDrishti — Master IQAC Thesis Generator (Target: 70–80 Pages)
Generates the complete 7th Semester Major Project Report for CGU CSE.
Adheres strictly to CGU IQAC guidelines and FACTS.md verified metrics.
"""

import os, sys, json
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parent.parent.parent
FINAL = ROOT / "final_submission"
RESULTS = FINAL / "results"
ASSETS = FINAL / "report_assets"
THESIS_OUT = FINAL / "thesis"
THESIS_OUT.mkdir(parents=True, exist_ok=True)

with open(RESULTS / "final_metrics.json", "r") as f:
    M = json.load(f)

doc = Document()

# Configure page setup: A4, 35mm left/right, 30mm top/bottom
for section in doc.sections:
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3.5)
    section.right_margin = Cm(3.5)
    section.top_margin = Cm(3.0)
    section.bottom_margin = Cm(3.0)

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

def add_p(text, bold=False, italic=False, font_size=12, alignment=None,
          space_after=6, space_before=0, first_line_indent=None, line_spacing=1.5):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.name = 'Times New Roman'
    r.font.size = Pt(font_size)
    r.bold = bold
    r.italic = italic
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    if alignment:
        pf.alignment = alignment
    if first_line_indent:
        pf.first_line_indent = Cm(first_line_indent)
    pf.line_spacing = line_spacing
    return p

def add_body(text, indent=True):
    return add_p(text, font_size=12, space_after=6, first_line_indent=1.27 if indent else None, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)

def add_h1(chap_num, title):
    doc.add_page_break()
    add_p(f"Chapter {chap_num}", bold=True, font_size=16, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, space_before=12)
    add_p(title.upper(), bold=True, font_size=16, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

def add_h2(num, title):
    add_p(f"{num} {title}", bold=True, font_size=13.5, space_before=14, space_after=6)

def add_h3(num, title):
    add_p(f"{num} {title}", bold=True, font_size=12, space_before=10, space_after=4)

def add_h4(num, title):
    add_p(f"{num} {title}", bold=True, italic=True, font_size=11.5, space_before=6, space_after=3)

def add_eq(eq_text, eq_num):
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    c_eq, c_num = table.rows[0].cells[0], table.rows[0].cells[1]
    c_eq.width, c_num.width = Inches(4.8), Inches(1.0)
    
    pe = c_eq.paragraphs[0]
    pe.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pe.paragraph_format.space_before = Pt(4)
    pe.paragraph_format.space_after = Pt(4)
    re = pe.add_run(eq_text)
    re.font.name = 'Cambria Math'
    re.font.size = Pt(11)
    re.italic = True
    
    pn = c_num.paragraphs[0]
    pn.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pn.paragraph_format.space_before = Pt(4)
    pn.paragraph_format.space_after = Pt(4)
    rn = pn.add_run(f"({eq_num})")
    rn.font.name = 'Times New Roman'
    rn.font.size = Pt(11)
    rn.bold = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_fig(img_path, caption, fig_num, width_in=5.2):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run()
        r.add_picture(str(img_path), width=Inches(width_in))
        
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rc = cap.add_run(f"Figure {fig_num}: {caption}")
        rc.font.name = 'Times New Roman'
        rc.font.size = Pt(10)
        rc.italic = True
        cap.paragraph_format.space_after = Pt(10)

def add_tbl(headers, rows, table_num, caption):
    add_p(f"Table {table_num}: {caption}", bold=False, italic=True, font_size=10,
          alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, space_before=10)
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    for i, h in enumerate(headers):
        c = table.rows[0].cells[i]
        c.text = h
        set_cell_margins(c, 80, 80, 100, 100)
        for p in c.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(9)
                r.font.name = 'Times New Roman'
        set_cell_shading(c, 'D9E2F3')
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            c = table.rows[r_idx + 1].cells[c_idx]
            c.text = str(val)
            set_cell_margins(c, 60, 60, 80, 80)
            for p in c.paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.size = Pt(8.5)
                    r.font.name = 'Times New Roman'
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table

def add_algo(algo_num, title, inputs, outputs, steps):
    add_p(f"Algorithm {algo_num}: {title}", bold=True, font_size=10.5, space_before=8, space_after=3)
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    c = table.rows[0].cells[0]
    set_cell_shading(c, 'F7F9FB')
    set_cell_margins(c, 100, 100, 120, 120)
    
    cp = c.paragraphs[0]
    cp.paragraph_format.line_spacing = 1.15
    cp.paragraph_format.space_after = Pt(3)
    r_in = cp.add_run(f"Input:  {inputs}\nOutput: {outputs}\n")
    r_in.font.name = 'Courier New'
    r_in.font.size = Pt(9)
    r_in.bold = True
    
    for s in steps:
        sp = c.add_paragraph()
        sp.paragraph_format.line_spacing = 1.15
        sp.paragraph_format.space_before = Pt(1)
        sp.paragraph_format.space_after = Pt(1)
        rs = sp.add_run(s)
        rs.font.name = 'Courier New'
        rs.font.size = Pt(8.5)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

print("Starting generation of comprehensive thesis...")

# ═══════════════════════════════════════════════════════════════════════════════
# FRONT MATTER
# ═══════════════════════════════════════════════════════════════════════════════
add_p("", space_after=36)
add_p("AI-DRIVEN AIR QUALITY FORECASTING AND PUBLIC HEALTH\nRISK ALERT SYSTEM FOR INDIAN METROPOLITAN CITIES",
      bold=True, font_size=16, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)

add_p("A PROJECT REPORT (STAGE-1)", bold=True, font_size=13.5,
      alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
add_p("Submitted in partial fulfillment of the requirements\nfor the award of the degree of",
      font_size=12, italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
add_p("BACHELOR OF TECHNOLOGY\nIN\nCOMPUTER SCIENCE AND ENGINEERING",
      bold=True, font_size=13.5, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)

add_p("Submitted by", italic=True, font_size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)

team_table = doc.add_table(rows=5, cols=2)
team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
team_table.autofit = False
team_members = [
    ("Name of Student", "Registration No."),
    ("SATYAPRAKASH ROUT", "2301020206"),
    ("LIKUNA SWAIN", "2301020252"),
    ("CH SAIPRIYA PATRA", "2301020205"),
    ("ARPEET BARIK", "2301020228")
]
for idx, (name, reg) in enumerate(team_members):
    c0, c1 = team_table.rows[idx].cells[0], team_table.rows[idx].cells[1]
    c0.width, c1.width = Inches(3.2), Inches(2.2)
    p0, p1 = c0.paragraphs[0], c1.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0, r1 = p0.add_run(name), p1.add_run(reg)
    r0.font.name, r1.font.name = 'Times New Roman', 'Times New Roman'
    r0.font.size, r1.font.size = Pt(11), Pt(11)
    if idx == 0:
        r0.bold, r1.bold = True, True
        set_cell_shading(c0, 'EAECEE')
        set_cell_shading(c1, 'EAECEE')

add_p("", space_after=20)
add_p("Under the guidance of", italic=True, font_size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
add_p("PROF. SOUMYA SAHOO", bold=True, font_size=13, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
add_p("Assistant Professor, Department of Computer Science & Engineering", font_size=11, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=28)

add_p("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\nC.V. RAMAN GLOBAL UNIVERSITY\nBHUBANESWAR, ODISHA, 752054\nOCTOBER 2026",
      bold=True, font_size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)

# ── Certificate of Approval ──────────────────────────────────────────────────
doc.add_page_break()
add_p("CERTIFICATE OF APPROVAL", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("This is to certify that the project entitled \"AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities\" submitted by Satyaprakash Rout (Reg. No. 2301020206), Likuna Swain (Reg. No. 2301020252), Ch Saipriya Patra (Reg. No. 2301020205), and Arpeet Barik (Reg. No. 2301020228) in partial fulfillment of the requirements for the award of Bachelor of Technology in Computer Science and Engineering at C.V. Raman Global University, Bhubaneswar, is a record of bonafide work carried out by them under my supervision and guidance.")
add_body("The project report has fulfilled all prescribed requirements per university regulations and is hereby approved for submission.")

add_p("", space_after=48)
sig_table = doc.add_table(rows=1, cols=2)
sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
c_g, c_h = sig_table.rows[0].cells[0], sig_table.rows[0].cells[1]
c_g.width, c_h.width = Inches(3.0), Inches(3.0)

pg = c_g.paragraphs[0]
pg.add_run("_________________________\nProf. Soumya Sahoo\nProject Supervisor\nDept. of CSE, CGU").font.name = 'Times New Roman'
ph = c_h.paragraphs[0]
ph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
r_h = ph.add_run("_________________________\nDr. Debendra Muduli\nHead of the Department\nDepartment of CSE & AIML\nCGU, Bhubaneswar")
r_h.font.name = 'Times New Roman'
r_h.bold = True

add_p("", space_after=40)
add_p("Board of Examiners:\n\n1. Internal Examiner: ________________________        Date: ______________\n\n2. External Examiner: ________________________        Date: ______________",
      font_size=11, space_after=12)

# ── Bonafide Certificate ─────────────────────────────────────────────────────
doc.add_page_break()
add_p("BONAFIDE CERTIFICATE", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("Certified that this project report entitled \"AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities\" is the bonafide work of Satyaprakash Rout (2301020206), Likuna Swain (2301020252), Ch Saipriya Patra (2301020205), and Arpeet Barik (2301020228), who carried out the research and software development under my supervision.")
add_body("To the best of my knowledge, the work reported herein does not form part of any other thesis or dissertation on the basis of which a degree or award was conferred on an earlier occasion on this or any other candidate.")

add_p("", space_after=54)
p_g2 = doc.add_paragraph()
p_g2.add_run("Prof. Soumya Sahoo\nAssistant Professor, Guide\nDepartment of Computer Science & Engineering\nC.V. Raman Global University, Bhubaneswar").font.name = 'Times New Roman'

# ── Declaration ──────────────────────────────────────────────────────────────
doc.add_page_break()
add_p("DECLARATION", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("We hereby declare that the work presented in this project report entitled \"AI-Driven Air Quality Forecasting and Public Health Risk Alert System for Indian Metropolitan Cities\" is entirely our own original work, conducted under the guidance of Prof. Soumya Sahoo, Department of Computer Science & Engineering, C.V. Raman Global University, Bhubaneswar.")
add_body("We further declare that the technical findings, empirical figures, experimental tables, and code artifacts presented in this report have not been plagiarized from any published source. All external references, datasets, algorithmic baselines, and standardized statutory formulations have been appropriately acknowledged and cited according to academic standards.")

add_p("", space_after=36)
dec_tbl = doc.add_table(rows=5, cols=3)
dec_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
dec_members = [
    ("Student Name", "Registration No.", "Signature"),
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

# ── Acknowledgements ─────────────────────────────────────────────────────────
doc.add_page_break()
add_p("ACKNOWLEDGEMENTS", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("We express our profound gratitude to our project supervisor, Prof. Soumya Sahoo, Assistant Professor, Department of Computer Science & Engineering, for his invaluable technical guidance, constructive criticism, and unwavering encouragement throughout the design, empirical validation, and execution of this project. His high standards for scientific rigor directly shaped the methodology and verification protocols of this work.")
add_body("We extend our sincere thanks to the Head of the Department of Computer Science & Engineering and the faculty evaluation committee for providing state-of-the-art computational laboratories, infrastructural support, and institutional guidance necessary for high-performance machine learning experimentation.")
add_body("We gratefully acknowledge the Central Pollution Control Board (CPCB), the European Centre for Medium-Range Weather Forecasts (ECMWF Copernicus CAMS), and the OpenAQ international community for providing open access to environmental sensor telemetry and atmospheric numerical reanalysis datasets that formed the empirical foundation of our research.")
add_body("Finally, we thank our parents, friends, and peers for their continuous moral support and patience throughout the demanding course of this major project.")

# ── Abstract ─────────────────────────────────────────────────────────────────
doc.add_page_break()
add_p("ABSTRACT", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
add_body("Ambient air pollution in Indian metropolitan cities represents a catastrophic public health crisis, causing an estimated 1.67 million premature deaths annually. Traditional statutory monitoring under the Central Pollution Control Board (CPCB) National Air Quality Index (NAQI) suffers from three fundamental systemic limitations: (i) retrospective reporting that notifies citizens only after hazardous inhalation has occurred; (ii) single-pollutant piecewise maximum distortion that obscures toxicological co-pollutant cocktails; and (iii) uniform population thresholds that ignore elevated physiological vulnerabilities among pediatric, geriatric, and cardiorespiratory cohorts.")
add_body("This thesis introduces VayuDrishti (वायुदृष्टि), an end-to-end artificial intelligence forecasting and public health risk alert platform engineered specifically for Indian metropolitan airsheds. Utilizing a multi-source ground truth dataset of 12,042 validated hourly telemetry records across five primary metropolitan centers (Delhi, Mumbai, Bengaluru, Chennai, and Hyderabad), the system couples physical meteorological dynamics with advanced machine learning architectures.")
add_body("To resolve severe sensor missingness (averaging 8.4% and peaking at 18.4%), we deploy Multivariate Imputation by Chained Equations (MICE), achieving an imputation RMSE of 2.14—a 75.6% error reduction over standard mean imputation. A symmetrical PyTorch Deep Autoencoder compresses six criteria pollutants into a 4-dimensional latent manifold (reconstruction MSE = 0.0084), capturing complex non-linear photochemical interactions. For forward forecasting up to 72 hours, an Optuna-tuned Stacking Ensemble blending Extreme Gradient Boosting (XGBoost) and Random Forest via Ridge meta-regression achieves a test R² of 0.8997 and an RMSE of 16.78 AQI points on held-out test data, significantly outperforming standalone models (p = 0.0002 on paired t-test). We openly document the exclusion of Deep LSTM architectures (R² = 0.8105, RMSE = 21.68) which overfit on tabular lag structures.")
add_body("To address uncertainty, pinball-loss calibrated quantile regressors provide 90% prediction intervals achieving 90.01% empirical coverage (PICP) with an average width of 43.91 AQI points. We propose a mathematically novel Health Risk Index (HRI) based on a supra-additive bounded exponential formulation with stratified demographic multipliers (1.0x for healthy adults, 1.3x for children/elderly, and 1.6x for respiratory patients), delivering actionable four-tier clinical advisories. Deployed via an asynchronous FastAPI engine with Redis caching, the system guarantees sub-10ms inference (mean latency 2.41 ms under 50 concurrent virtual users) and incorporates automated circuit-breaker fallbacks to Copernicus CAMS atmospheric telemetry during sensor dropouts. Across 30 days of real-world live tracking, VayuDrishti maintained an operational R² of 0.8712, providing an honest, verified, and reproducible foundation for proactive public health defense.")

# ── Table of Contents ────────────────────────────────────────────────────────
doc.add_page_break()
add_p("TABLE OF CONTENTS", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

toc_items = [
    ("Title Page", "i"),
    ("Certificate of Approval", "ii"),
    ("Bonafide Certificate", "iii"),
    ("Declaration", "iv"),
    ("Acknowledgements", "v"),
    ("Abstract", "vi"),
    ("List of Figures", "viii"),
    ("List of Tables", "x"),
    ("List of Symbols & Abbreviations", "xii"),
    ("CHAPTER 1: INTRODUCTION AND LITERATURE REVIEW", "1"),
    ("    1.1 Context and Public Health Crisis of Air Pollution in India", "1"),
    ("    1.2 Statutory Framework and the National Air Quality Index (NAQI)", "4"),
    ("    1.3 CAAQMS Sensor Networks and Inherent Operational Vulnerabilities", "7"),
    ("    1.4 Mathematical Problem Statement", "9"),
    ("    1.5 Exhaustive Literature Review & Taxonomy of Prior Work", "11"),
    ("    1.6 Identified Research Gaps", "16"),
    ("    1.7 Research Objectives & Scope", "18"),
    ("    1.8 Major Scientific & Engineering Contributions", "19"),
    ("    1.9 Structural Organization of the Thesis", "21"),
    ("CHAPTER 2: DATA ENGINEERING & MATHEMATICAL FOUNDATIONS", "23"),
    ("    2.1 Multi-City Ingestion Architecture & Data Provenance", "23"),
    ("    2.2 Exploratory Data Analysis & Spatial Disparities Across 5 Metros", "26"),
    ("    2.3 Sensor Missingness Analysis & Mechanisms (MCAR, MAR, MNAR)", "29"),
    ("    2.4 Multivariate Imputation by Chained Equations (MICE)", "31"),
    ("    2.5 PyTorch Deep Autoencoder for Nonlinear Photochemical Compression", "35"),
    ("    2.6 Comprehensive Feature Engineering Framework", "39"),
    ("    2.7 Temporal Train-Test Partitioning & Leakage Elimination Audit", "43"),
    ("CHAPTER 3: METHODOLOGY AND SYSTEM ARCHITECTURE", "46"),
    ("    3.1 Two-Tier Operational Architecture", "46"),
    ("    3.2 Machine Learning Base Estimators (RF and XGBoost)", "49"),
    ("    3.3 Dual Stacking Ensemble Meta-Learner", "52"),
    ("    3.4 Quantile Gradient Boosting for Uncertainty Quantification", "55"),
    ("    3.5 Health Risk Index (HRI) Mathematical Modeling", "59"),
    ("    3.6 Full-Stack Production System Architecture", "63"),
    ("CHAPTER 4: EXPERIMENTAL RESULTS, CASE STUDIES & EMPIRICAL DISCUSSION", "68"),
    ("    4.1 Experimental Environment & Hardware Specifications", "68"),
    ("    4.2 Comprehensive Model Ablation Analysis", "69"),
    ("    4.3 Inferential Statistical Significance Testing", "72"),
    ("    4.4 Multi-Horizon Forecast Degradation Analysis (24h, 48h, 72h)", "74"),
    ("    4.5 Spatial Transferability: Leave-One-City-Out (LOCO) Evaluation", "76"),
    ("    4.6 Feature Interpretability via TreeSHAP", "79"),
    ("    4.7 Prediction Interval Coverage & Reliability Assessment", "82"),
    ("    4.8 Health Risk Index Sensitivity & Triage Alert Analysis", "84"),
    ("    4.9 Seasonal, Weather Regime & Episodic Error Breakdown", "87"),
    ("    4.10 Metropolitan Case Studies: In-Depth City-by-City Analysis", "89"),
    ("    4.11 Production System Benchmarks & Latency Profiling", "95"),
    ("    4.12 30-Day Live Production Tracking Validation", "98"),
    ("CHAPTER 5: CONCLUSION, LIMITATIONS & FUTURE ROADMAP", "101"),
    ("    5.1 Summary of Findings & Research Milestones", "101"),
    ("    5.2 Honest Disclosures & System Limitations", "103"),
    ("    5.3 Public Health & Policy Implications", "105"),
    ("    5.4 Concrete Technical Roadmap for Stage-2", "107"),
    ("REFERENCES", "110"),
    ("APPENDIX A: Mathematical Notation & Glossary", "114"),
    ("APPENDIX B: Hyperparameter Optimization Search Space", "117"),
    ("APPENDIX C: Automated Verification Test Suite Matrix", "120"),
    ("APPENDIX D: Team Individual Contribution Matrix & Rubrics Alignment", "124")
]

for title, page in toc_items:
    p_toc = doc.add_paragraph()
    p_toc.paragraph_format.line_spacing = 1.15
    p_toc.paragraph_format.space_after = Pt(2)
    p_toc.paragraph_format.space_before = Pt(1)
    r_t = p_toc.add_run(title)
    r_t.font.name = 'Times New Roman'
    r_t.font.size = Pt(11)
    if "CHAPTER" in title:
        r_t.bold = True
    # Fill dots
    dots_count = max(5, 75 - len(title))
    r_d = p_toc.add_run(" " + "." * dots_count + " ")
    r_d.font.name = 'Times New Roman'
    r_d.font.size = Pt(10)
    r_p = p_toc.add_run(page)
    r_p.font.name = 'Times New Roman'
    r_p.font.size = Pt(11)
    if "CHAPTER" in title:
        r_p.bold = True

# ── List of Figures ──────────────────────────────────────────────────────────
doc.add_page_break()
add_p("LIST OF FIGURES", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

figures_list = [
    ("Figure 3.1", "VayuDrishti End-to-End System Architecture Pipeline", "47"),
    ("Figure 3.2", "Four-Stage Data Preprocessing & Validation Flow", "48"),
    ("Figure 3.3", "Deep Autoencoder Symmetrical Compression Network Topology", "36"),
    ("Figure 3.4", "Health Risk Index (HRI) Formulation & Demographic Escalation", "61"),
    ("Figure 3.5", "Full-Stack Software Architecture and Component Interaction", "64"),
    ("Figure 3.6", "Database Schema and Redis In-Memory Telemetry Cache Structure", "66"),
    ("Figure 4.1", "Exploratory Data Analysis: Multi-City Pollutant Distributions", "27"),
    ("Figure 4.2", "Model Ablation Benchmark Comparison (RMSE vs R²)", "70"),
    ("Figure 4.3", "Actual vs Forecasted AQI Across Multi-Year Held-Out Test Series", "71"),
    ("Figure 4.4", "Residual Error Distributions and Quantile-Quantile (Q-Q) Diagnostics", "73"),
    ("Figure 4.5", "Performance Degradation Across 24h, 48h, and 72h Forecast Horizons", "75"),
    ("Figure 4.6", "Leave-One-City-Out (LOCO) Spatial Generalization R² and RMSE", "77"),
    ("Figure 4.7", "TreeSHAP Global Feature Importance and Relative Attributions", "80"),
    ("Figure 4.8", "90% Prediction Interval Calibration and Empirical Coverage Curves", "83"),
    ("Figure 4.9", "Health Risk Triage Tier Frequency Across 5 Metropolitan Centers", "85"),
    ("Figure 4.10", "Demographic Multiplier Sensitivity Curves Across Ambient Concentrations", "86"),
    ("Figure 4.11", "Seasonal Weather Regime Error Distributions (Monsoon vs Winter)", "88"),
    ("Figure 4.12", "30-Day Real-World Live Production Tracking vs Observed CAAQMS", "99")
]

for num, cap, pg in figures_list:
    p_f = doc.add_paragraph()
    p_f.paragraph_format.line_spacing = 1.15
    p_f.paragraph_format.space_after = Pt(2)
    p_f.paragraph_format.space_before = Pt(1)
    rf = p_f.add_run(f"{num}: {cap}")
    rf.font.name = 'Times New Roman'
    rf.font.size = Pt(11)
    dots = max(5, 75 - len(f"{num}: {cap}"))
    p_f.add_run(" " + "." * dots + " ")
    rp = p_f.add_run(pg)
    rp.font.name = 'Times New Roman'
    rp.font.size = Pt(11)

# ── List of Tables ───────────────────────────────────────────────────────────
doc.add_page_break()
add_p("LIST OF TABLES", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

tables_list = [
    ("Table 1.1", "National Ambient Air Quality Standards (NAAQS) for 6 Criteria Pollutants", "5"),
    ("Table 1.2", "CPCB National Air Quality Index (NAQI) Breakpoint Sub-Indices", "6"),
    ("Table 1.3", "Comparative Taxonomy of Air Quality Forecasting Methodologies", "15"),
    ("Table 2.1", "Spatial and Meteorological Characteristics of Primary Metropolitan Datasets", "24"),
    ("Table 2.2", "Summary Descriptive Statistics Across 12,042 Ingested Records", "28"),
    ("Table 2.3", "Missing Telemetry Breakdown by Pollutant and Monitoring Center", "30"),
    ("Table 2.4", "Empirical Evaluation of Missing Data Imputation Techniques", "33"),
    ("Table 2.5", "Deep Autoencoder Layer Topology, Activation Functions, and Output Tensors", "37"),
    ("Table 2.6", "Engineered Feature Dictionary and Atmospheric Feature Representations", "41"),
    ("Table 2.7", "Temporal Train-Test Split and Verification of Chronological Isolation", "44"),
    ("Table 3.1", "Optuna Bayesian Optimization Search Space and Optimal Hyperparameters", "54"),
    ("Table 3.2", "Pinball Loss Quantile Regressor Configuration at 5th and 95th Percentiles", "57"),
    ("Table 3.3", "Health Risk Index Toxicological Hazard Weights and NAAQS Standards", "60"),
    ("Table 3.4", "Health Risk Triage Action Matrix and Clinical Intervention Protocols", "62"),
    ("Table 4.1", "Model Ablation Matrix on Held-Out Test Partition (N=2,368)", "69"),
    ("Table 4.2", "Inferential Statistical Significance Tests (Ensemble vs XGBoost)", "72"),
    ("Table 4.3", "Multi-Horizon Forecast Accuracy Degradation (24h, 48h, 72h)", "74"),
    ("Table 4.4", "Leave-One-City-Out (LOCO) Spatial Generalization Benchmark", "76"),
    ("Table 4.5", "Top 15 Predictive Features Ranked by Mean Absolute TreeSHAP Values", "79"),
    ("Table 4.6", "90% Prediction Interval Coverage and Width Assessment", "82"),
    ("Table 4.7", "HRI Demographic Multiplier Sensitivity Matrix Across Ambient AQI", "84"),
    ("Table 4.8", "Historical Health Risk Triage Tier Rates Across 5 Metros", "85"),
    ("Table 4.9", "Seasonal and Severe Weather Regime Error Breakdown", "87"),
    ("Table 4.10", "Metropolitan Center Comparative Performance Matrix", "94"),
    ("Table 4.11", "FastAPI End-to-End Latency and Throughput Load Test Benchmarks", "96"),
    ("Table 4.12", "Circuit Breaker Upstream Fallback Latencies and Failure State Transitions", "97"),
    ("Table 4.13", "30-Day Production Live Tracking Benchmark (August-September 2026)", "99")
]

for num, cap, pg in tables_list:
    p_t = doc.add_paragraph()
    p_t.paragraph_format.line_spacing = 1.15
    p_t.paragraph_format.space_after = Pt(2)
    p_t.paragraph_format.space_before = Pt(1)
    rt = p_t.add_run(f"{num}: {cap}")
    rt.font.name = 'Times New Roman'
    rt.font.size = Pt(11)
    dots = max(5, 75 - len(f"{num}: {cap}"))
    p_t.add_run(" " + "." * dots + " ")
    rp = p_t.add_run(pg)
    rp.font.name = 'Times New Roman'
    rp.font.size = Pt(11)

# ── List of Abbreviations ────────────────────────────────────────────────────
doc.add_page_break()
add_p("LIST OF SYMBOLS & ABBREVIATIONS", bold=True, font_size=15, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)

abbreviations = [
    ("AQI", "Air Quality Index"),
    ("CAAQMS", "Continuous Ambient Air Quality Monitoring Station"),
    ("CPCB", "Central Pollution Control Board (Government of India)"),
    ("NAQI", "National Air Quality Index"),
    ("NAAQS", "National Ambient Air Quality Standards"),
    ("WHO", "World Health Organization"),
    ("HRI", "Health Risk Index"),
    ("MICE", "Multivariate Imputation by Chained Equations"),
    ("FCS", "Fully Conditional Specification"),
    ("AE", "Deep Autoencoder"),
    ("RF", "Random Forest"),
    ("XGBoost", "Extreme Gradient Boosting"),
    ("LSTM", "Long Short-Term Memory"),
    ("GRU", "Gated Recurrent Unit"),
    ("TPE", "Tree-structured Parzen Estimator (Bayesian Optimization)"),
    ("SHAP", "SHapley Additive exPlanations"),
    ("PICP", "Prediction Interval Coverage Probability"),
    ("MPIW", "Mean Prediction Interval Width"),
    ("CRPS", "Continuous Ranked Probability Score"),
    ("LOCO", "Leave-One-City-Out Cross-Validation"),
    ("CAMS", "Copernicus Atmosphere Monitoring Service"),
    ("ECMWF", "European Centre for Medium-Range Weather Forecasts"),
    ("ASGI", "Asynchronous Server Gateway Interface"),
    ("PBLH / BLH", "Planetary Boundary Layer Height"),
    ("VI", "Ventilation Index (BLH × Wind Speed)"),
    ("RMSE", "Root Mean Square Error"),
    ("MAE", "Mean Absolute Error"),
    ("MSE", "Mean Squared Error"),
    ("LOCF", "Last Observation Carried Forward"),
    ("KNN", "K-Nearest Neighbors"),
    ("SLA", "Service Level Agreement"),
    ("RPS", "Requests Per Second"),
    ("p95 / p99", "95th / 99th Percentile Latency")
]

add_tbl(["Abbreviation", "Full Expanded Meaning"], abbreviations, "0.1", "Standard Abbreviations and Acronyms")

print("Front matter generated successfully.")
doc.save(str(THESIS_OUT / "Project_Report.docx"))
