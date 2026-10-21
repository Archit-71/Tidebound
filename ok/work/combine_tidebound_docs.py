from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree
import os
import re
import tempfile

ROOT = Path(r'C:\Users\Archit\Documents\Codex\2026-10-14\ok')
OUT = ROOT / 'outputs'
PROJECT = OUT / 'Tidebound_Project_Report.docx'
TECH = OUT / 'Tidebound_Technical_Architecture_and_Design.docx'
DEST = OUT / 'Tidebound_Combined_Project_and_Technical_Document.docx'

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}
WBR = '{%s}br' % NS['w']
R_EMBED = '{%s}embed' % NS['r']
REL_ID = 'Id'
REL_TYPE = 'Type'
REL_TARGET = 'Target'
IMAGE_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'

def xml_bytes(root):
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

with ZipFile(PROJECT) as pzip, ZipFile(TECH) as tzip:
    p_doc = etree.fromstring(pzip.read('word/document.xml'))
    t_doc = etree.fromstring(tzip.read('word/document.xml'))
    p_body = p_doc.find('w:body', NS)
    t_body = t_doc.find('w:body', NS)

    # Find the page break after the technical cover and retain it, its contents
    # page, and all following technical sections.
    t_children = list(t_body)
    cover_break = next((i for i, el in enumerate(t_children)
                        if el.tag == '{%s}p' % NS['w'] and el.xpath('.//w:br[@w:type="page"]', namespaces=NS)), None)
    if cover_break is None:
        raise RuntimeError('Could not locate the technical document cover-page break.')
    technical_content = [deepcopy(el) for el in t_children[cover_break:] if el.tag != '{%s}sectPr' % NS['w']]

    p_rels = etree.fromstring(pzip.read('word/_rels/document.xml.rels'))
    t_rels = etree.fromstring(tzip.read('word/_rels/document.xml.rels'))
    existing_ids = [int(m.group(1)) for rel in p_rels if (m := re.fullmatch(r'rId(\d+)', rel.get(REL_ID, '')))]
    next_rid = max(existing_ids, default=0) + 1
    p_media = [n for n in pzip.namelist() if n.startswith('word/media/')]
    media_num = max([int(m.group(1)) for n in p_media if (m := re.search(r'image(\d+)', n))] or [0]) + 1

    # Copy only relationships actually referenced in the retained technical body.
    referenced = {node.get(R_EMBED) for el in technical_content for node in el.xpath('.//a:blip[@r:embed]', namespaces=NS)}
    rel_map = {}
    new_files = {}
    for rel in t_rels:
        old_id = rel.get(REL_ID)
        if old_id not in referenced:
            continue
        if rel.get(REL_TYPE) != IMAGE_REL:
            raise RuntimeError('Unexpected referenced relationship in technical body: ' + str(rel.get(REL_TYPE)))
        target = rel.get(REL_TARGET)
        source_path = 'word/' + target.replace('\\', '/')
        suffix = Path(target).suffix or '.png'
        new_target = f'media/image{media_num}{suffix}'
        new_id = f'rId{next_rid}'
        next_rid += 1
        media_num += 1
        rel_map[old_id] = new_id
        new_files['word/' + new_target] = tzip.read(source_path)
        new_rel = etree.SubElement(p_rels, '{%s}Relationship' % NS['rel'])
        new_rel.set(REL_ID, new_id)
        new_rel.set(REL_TYPE, IMAGE_REL)
        new_rel.set(REL_TARGET, new_target)

    for el in technical_content:
        for blip in el.xpath('.//a:blip[@r:embed]', namespaces=NS):
            blip.set(R_EMBED, rel_map[blip.get(R_EMBED)])

    # Avoid duplicate drawing object identifiers in the merged Word body.
    max_docpr = max([int(x.get('id')) for x in p_body.xpath('.//wp:docPr[@id]', namespaces=NS) if x.get('id','').isdigit()] or [0])
    for dp in (x for el in technical_content for x in el.xpath('.//wp:docPr[@id]', namespaces=NS)):
        max_docpr += 1
        dp.set('id', str(max_docpr))

    # Append after the project report and before the package's final section properties.
    sect = p_body.find('w:sectPr', NS)
    insert_at = list(p_body).index(sect) if sect is not None else len(p_body)
    for offset, el in enumerate(technical_content):
        p_body.insert(insert_at + offset, el)

    # Unify running header/footer across the combined volume.
    updates = {
        'word/header1.xml': {'TIDEBOUND  /  TECHNICAL ARCHITECTURE': 'TIDEBOUND  /  PROJECT AND TECHNICAL REPORT'},
        'word/footer1.xml': {'Tidebound Technical Reference': 'Tidebound Project and Technical Report'},
        'docProps/core.xml': {'Tidebound Project Report': 'Tidebound Project and Technical Document'},
    }
    replacements = {'word/document.xml': xml_bytes(p_doc), 'word/_rels/document.xml.rels': xml_bytes(p_rels)}
    for path, mapping in updates.items():
        if path in pzip.namelist():
            raw = pzip.read(path)
            for before, after in mapping.items():
                raw = raw.replace(before.encode('utf-8'), after.encode('utf-8'))
            replacements[path] = raw

    temp = DEST.with_suffix('.tmp.docx')
    with ZipFile(temp, 'w', ZIP_DEFLATED) as zout:
        for item in pzip.infolist():
            zout.writestr(item, replacements.get(item.filename, pzip.read(item.filename)))
        for name, data in new_files.items():
            zout.writestr(name, data)
    os.replace(temp, DEST)

print(DEST)
print('Technical cover omitted; technical contents page and body retained.')
print('Technical diagrams copied:', len(rel_map))
