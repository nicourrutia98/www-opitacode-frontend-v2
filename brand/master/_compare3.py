"""
Compare the LEGACY svg render vs the PDF reference vs MY new master.
"""
import cairosvg
from PIL import Image
import numpy as np

# Render the legacy SVG (the one that was working in the .ico)
cairosvg.svg2png(
    url=r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend\assets\img\opita-symbol-light.svg',
    write_to='_legacy-render.png',
    output_width=230,
    output_height=230
)
print('Legacy rendered at 230x230')

# Render my new master
cairosvg.svg2png(
    url='opita-code-symbol.svg',
    write_to='_master-render.png',
    output_width=230,
    output_height=230
)
print('Master rendered at 230x230')

# Render the PDF reference
pdf = Image.open(r'C:\Users\nicou\Documents\IA\discolmeds\REPORT\output\_page1-img2.png').convert('RGBA')
print(f'PDF ref: {pdf.size}')

# Side-by-side
legacy = Image.open('_legacy-render.png').convert('RGBA')
master = Image.open('_master-render.png').convert('RGBA')

# Resize all to same height
target = (230, 230)
legacy_r = legacy.resize(target)
master_r = master.resize(target)
pdf_r = pdf.resize(target)

combined = Image.new('RGBA', (target[0] * 3 + 40, target[1] + 40), (255, 255, 255, 255))
combined.paste(pdf_r, (0, 20))
combined.paste(legacy_r, (target[0] + 20, 20))
combined.paste(master_r, (target[0] * 2 + 40, 20))
combined.save('_compare-3way.png')
print('3-way comparison saved: _compare-3way.png')
print('Left: PDF reference. Middle: Legacy SVG. Right: My master.')
