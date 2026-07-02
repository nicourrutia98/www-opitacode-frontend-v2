import cairosvg
from PIL import Image
import numpy as np

# Test 1: simple rectangle fill
test1 = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M 10 10 L 90 10 L 90 90 L 10 90 Z" fill="black"/></svg>'
with open('_t1.svg', 'w') as f: f.write(test1)
cairosvg.svg2png(url='_t1.svg', write_to='_t1.png', output_width=100, output_height=100)
arr = np.array(Image.open('_t1.png').convert('RGBA'))
print(f'Test 1 (simple rect): black pixels = {(arr[:,:,:3].mean(axis=2) < 50).sum()}')

# Test 2: same with transform
test2 = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g transform="translate(0, 100) scale(1, -1)"><path d="M 10 90 L 90 90 L 90 10 L 10 10 Z" fill="black"/></g></svg>'
with open('_t2.svg', 'w') as f: f.write(test2)
cairosvg.svg2png(url='_t2.svg', write_to='_t2.png', output_width=100, output_height=100)
arr = np.array(Image.open('_t2.png').convert('RGBA'))
print(f'Test 2 (transform + inverted): black pixels = {(arr[:,:,:3].mean(axis=2) < 50).sum()}')

# Test 3: complex path with relative cubic (like potrace)
test3 = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><g transform="translate(0, 1024) scale(1, -1)" fill="#000000" stroke="none"><path d="M375 916 c0 -1 -1 -1 -3 -1 c-2 0 -3 0 -4 -1 c-1 -1 -3 -1 -3 -1 c-1 1 -2 0 -3 -1 c-1 0 -2 -1 -3 -1 c-1 1 -2 0 -3 0 c0 -1 -6 -4 -8 -4 c-1 0 -2 0 -3 -1 c0 -1 -1 -1 -2 -1 c-1 1 -2 0 -3 0 c0 -2 -7 -4 -8 -4 c0 1 -1 1 -1 0 c-1 -1 -12 -6 -13 -6 c0 1 -1 1 -1 0 c-1 -1 -11 -6 -13 -6 z"/></g></svg>'
with open('_t3.svg', 'w') as f: f.write(test3)
cairosvg.svg2png(url='_t3.svg', write_to='_t3.png', output_width=100, output_height=100)
arr = np.array(Image.open('_t3.png').convert('RGBA'))
print(f'Test 3 (potrace-style with z): black pixels = {(arr[:,:,:3].mean(axis=2) < 50).sum()}')

# Test 4: same as test 3 but no z
test4 = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><g transform="translate(0, 1024) scale(1, -1)" fill="#000000" stroke="none"><path d="M375 916 c0 -1 -1 -1 -3 -1 c-2 0 -3 0 -4 -1 c-1 -1 -3 -1 -3 -1 c-1 1 -2 0 -3 -1 c-1 0 -2 -1 -3 -1 c-1 1 -2 0 -3 0 c0 -1 -6 -4 -8 -4 c-1 0 -2 0 -3 -1 c0 -1 -1 -1 -2 -1 c-1 1 -2 0 -3 0 c0 -2 -7 -4 -8 -4 c0 1 -1 1 -1 0 c-1 -1 -12 -6 -13 -6 c0 1 -1 1 -1 0 c-1 -1 -11 -6 -13 -6"/></g></svg>'
with open('_t4.svg', 'w') as f: f.write(test4)
cairosvg.svg2png(url='_t4.svg', write_to='_t4.png', output_width=100, output_height=100)
arr = np.array(Image.open('_t4.png').convert('RGBA'))
print(f'Test 4 (potrace-style NO z): black pixels = {(arr[:,:,:3].mean(axis=2) < 50).sum()}')
