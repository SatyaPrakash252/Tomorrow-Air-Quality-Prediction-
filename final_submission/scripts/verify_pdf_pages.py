import fitz
from pathlib import Path

import sys
sys.stdout.reconfigure(encoding='utf-8')
pdf_path = Path("final_submission/thesis/Project_Report.pdf")
doc = fitz.open(str(pdf_path))
print(f"Total Pages: {len(doc)}")

short_pages = []
for i, page in enumerate(doc):
    text = page.get_text().strip()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_line = lines[0] if lines else 'EMPTY'
    last_line = lines[-1] if lines else 'EMPTY'
    print(f"Page {i+1:02d}: lines={len(lines):02d} | first=\"{first_line[:35]}\" | last=\"{last_line[:35]}\"")
    if len(lines) < 6:
        short_pages.append((i+1, len(lines), first_line))

print("\n--- Summary of Short Pages (< 6 lines) ---")
for sp in short_pages:
    print(f"Page {sp[0]}: {sp[1]} lines -> '{sp[2]}'")
