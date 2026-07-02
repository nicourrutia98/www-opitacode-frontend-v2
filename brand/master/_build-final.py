"""Final master: clean version of the raw potrace output."""
import re
import cairosvg
from PIL import Image
from svg.path import parse_path

# Read the raw potrace output
with open('_traced-raw.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path_d = match.group(1)
path = parse_path(path_d)

# Find bbox (in potrace's coordinate system, where Y is inverted)
min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')
for seg in path:
    try:
        for p in [seg.start, seg.end] + [seg.point(t) for t in [i/20 for i in range(1, 20)]]:
            min_x, min_y = min(min_x, p.real), min(min_y, p.imag)
            max_x, max_y = max(max_x, p.real), max(max_y, p.imag)
    except: pass
print(f'Path bbox (potrace coords): ({min_x:.0f}, {min_y:.0f}) to ({max_x:.0f}, {max_y:.0f})')

# The transform is translate(0, 1024) scale(1, -1)
# In the viewBox 0 0 1024 1024, a point (x, y) in path becomes (x, 1024 - y)
# So the visible bbox in the viewBox is (min_x, 1024-max_y) to (max_x, 1024-min_y)
vis_x1 = min_x
vis_y1 = 1024 - max_y
vis_x2 = max_x
vis_y2 = 1024 - min_y
print(f'Visible bbox in viewBox: ({vis_x1:.0f}, {vis_y1:.0f}) to ({vis_x2:.0f}, {vis_y2:.0f})')
print(f'  Size: {vis_x2-vis_x1:.0f} x {vis_y2-vis_y1:.0f}')

# Build a clean SVG with the path in standard coordinates (Y up)
# Apply the inverse transform: (x, y) -> (x, 1024 - y)
# For absolute points: y_new = 1024 - y_old
# For relative deltas: dy_new = -dy_old

import re
new_d = []
tokens = re.findall(r'[MmCcLlSsQqTtAaZz]|-?\d+\.?\d*', path_d)
i = 0
last_cmd = None
x, y = 0.0, 0.0
first_move = True

while i < len(tokens):
    tok = tokens[i]
    if re.match(r'^[MmCcLlSsQqTtAaZz]$', tok):
        cmd = tok
        i += 1
    else:
        cmd = last_cmd or 'M'

    if cmd in 'Mm':
        if i + 1 >= len(tokens): break
        nx, ny = float(tokens[i]), float(tokens[i+1])
        i += 2
        # Close previous subpath if this is not the first move
        if not first_move:
            new_d.append('Z')
        first_move = False
        if cmd == 'M':
            x, y = nx, 1024 - ny
            new_d.append(f'M{x:.1f} {y:.1f}')
        else:
            x += nx
            y -= ny
            new_d.append(f'm{x:.1f} {y:.1f}')
    elif cmd in 'Cc':
        if i + 5 >= len(tokens): break
        vals = [float(tokens[i+k]) for k in range(6)]
        i += 6
        c1x, c1y, c2x, c2y, ex, ey = vals
        if cmd == 'C':
            new_c1x, new_c1y = c1x, 1024 - c1y
            new_c2x, new_c2y = c2x, 1024 - c2y
            new_ex, new_ey = ex, 1024 - ey
            new_d.append(f'C{new_c1x:.1f} {new_c1y:.1f} {new_c2x:.1f} {new_c2y:.1f} {new_ex:.1f} {new_ey:.1f}')
            x, y = ex, 1024 - ey
        else:  # c
            # c is relative — just flip the Y deltas
            new_d.append(f'c{c1x:.1f} {-c1y:.1f} {c2x:.1f} {-c2y:.1f} {ex:.1f} {-ey:.1f}')
            x += ex
            y -= ey
    elif cmd in 'Ss':
        if i + 3 >= len(tokens): break
        vals = [float(tokens[i+k]) for k in range(4)]
        i += 4
        c2x, c2y, ex, ey = vals
        if cmd == 'S':
            new_c2x, new_c2y = c2x, 1024 - c2y
            new_ex, new_ey = ex, 1024 - ey
            new_d.append(f'S{new_c2x:.1f} {new_c2y:.1f} {new_ex:.1f} {new_ey:.1f}')
            x, y = ex, 1024 - ey
        else:  # s
            new_d.append(f's{c2x:.1f} {-c2y:.1f} {ex:.1f} {-ey:.1f}')
            x += ex
            y -= ey
    elif cmd in 'Zz':
        # Don't add Z here - we add it before each M/m and at the end
        pass
    elif cmd in 'Ll':
        if i + 1 >= len(tokens): break
        nx, ny = float(tokens[i]), float(tokens[i+1])
        i += 2
        if cmd == 'L':
            new_d.append(f'L{nx:.1f} {1024-ny:.1f}')
            x, y = nx, 1024 - ny
        else:
            x += nx
            y -= ny
            new_d.append(f'l{nx:.1f} {-ny:.1f}')
    last_cmd = cmd

new_d.append('Z')
new_path_d = ' '.join(new_d)
print(f'New path: {len(new_path_d)} bytes, M: {new_path_d.count("M")}, m: {new_path_d.count("m")}, Z: {new_path_d.count("Z")}')

# Set viewBox to match the path's extent (in standard Y-up coords)
# Path is at (min_x, 1024-max_y) to (max_x, 1024-min_y) in original space
# We transformed to (min_x, min_y) where min_y is now at the bottom
# So path extent in new coords: (min_x, 1024-max_y) to (max_x, 1024-min_y)
new_min_y = 1024 - max_y
new_max_y = 1024 - min_y
vb_x = int(min_x) - 4
vb_y = int(new_min_y) - 4
vb_w = int(max_x - min_x) + 8
vb_h = int(new_max_y - new_min_y) + 8
print(f'ViewBox: {vb_x} {vb_y} {vb_w} {vb_h}')

master = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{vb_x} {vb_y} {vb_w} {vb_h}"
     width="{vb_w}" height="{vb_h}"
     role="img"
     aria-label="Opita Code symbol">
  <title>Opita Code - Symbol</title>
  <desc>The Opita Code corporate mark. A 4-lobe ring with a central diamond negative space. The mark represents modular engineering: each lobe interlocks with its neighbors around a governed core.</desc>
  <path fill="#0D0D0D" fill-rule="evenodd" d="{new_path_d}"/>
</svg>
'''

with open('opita-code-symbol.svg', 'w') as f:
    f.write(master)
print(f'\nMaster saved ({len(master)} bytes)')

# Render
cairosvg.svg2png(url='opita-code-symbol.svg', write_to='_final-render.png', output_width=512, output_height=512)
img = Image.open('_final-render.png')
bg = Image.new('RGBA', img.size, (255, 0, 0, 255))
bg.paste(img, (0, 0), img)
bg.save('_final-on-red.png')
print('Rendered')
