import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import win32com.client
import os

doc = docx.Document()
p = doc.add_paragraph()
r = p.add_run()

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

add_field(p, r'TOC \o "1-3" \h \z \u')

for i in range(1, 4):
    doc.add_heading(f'Chapter {i}: Introduction to System {i}', level=1)
    p_body = doc.add_paragraph(f'This is content for chapter {i}.')

test_docx = os.path.abspath('final_submission/thesis/test_toc.docx')
doc.save(test_docx)

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
try:
    wdoc = word.Documents.Open(test_docx)
    for f in wdoc.Fields:
        f.Update()
    wdoc.Save()
    print('TOC updated successfully!')
    print('Field count:', wdoc.Fields.Count)
    if wdoc.TablesOfContents.Count > 0:
        print('TOC items:', repr(wdoc.TablesOfContents(1).Range.Text[:200]))
    wdoc.Close(False)
finally:
    word.Quit()
