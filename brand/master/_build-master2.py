"""Use the original optimized SVG, just normalize the viewBox to match path extent."""
import re
import cairosvg
from PIL import Image
from svg.path import parse_path

with open('_master-opt.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path_d = match.group(1)
path = parse_path(path_d)

# Find bbox
min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')
for seg in path:
    try:
        for p in [seg.start, seg.end] + [seg.point(t) for t in [i/20 for i in range(1, 20)]]:
            min_x, min_y = min(min_x, p.real), min(min_y, p.imag)
            max_x, max_y = max(max_x, p.real), max(max_y, p.imag)
    except: pass

w, h = max_x - min_x, max_y - min_y
print(f'Path bbox: ({min_x:.0f}, {min_y:.0f}) to ({max_x:.0f}, {max_y:.0f}) = {w:.0f}x{h:.0f}')

# Use a viewBox that matches the path's actual extent (rounded to clean numbers)
# Use viewBox "0 0 808 814" (slightly larger than path for clean padding)
vb_x = 0
vb_y = 0
vb_w = int(w) + 4
vb_h = int(h) + 4
# Center the path in the viewBox
offset_x = (vb_w - w) / 2 - min_x
offset_y = (vb_h - h) / 2 - min_y
print(f'ViewBox: {vb_x} {vb_y} {vb_w} {vb_h}')
print(f'Offset: ({offset_x:.1f}, {offset_y:.1f})')

# Build the SVG with proper structure
master = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{vb_x} {vb_y} {vb_w} {vb_h}"
     width="{vb_w}" height="{vb_h}"
     role="img"
     aria-label="Opita Code symbol">
  <title>Opita Code - Symbol</title>
  <desc>The Opita Code corporate mark. A 4-lobe ring with a central diamond negative space. The mark represents modular engineering: each lobe interlocks with its neighbors around a governed core.</desc>
  <g transform="translate({offset_x:.2f}, {offset_y:.2f})">
    <path fill="#0D0D0D" fill-rule="evenodd" d="{path_d}"/>
  </g>
</svg>
'''

with open('opita-code-symbol.svg', 'w') as f:
    f.write(master)
print(f'\nMaster saved ({len(master)} bytes)')

# Render to verify
cairosvg.svg2png(url='opita-code-symbol.svg', write_to='_final-render.png', output_width=512, output_height=512)
print('Rendered _final-render.png')

# On red bg
img = Image.open('_final-render.png')
bg = Image.new('RGBA', img.size, (255, 0, 0, 255))
bg.paste(img, (0, 0), img)
bg.save('_final-on-red.png')
print('Rendered _final-on-red.png')
