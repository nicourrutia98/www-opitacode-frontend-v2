"""Check if the favicon-512x512.png is one connected ring or 4 separate lobes."""
from PIL import Image
import numpy as np
from scipy import ndimage

img = Image.open(r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend\assets\img\favicon-512x512.png')
arr = np.array(img.convert('RGBA'))
# Source: white logo on transparent
gray = arr[:, :, :3].mean(axis=2)
alpha = arr[:, :, 3]
ink = (alpha > 128) & (gray > 200)
print(f'Ink pixels: {ink.sum():,}')

# Find connected components
labeled, num_features = ndimage.label(ink)
print(f'Number of connected components (ink): {num_features}')

# Check the inverse (transparent = "ink" for the outside)
not_ink = ~ink
labeled2, num_features2 = ndimage.label(not_ink)
print(f'Number of connected components (NOT ink, i.e., transparent + 1 ring center): {num_features2}')

# If the logo is a single ring, the inverse should have 2 components:
# - 1 outer (the area outside the ring)
# - 1 inner (the diamond cutout)
# Plus the disconnected "ink" might be 1 component (the ring itself) or 4 (the lobes)

# Check the size of each component
for labeled_arr, n, name in [(labeled, num_features, 'ink'), (labeled2, num_features2, 'not_ink')]:
    sizes = [(labeled_arr == i).sum() for i in range(1, n + 1)]
    sizes.sort(reverse=True)
    print(f'  {name} component sizes: {sizes[:10]}')
