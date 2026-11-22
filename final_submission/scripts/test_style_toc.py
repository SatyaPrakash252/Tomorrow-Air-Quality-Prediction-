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

p_lof = doc.add_paragraph()
add_field(p_lof, r'TOC \t "Caption" \h \z')

p1 = doc.add_paragraph('Figure 3.1: System Architecture Pipeline', style='Caption')
p2 = doc.add_paragraph('Figure 3.2: Module Call Graph', style='Caption')

test_docx = os.path.abspath('final_submission/thesis/test_style_toc.docx')
doc.save(test_docx)

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
wdoc = word.Documents.Open(test_docx)
for f in wdoc.Fields:
    f.Update()
print('TOC Count:', wdoc.TablesOfContents.Count)
for i in range(1, wdoc.TablesOfContents.Count + 1):
    print(f'TOC {i}:', repr(wdoc.TablesOfContents(i).Range.Text))
wdoc.Save()
wdoc.Close(False)
word.Quit()
