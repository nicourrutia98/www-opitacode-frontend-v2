"""
Pipeline profesional de vectorización:
  PNG → PIL (convert to PBM) → mkbitmap (scale + filter) → potrace (--flat, -W -H) → svgo
"""
import subprocess, sys, os
from PIL import Image
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

SRC_PNG = r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend\assets\img\favicon-512x512.png'
OUT_DIR = r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend-v2\brand\master'
MKBITMAP = r'C:\Users\nicou\scoop\shims\mkbitmap.exe'
POTRACE = r'C:\Users\nicou\scoop\shims\potrace.exe'
SVGO = r'C:\Users\nicou\.bun\install\cache\svgo@4.0.1@@@1\bin\svgo.js'

os.chdir(OUT_DIR)
print(f'Working dir: {OUT_DIR}')

# 1) PIL: PNG → PBM (bilevel)
print('\n=== Step 1: PIL convert PNG → PBM ===')
img = Image.open(SRC_PNG).convert('RGBA')
arr = np.array(img)
# Source: white logo on transparent. Threshold: alpha>128 AND gray>200 = ink
gray = arr[:, :, :3].mean(axis=2)
alpha = arr[:, :, 3]
ink = (alpha > 128) & (gray > 200)
print(f'Ink pixels: {ink.sum():,} ({100*ink.sum()/ink.size:.1f}%)')

# Convert to bilevel PIL image (mode '1')
bilevel = Image.fromarray(ink.astype(np.uint8) * 255, mode='L').convert('1')
bilevel.save('_source.pbm')
print(f'Saved _source.pbm ({os.path.getsize("_source.pbm")} bytes)')

# 2) mkbitmap: scale + filter
print('\n=== Step 2: mkbitmap ===')
r = subprocess.run([MKBITMAP, '-s', '4', '-f', '4', '-3', '-t', '0.5', '-o', '_bitmap.pbm', '_source.pbm'],
    capture_output=True, text=True)
print(f'Exit: {r.returncode}')
if r.stderr: print(f'Stderr: {r.stderr}')
print(f'Bitmap: {os.path.getsize("_bitmap.pbm")} bytes')

# 3) potrace with --flat, -W 512 -H 512
print('\n=== Step 3: potrace ===')
r = subprocess.run([POTRACE, '-s', '--flat', '-W', '512', '-H', '512', '-u', '10', '-O', '0.2', '-a', '1.0', '-t', '2', '-o', '_traced-clean.svg', '_bitmap.pbm'],
    capture_output=True, text=True)
print(f'Exit: {r.returncode}')
if r.stderr: print(f'Stderr: {r.stderr}')
if os.path.exists('_traced-clean.svg'):
    size = os.path.getsize('_traced-clean.svg')
    print(f'Traced: {size} bytes')
    with open('_traced-clean.svg') as f:
        content = f.read()
    print(f'First 500: {content[:500]}')
    print(f'Last 200: {content[-200:]}')

# 4) Render the traced SVG to verify
import cairosvg
cairosvg.svg2png(url='_traced-clean.svg', write_to='_traced-render.png', output_width=512, output_height=512)
print(f'\nRendered _traced-render.png')
