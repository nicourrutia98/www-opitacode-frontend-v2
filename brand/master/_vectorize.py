"""
Vectorize the deployed favicon-512x512.png.
The favicon is WHITE on TRANSPARENT (not black on transparent).
Invert for potrace: trace white pixels, output as black shape.
"""
import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image
import numpy as np

src = r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend\assets\img\favicon-512x512.png'
img = Image.open(src)
arr = np.array(img.convert('RGBA'))

# The logo is WHITE pixels with alpha=255. Trace those.
# Create bitmap: white pixels = ink (1), transparent or dark = no ink (0)
gray = arr[:, :, :3].mean(axis=2)
alpha = arr[:, :, 3]
ink = (alpha > 128) & (gray > 200)  # white-ish + opaque = logo
print(f'Ink (white logo) pixels: {ink.sum()} / {ink.size} ({100*ink.sum()/ink.size:.1f}%)')

# Save as PBM (PBM: 0=ink, 1=background, in potrace's logic)
# potrace traces black on white. The "ink" (0) is what gets traced.
# So: white logo pixels → 0 (ink), everything else → 1 (background)
binary = np.where(ink, 0, 1).astype(np.uint8)
pbm = Image.fromarray(binary * 255, mode='L')
pbm.save('_source.pbm')
print('Saved _source.pbm')

# Run potrace
potrace = r'C:\Users\nicou\scoop\shims\potrace.exe'
result = subprocess.run([
    potrace,
    '-s',  # SVG output
    '-o', '_traced.svg',
    '--tight',
    '-t', '4',  # turd size
    '-a', '1.0',  # corner threshold
    '-O', '0.2',  # optimization tolerance
    '-W', '512',  # width
    '-H', '512',  # height
    '_source.pbm'
], capture_output=True, text=True)
print(f'potrace exit: {result.returncode}')
if result.stderr:
    print(f'potrace stderr: {result.stderr[:200]}')

with open('_traced.svg', 'r') as f:
    traced = f.read()
print(f'\nTraced SVG: {len(traced)} bytes')
print(f'First 600 chars:')
print(traced[:600])
