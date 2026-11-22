#!/usr/bin/env python3
"""
VayuDrishti — Master IQAC Thesis Generator (75 Pages)
Executes the modular compiler in final_submission/scripts/compile_thesis.py.
Produces the comprehensive 75-page Project_Report.docx and exports Project_Report.pdf.
"""

import os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
COMPILE_SCRIPT = ROOT / "final_submission" / "scripts" / "compile_thesis.py"

print("="*60)
print("  EXECUTING MASTER 75-PAGE THESIS COMPILER")
print("="*60)

res = subprocess.run([sys.executable, str(COMPILE_SCRIPT)], check=True)

# Export PDF via Word COM if available
try:
    import win32com.client
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    doc_path = str((ROOT / "final_submission" / "thesis" / "Project_Report.docx").resolve())
    pdf_path = str((ROOT / "final_submission" / "thesis" / "Project_Report.pdf").resolve())
    print(f"Exporting PDF via Word COM: {pdf_path}")
    doc = word.Documents.Open(doc_path)
    pages = doc.ComputeStatistics(2)
    words = doc.ComputeStatistics(0)
    doc.SaveAs(pdf_path, FileFormat=17) # wdFormatPDF = 17
    doc.Close()
    word.Quit()
    print("="*60)
    print(f"  THESIS COMPILED & EXPORTED SUCCESSFULLY!")
    print(f"  Pages: {pages}")
    print(f"  Words: {words}")
    print(f"  Word Doc: {doc_path}")
    print(f"  PDF Doc:  {pdf_path}")
    print("="*60)
except Exception as e:
    print(f"Word COM PDF export notice: {e}")
