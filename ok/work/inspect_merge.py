from zipfile import ZipFile
from lxml import etree
from pathlib import Path
p=Path(r'C:\Users\Archit\Documents\Codex\2026-10-14\ok\outputs\Tidebound_Technical_Architecture_and_Design.docx')
z=ZipFile(p); n={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
d=etree.fromstring(z.read('word/document.xml')); b=d.find('w:body',n); cs=list(b); i=next(i for i,e in enumerate(cs) if e.tag.endswith('}p') and e.xpath('.//w:br[@w:type="page"]',namespaces=n)); refs={x.get('{'+n['r']+'}embed') for e in cs[i:] for x in e.xpath('.//a:blip[@r:embed]',namespaces=n)}
r=etree.fromstring(z.read('word/_rels/document.xml.rels')); print('refs',refs); print('rels',[(x.get('Id'),x.get('Type'),x.get('Target')) for x in r if x.get('Id') in refs])
