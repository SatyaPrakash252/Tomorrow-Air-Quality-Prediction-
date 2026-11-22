import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import win32com.client
import os

doc = docx.Document()

# Ensure styles exist
styles = doc.styles
try:
    fig_style = styles.add_style('FigureCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    fig_style.base_style = styles['Normal']
except Exception:
    fig_style = styles['FigureCaption']

try:
    tbl_style = styles.add_style('TableCaption', docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    tbl_style.base_style = styles['Normal']
except Exception:
    tbl_style = styles['TableCaption']

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

p_toc = doc.add_paragraph()
add_field(p_toc, r'TOC \o "1-3" \h \z \u')

p_lof = doc.add_paragraph()
add_field(p_lof, r'TOC \t "FigureCaption" \h \z')

p_lot = doc.add_paragraph()
add_field(p_lot, r'TOC \t "TableCaption" \h \z')

# Add content
doc.add_page_break()
doc.add_heading('Chapter 1: Introduction', level=1)
doc.add_heading('1.1 Background Context', level=2)

p_fig = doc.add_paragraph('Figure 1.1: System Architecture Overview', style='FigureCaption')
p_tbl = doc.add_paragraph('Table 1.1: NAAQS Statutory Standards', style='TableCaption')

doc.add_page_break()
doc.add_heading('Chapter 2: Methodology', level=1)
p_fig2 = doc.add_paragraph('Figure 2.1: Data Preprocessing Flow', style='FigureCaption')

test_docx = os.path.abspath('final_submission/thesis/test_custom_styles.docx')
doc.save(test_docx)

word = win32com.client.Dispatch('Word.Application')
word.Visible = False
wdoc = word.Documents.Open(test_docx)
for f in wdoc.Fields:
    f.Update()
print('TOC Count:', wdoc.TablesOfContents.Count)
for i in range(1, wdoc.TablesOfContents.Count + 1):
    print(f'TOC {i} (len={len(wdoc.TablesOfContents(i).Range.Text)}):')
    print(repr(wdoc.TablesOfContents(i).Range.Text))
wdoc.Save()
wdoc.Close(False)
word.Quit()
