import xml.etree.ElementTree as ET
tree = ET.parse('opita-code-symbol.svg')
root = tree.getroot()
print(f'Root: {root.tag}')
print(f'Attribs: {root.attrib}')
for child in root:
    print(f'  Child: {child.tag} attribs: {child.attrib}')
    for grandchild in child:
        d = grandchild.attrib.get('d', '')
        print(f'    {grandchild.tag} d length: {len(d)}')
