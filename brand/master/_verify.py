"""
Render the master symbol at 230x196 (same size as the PDF symbol) and
compare with the PDF reference image.

If the master renders visually identical to the PDF reference, proceed
to generate all variants. If not, iterate on the master geometry.
"""
import cairosvg, sys
from PIL import Image, ImageChops
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')

# 1) Render master at 230x196 (PDF symbol size)
cairosvg.svg2png(
    url='opita-code-symbol.svg',
    write_to='_master-230.png',
    output_width=230,
    output_height=230,  # square (master is square)
    background_color='white'
)
print('Master rendered at 230x230 (square)')

# 2) Load PDF reference
pdf_ref = Image.open(r'C:\Users\nicou\Documents\IA\discolmeds\REPORT\output\_page1-img2.png')
print(f'PDF reference: {pdf_ref.size} mode={pdf_ref.mode}')

# 3) Resize master to match PDF reference size
master = Image.open('_master-230.png').convert('RGBA')
master_resized = master.resize(pdf_ref.size)
master_resized.save('_master-resized.png')
print(f'Master resized to: {master_resized.size}')

# 4) Side-by-side comparison
combined = Image.new('RGBA', (pdf_ref.width * 2 + 20, pdf_ref.height), (255, 255, 255, 255))
combined.paste(pdf_ref.convert('RGBA'), (0, 0))
combined.paste(master_resized, (pdf_ref.width + 20, 0))
combined.save('_compare-side.png')
print('Side-by-side comparison saved: _compare-side.png')

# 5) Pixel diff (only count where both have content)
pdf_arr = np.array(pdf_ref.convert('RGBA'))
master_arr = np.array(master_resized)
# Diff in grayscale (where one is dark and the other is light)
pdf_gray = 255 - pdf_arr[:, :, :3].mean(axis=2)  # 0=white, 255=black
master_gray = 255 - master_arr[:, :, :3].mean(axis=2)
# Both are dark = match; one dark, one light = mismatch
match = (pdf_gray > 50) & (master_gray > 50)
mismatch = ((pdf_gray > 50) & (master_gray < 50)) | ((pdf_gray < 50) & (master_gray > 50))
print(f'\nBoth dark (match): {match.sum()} pixels ({100*match.sum()/(pdf_gray.size):.1f}%)')
print(f'Mismatch:          {mismatch.sum()} pixels ({100*mismatch.sum()/(pdf_gray.size):.1f}%)')
print(f'PDF only dark:     {((pdf_gray > 50) & (master_gray < 50)).sum()} pixels')
print(f'Master only dark:  {((pdf_gray < 50) & (master_gray > 50)).sum()} pixels')

# 6) Save the diff visualization
diff_img = np.zeros((*pdf_gray.shape, 4), dtype=np.uint8)
diff_img[..., 0] = 255  # red
diff_img[..., 3] = mismatch * 200  # semi-transparent where mismatch
Image.fromarray(diff_img).save('_compare-diff.png')
print('Diff visualization saved: _compare-diff.png')
