from docx import Document
from pathlib import Path
root=Path(r'C:\Users\Archit\Documents\Codex\2026-10-14\ok\outputs')
for name in ['Tidebound_Project_Report.docx','Tidebound_Technical_Architecture_and_Design.docx','Tidebound_Combined_Project_and_Technical_Document.docx']:
 d=Document(root/name); print('\n'+name)
 for i,p in enumerate(d.paragraphs):
  if any(s in p.text.lower() for s in ['github','super-pirate-world','super pirate world','clear-code','clear code','developer']): print(i, p.text[:180])
 print('metadata:',d.core_properties.title, d.core_properties.author)
