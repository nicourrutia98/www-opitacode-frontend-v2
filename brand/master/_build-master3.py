"""Final master: just normalize the viewBox of the optimized potrace output."""
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

# Use viewBox that exactly matches the path extent (with 1px padding for safety)
vb_w = int(max_x - min_x) + 4
vb_h = int(max_y - min_y) + 4
# Center the path: the path starts at (min_x, min_y), viewBox starts at (0, 0)
# So we need to translate the path by (-min_x + 2, -min_y + 2)
tx = 2 - min_x
ty = 2 - min_y

# Build SVG with translate on the path (in-place, no wrapper)
master = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {vb_w} {vb_h}"
     width="{vb_w}" height="{vb_h}"
     role="img"
     aria-label="Opita Code symbol">
  <title>Opita Code - Symbol</title>
  <desc>The Opita Code corporate mark. A 4-lobe ring with a central diamond negative space. The mark represents modular engineering: each lobe interlocks with its neighbors around a governed core.</desc>
  <path fill="#0D0D0D" fill-rule="evenodd" transform="translate({tx:.1f}, {ty:.1f})" d="{path_d}"/>
</svg>
'''

with open('opita-code-symbol.svg', 'w') as f:
    f.write(master)
print(f'Master saved ({len(master)} bytes), viewBox=0 0 {vb_w} {vb_h}, transform=translate({tx:.1f}, {ty:.1f})')

# Render
cairosvg.svg2png(url='opita-code-symbol.svg', write_to='_final-render.png', output_width=512, output_height=512)
img = Image.open('_final-render.png')
bg = Image.new('RGBA', img.size, (255, 0, 0, 255))
bg.paste(img, (0, 0), img)
bg.save('_final-on-red.png')
print('Rendered on red')
