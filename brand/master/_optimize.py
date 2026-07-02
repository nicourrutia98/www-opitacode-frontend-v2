"""Re-run potrace with better parameters: lower precision, higher opttolerance."""
import subprocess, sys, os
from PIL import Image
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

SRC_PNG = r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend\assets\img\favicon-512x512.png'
OUT_DIR = r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend-v2\brand\master'
MKBITMAP = r'C:\Users\nicou\scoop\shims\mkbitmap.exe'
POTRACE = r'C:\Users\nicou\scoop\shims\potrace.exe'

os.chdir(OUT_DIR)

# PNG → PBM
img = Image.open(SRC_PNG).convert('RGBA')
arr = np.array(img)
gray = arr[:, :, :3].mean(axis=2)
alpha = arr[:, :, 3]
ink = (alpha > 128) & (gray > 200)
bilevel = Image.fromarray(ink.astype(np.uint8) * 255, mode='L').convert('1')
bilevel.save('_source.pbm')

# mkbitmap: -s 2 (just 2x scale, less detail) -f 4 (default filter) -3 (cubic)
subprocess.run([MKBITMAP, '-s', '2', '-f', '4', '-3', '-t', '0.5', '-o', '_bitmap.pbm', '_source.pbm'], check=True, capture_output=True)
print(f'Bitmap: {os.path.getsize("_bitmap.pbm")} bytes')

# potrace with optimized parameters
# -u 1: integer precision (1px)
# -O 1.0: higher opttolerance (more simplification)
# -t 10: turdsize 10 (remove more specks)
# -a 1.0: default alphamax
# --flat: single path
subprocess.run([POTRACE, '-s', '--flat', '-u', '1', '-O', '1.0', '-t', '10', '-a', '1.0', '-o', '_traced-optimized.svg', '_bitmap.pbm'], check=True, capture_output=True)
print(f'Traced: {os.path.getsize("_traced-optimized.svg")} bytes')

# svgo optimize
subprocess.run(['svgo.cmd', '--multipass', '_traced-optimized.svg', '-o', '_master-opt.svg'], capture_output=True)
print(f'SVGO: {os.path.getsize("_master-opt.svg")} bytes')

# Render to verify
import cairosvg
cairosvg.svg2png(url='_master-opt.svg', write_to='_master-opt-render.png', output_width=512, output_height=512)
print('Rendered')

# Get bbox
from svg.path import parse_path
import re
with open('_master-opt.svg') as f: svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path_d = match.group(1)
path = parse_path(path_d)
print(f'Path elements: {len(path)}')

min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')
for seg in path:
    try:
        for p in [seg.start, seg.end] + [seg.point(t) for t in [i/10 for i in range(1, 10)]]:
            min_x, min_y = min(min_x, p.real), min(min_y, p.imag)
            max_x, max_y = max(max_x, p.real), max(max_y, p.imag)
    except: pass

print(f'BBox: x=[{min_x:.0f}, {max_x:.0f}] y=[{min_y:.0f}, {max_y:.0f}]')
print(f'Width: {max_x-min_x:.0f}, Height: {max_y-min_y:.0f}')
print(f'Aspect: {(max_x-min_x)/(max_y-min_y):.4f}')
