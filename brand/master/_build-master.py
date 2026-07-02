"""Build the final master SVG with proper metadata, normalized viewBox."""
import re
from svg.path import parse_path
from svg.path.path import Path, Move, CubicBezier, Line, Close

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

# Normalize: shift to origin, scale to 0-512
w = max_x - min_x
h = max_y - min_y
TARGET = 512
scale = TARGET / max(w, h)
tx = -min_x
ty = -min_y
print(f'Original bbox: {w:.1f}x{h:.1f} at ({min_x:.1f}, {min_y:.1f})')
print(f'Transform: translate({tx:.2f}, {ty:.2f}) scale({scale:.4f})')
print(f'Target: 0 0 {TARGET} {TARGET}')

# Rebuild the path d="" string with normalized coordinates
# IMPORTANT: add Z after each subpath (Move = new subpath) for proper evenodd fill
new_d = []
for i, seg in enumerate(path):
    if isinstance(seg, Move):
        nx = (seg.start.real + tx) * scale
        ny = (seg.start.imag + ty) * scale
        # Close previous subpath if this isn't the first
        if i > 0:
            new_d.append('Z')
        new_d.append(f'M{nx:.2f} {ny:.2f}')
    elif isinstance(seg, Close):
        new_d.append('Z')
    elif isinstance(seg, CubicBezier):
        c1 = seg.control1
        c2 = seg.control2
        e = seg.end
        c1x, c1y = (c1.real + tx) * scale, (c1.imag + ty) * scale
        c2x, c2y = (c2.real + tx) * scale, (c2.imag + ty) * scale
        ex, ey = (e.real + tx) * scale, (e.imag + ty) * scale
        new_d.append(f'C{c1x:.2f} {c1y:.2f} {c2x:.2f} {c2y:.2f} {ex:.2f} {ey:.2f}')
    elif isinstance(seg, Line):
        ex = (seg.end.real + tx) * scale
        ey = (seg.end.imag + ty) * scale
        new_d.append(f'L{ex:.2f} {ey:.2f}')

# Close the last subpath
new_d.append('Z')

normalized_d = ' '.join(new_d)
print(f'New d: {len(normalized_d)} bytes, M: {normalized_d.count("M")}, Z: {normalized_d.count("Z")}')

# Build the final master SVG
master = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {TARGET} {TARGET}"
     width="{TARGET}" height="{TARGET}"
     role="img"
     aria-label="Opita Code symbol">
  <title>Opita Code - Symbol</title>
  <desc>The Opita Code corporate mark. A 4-lobe ring with a central diamond negative space. The mark represents modular engineering: each lobe interlocks with its neighbors around a governed core.</desc>
  <path fill="#0D0D0D" fill-rule="evenodd" d="{normalized_d}"/>
</svg>
'''

with open('opita-code-symbol.svg', 'w') as f:
    f.write(master)
print(f'\nMaster saved: opita-code-symbol.svg ({len(master)} bytes)')

# Render to verify
import cairosvg
cairosvg.svg2png(url='opita-code-symbol.svg', write_to='_final-render.png', output_width=512, output_height=512)
print('Rendered _final-render.png')

# Also render on red to show transparency
from PIL import Image
img = Image.open('_final-render.png')
bg = Image.new('RGBA', img.size, (255, 0, 0, 255))
bg.paste(img, (0, 0), img)
bg.save('_final-on-red.png')
print('Rendered _final-on-red.png (red bg)')
