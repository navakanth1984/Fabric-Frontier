import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def format_screenplay(input_md, output_docx):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Courier New'
    style.font.size = Pt(12)

    with open(input_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue

        # Scene Headings
        if line.startswith('INT.') or line.startswith('EXT.'):
            p = doc.add_paragraph()
            p.add_run(line.upper()).bold = True
            p.paragraph_format.space_before = Pt(12)
        # Transitions
        elif line.endswith(':') and line.isupper():
            p = doc.add_paragraph(line)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        # Character Names (Simplified detection: ALL CAPS and no punctuation)
        elif line.isupper() and not any(c in line for c in ['.', ',', '!', '?']):
            p = doc.add_paragraph(line)
            p.paragraph_format.left_indent = Inches(2.0)
            p.paragraph_format.space_before = Pt(12)
        # Parentheticals
        elif line.startswith('(') and line.endswith(')'):
            p = doc.add_paragraph(line)
            p.paragraph_format.left_indent = Inches(1.5)
        # Dialogue (Assume follows character or paren)
        elif i > 0 and (lines[i-1].strip().isupper() or lines[i-1].strip().startswith('(')):
            p = doc.add_paragraph(line)
            p.paragraph_format.left_indent = Inches(1.0)
            p.paragraph_format.right_indent = Inches(1.0)
        # Action
        else:
            p = doc.add_paragraph(line)
            p.paragraph_format.space_before = Pt(6)

    doc.save(output_docx)
    print(f'Done: {output_docx}')

if __name__ == '__main__':
    format_screenplay('factory_output.md', 'DAAVA_Screenplay_Formatted_V1.docx')
