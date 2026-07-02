"""Final master: take the raw potrace output, just crop the viewBox and add metadata."""
import re
import cairosvg
from PIL import Image

# Read the raw potrace output
with open('_traced-raw.svg') as f:
    raw = f.read()
match = re.search(r'd="([^"]+)"', raw, re.DOTALL)
path_d = match.group(1)

# Path is in coords (108, 107) to (915, 920) with the original transform
# Test with original viewBox 0 0 1024 1024
vb_x, vb_y, vb_w, vb_h = 0, 0, 1024, 1024

# Build the final master with proper structure
master = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="{vb_x} {vb_y} {vb_w} {vb_h}"
     width="{vb_w}.000000pt" height="{vb_h}.000000pt"
     preserveAspectRatio="xMidYMid meet"
     role="img"
     aria-label="Opita Code symbol">
  <title>Opita Code - Symbol</title>
  <desc>The Opita Code corporate mark. A 4-lobe ring with a central diamond negative space. The mark represents modular engineering: each lobe interlocks with its neighbors around a governed core.</desc>
  <g transform="translate(0.000000,1024.000000) scale(1.000000,-1.000000)" fill="#0D0D0D" stroke="none">
    <path fill-rule="evenodd" d="{path_d}"/>
  </g>
</svg>
'''

with open('opita-code-symbol.svg', 'w') as f:
    f.write(master)
print(f'Master saved ({len(master)} bytes)')
print(f'ViewBox: {vb_x} {vb_y} {vb_w} {vb_h}')

# Render
cairosvg.svg2png(url='opita-code-symbol.svg', write_to='_final-render.png', output_width=512, output_height=512)
img = Image.open('_final-render.png')
bg = Image.new('RGBA', img.size, (255, 0, 0, 255))
bg.paste(img, (0, 0), img)
bg.save('_final-on-red.png')
print('Rendered on red')
