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

p_lof1 = doc.add_paragraph()
add_field(p_lof1, r'TOC \c "Figure" \h \z')

p_lot1 = doc.add_paragraph()
add_field(p_lot1, r'TOC \c "Table" \h \z')

p_cap1 = doc.add_paragraph(style='Caption')
p_cap1.add_run('Figure ')
add_field(p_cap1, r'SEQ Figure \* ARABIC')
p_cap1.add_run(': System Architecture Pipeline')

p_cap2 = doc.add_paragraph(style='Caption')
p_cap2.add_run('Figure ')
add_field(p_cap2, r'SEQ Figure \* ARABIC')
p_cap2.add_run(': Data Flow Diagram')

p_tbl1 = doc.add_paragraph(style='Caption')
p_tbl1.add_run('Table ')
add_field(p_tbl1, r'SEQ Table \* ARABIC')
p_tbl1.add_run(': Model Ablation Results')

test_docx = os.path.abspath('final_submission/thesis/test_seq.docx')
doc.save(test_docx)

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
wdoc = word.Documents.Open(test_docx)
for f in wdoc.Fields:
    f.Update()
print('TablesOfFigures Count:', wdoc.TablesOfFigures.Count)
for i in range(1, wdoc.TablesOfFigures.Count + 1):
    print(f'TOF {i}:', repr(wdoc.TablesOfFigures(i).Range.Text))
wdoc.Save()
wdoc.Close(False)
word.Quit()
