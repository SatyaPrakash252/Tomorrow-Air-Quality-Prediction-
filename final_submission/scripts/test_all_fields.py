import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import win32com.client
import os

doc = docx.Document()

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

p_toc = doc.add_paragraph()
add_field(p_toc, r'TOC \o "1-3" \h \z \u')

p_lof = doc.add_paragraph()
add_field(p_lof, r'TOC \c "Figure" \h \z')

p_lot = doc.add_paragraph()
add_field(p_lot, r'TOC \c "Table" \h \z')

for i in range(1, 3):
    h = doc.add_heading(f'Chapter {i}: Model Architecture {i}', level=1)
    p = doc.add_paragraph(f'This describes the deep autoencoder and health risk index.')
    add_index_entry(p, "Autoencoder")
    add_index_entry(p, "Health Risk Index")
    
    # Add a figure caption
    p_fig = doc.add_paragraph('Figure 1.1: System Pipeline', style='Caption')
    # Add a table caption
    p_tbl = doc.add_paragraph('Table 1.1: Imputation Benchmark', style='Caption')

p_idx = doc.add_paragraph()
add_field(p_idx, r'INDEX \c "2" \z "1033"')

test_docx = os.path.abspath('final_submission/thesis/test_all_fields.docx')
doc.save(test_docx)

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    wdoc = word.Documents.Open(test_docx)
    for f in wdoc.Fields:
        f.Update()
    wdoc.Save()
    print('All fields updated successfully!')
    print('Field count:', wdoc.Fields.Count)
    if wdoc.Indexes.Count > 0:
        print('Index content:', repr(wdoc.Indexes(1).Range.Text[:200]))
    wdoc.Close(False)
finally:
    word.Quit()
