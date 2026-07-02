"""
Verify the new master renders identically to the source favicon.
Renders the master at 512x512 and pixel-diffs against the source.
"""
import cairosvg
from PIL import Image
import numpy as np

# Render the new master
cairosvg.svg2png(
    url='opita-code-symbol.svg',
    write_to='_master-render.png',
    output_width=512,
    output_height=512
)
print('Master rendered at 512x512')

# Load source favicon
src = Image.open(r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend\assets\img\favicon-512x512.png').convert('RGBA')
print(f'Source: {src.size} mode={src.mode}')

master = Image.open('_master-render.png').convert('RGBA')

# Convert both to grayscale (ink detection)
def to_ink_mask(img, threshold=128):
    arr = np.array(img)
    gray = arr[:, :, :3].mean(axis=2)
    alpha = arr[:, :, 3]
    return (alpha > 128) & (gray < threshold)  # dark = ink

# Master: rendered as black on white (so dark = ink)
master_ink = to_ink_mask(master, 128)
# Source: white on transparent (so light = ink in the "white logo" sense)
src_arr = np.array(src)
src_gray = src_arr[:, :, :3].mean(axis=2)
src_alpha = src_arr[:, :, 3]
src_ink = (src_alpha > 128) & (src_gray > 200)  # white-ish = ink

print(f'\nSource ink:    {src_ink.sum():,} pixels ({100*src_ink.sum()/src_ink.size:.2f}%)')
print(f'Master ink:    {master_ink.sum():,} pixels ({100*master_ink.sum()/master_ink.size:.2f}%)')
print(f'Both ink:      {(src_ink & master_ink).sum():,} pixels')
print(f'Source only:   {(src_ink & ~master_ink).sum():,} pixels')
print(f'Master only:   {(~src_ink & master_ink).sum():,} pixels')
overlap = (src_ink & master_ink).sum() / max(src_ink.sum(), master_ink.sum())
print(f'Overlap ratio: {overlap:.4f}')

# Save side-by-side
src_rgba = src.convert('RGBA')
master_rgba = master.convert('RGBA')
combined = Image.new('RGBA', (1024 + 20, 512), (200, 200, 200, 255))
combined.paste(src_rgba, (0, 0))
combined.paste(master_rgba, (532, 0))
combined.save('_compare-master.png')
print('Side-by-side saved: _compare-master.png (left=source, right=master)')
