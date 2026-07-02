"""
Genera TODOS los assets de marca desde el PNG canónico (favicon-512x512.png).

Source of truth: el SVG maestro (brand/master/opita-code-symbol.svg) Y el PNG
original (frontend/assets/img/favicon-512x512.png) que es la versión rasterizada.

Outputs:
  brand/output/svg/    SVGs light + dark + horizontal + stacked
  brand/output/png/    PNGs a 7 tamaños
  brand/output/ico/    favicon.ico multi-res
  brand/output/social/ OG image, GitHub avatar, app icon

Estándar de marca:
  - #0D0D0D (casi-negro, para fondos claros)
  - #FAF8F5 (off-white, para fondos oscuros)
  - tipografía: 'Segoe UI', system-ui, -apple-system, sans-serif
  - wordmark "Opita Code" — "Opita" bold 600, "Code" regular 400
"""
import os, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import struct
import cairosvg

ROOT = r'C:\Users\nicou\Documents\IA\AGENTE\www.opitacode.com\frontend-v2'
MASTER_DIR = os.path.join(ROOT, 'brand', 'master')
OUT_DIR = os.path.join(ROOT, 'brand', 'output')
SRC_PNG = os.path.join(ROOT, '..', 'frontend', 'assets', 'img', 'favicon-512x512.png')

# Asegurar carpetas
for sub in ['svg', 'png', 'ico', 'social', 'intermediate']:
    os.makedirs(os.path.join(OUT_DIR, sub), exist_ok=True)

print(f'Source PNG: {SRC_PNG}')

# 1) Cargar PNG canónico
src = Image.open(SRC_PNG).convert('RGBA')
print(f'Source: {src.size} mode={src.mode}')

# El logo es BLANCO sobre transparente. Para generar la versión NEGRA,
# invertimos los colores (negro sobre transparente).
def invert_white_to_black(img):
    arr = np.array(img)
    # Donde es blanco (rgb > 200) y opaco (alpha > 128), poner negro
    gray = arr[:, :, :3].mean(axis=2)
    alpha = arr[:, :, 3]
    is_white_logo = (alpha > 128) & (gray > 200)
    new_arr = arr.copy()
    new_arr[is_white_logo, :3] = 0  # negro
    new_arr[is_white_logo, 3] = 255  # opaco
    return Image.fromarray(new_arr, mode='RGBA')

black_src = invert_white_to_black(src)
black_src.save(os.path.join(OUT_DIR, 'intermediate', 'symbol-black-512.png'))
print('Generated black version')

# 2) PNG variants a 7 tamaños
#    16, 32, 48, 64, 180, 192, 512
sizes = [16, 32, 48, 64, 180, 192, 512]
for size in sizes:
    img = black_src.resize((size, size), Image.LANCZOS)
    out_path = os.path.join(OUT_DIR, 'png', f'opita-code-symbol-{size}.png')
    img.save(out_path)
    print(f'  {out_path}: {os.path.getsize(out_path)} bytes')

# 3) favicon.ico multi-res (16, 32, 48, 64)
ico_sizes = [16, 32, 48, 64]
# Generate each size with transparency
ico_images = []
for size in ico_sizes:
    img = black_src.resize((size, size), Image.LANCZOS)
    ico_images.append((size, img.tobytes('raw', 'RGBA')))

# Build ICO file manually
ico_path = os.path.join(OUT_DIR, 'ico', 'opita-code-favicon.ico')
with open(ico_path, 'wb') as f:
    # Header: 6 bytes
    f.write(struct.pack('<HHH', 0, 1, len(ico_images)))
    # Directory: 16 bytes per image
    offset = 6 + 16 * len(ico_images)
    directory = b''
    for size, data in ico_images:
        w = 0 if size == 256 else size
        h = 0 if size == 256 else size
        directory += struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    f.write(directory)
    # PNG data (modern ICO can embed PNG directly)
    for size, data in ico_images:
        f.write(data)
print(f'  {ico_path}: {os.path.getsize(ico_path)} bytes')

# 4) App icon (1024x1024) — iOS-style
# iOS app icons: 1024x1024 with the symbol centered, no transparency
app_bg = Image.new('RGBA', (1024, 1024), (250, 248, 245, 255))  # off-white
# Center the symbol with 20% padding
symbol_size = 1024 * 0.6
symbol = black_src.resize((int(symbol_size), int(symbol_size)), Image.LANCZOS)
x = (1024 - symbol.width) // 2
y = (1024 - symbol.height) // 2
app_bg.paste(symbol, (x, y), symbol)
app_bg.save(os.path.join(OUT_DIR, 'social', 'opita-code-app-icon-1024.png'))
print(f'  app-icon-1024: {os.path.getsize(os.path.join(OUT_DIR, "social", "opita-code-app-icon-1024.png"))} bytes')

# 5) GitHub avatar (460x460, square with bg)
gh_size = 460
gh_bg = Image.new('RGBA', (gh_size, gh_size), (13, 13, 13, 255))  # #0D0D0D
# Use the white version (the favicon is white-on-transparent, so it's the right asset for dark bg)
gh_symbol = src.resize((int(gh_size * 0.6), int(gh_size * 0.6)), Image.LANCZOS)
x = (gh_size - gh_symbol.width) // 2
y = (gh_size - gh_symbol.height) // 2
gh_bg.paste(gh_symbol, (x, y), gh_symbol)
gh_bg.save(os.path.join(OUT_DIR, 'social', 'opita-code-github-avatar.png'))
print(f'  github-avatar: {os.path.getsize(os.path.join(OUT_DIR, "social", "opita-code-github-avatar.png"))} bytes')

# 6) OG image (1200x630) — symbol + "Opita Code" wordmark + tagline
og_w, og_h = 1200, 630
og_bg = Image.new('RGBA', (og_w, og_h), (250, 248, 245, 255))  # off-white
draw = ImageDraw.Draw(og_bg)

# Symbol on the left
og_symbol_size = 240
og_symbol = black_src.resize((og_symbol_size, og_symbol_size), Image.LANCZOS)
og_bg.paste(og_symbol, (100, (og_h - og_symbol_size) // 2), og_symbol)

# Wordmark text — find a usable font
def find_font(size, weight='regular'):
    candidates = [
        ('C:\\Windows\\Fonts\\segoeuib.ttf' if weight == 'bold' else 'C:\\Windows\\Fonts\\segoeui.ttf'),
        'C:\\Windows\\Fonts\\arial.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except: pass
    return ImageFont.load_default()

# Use Segoe UI for the wordmark
font_xxl = find_font(96, 'bold')  # "Opita" large bold
font_xl = find_font(96, 'regular')  # "Code" large regular
font_sm = find_font(28, 'regular')  # tagline

# Text positioning (to the right of the symbol)
text_x = 100 + og_symbol_size + 40
text_y = (og_h - 96) // 2 - 20

# "Opita" in bold
draw.text((text_x, text_y), 'Opita', fill=(13, 13, 13, 255), font=font_xxl)
# Calculate "Opita" width to position "Code"
opita_bbox = draw.textbbox((0, 0), 'Opita', font=font_xxl)
opita_width = opita_bbox[2] - opita_bbox[0]
code_x = text_x + opita_width + 20
code_y = text_y + 8  # slight offset for baseline alignment
draw.text((code_x, code_y), 'Code', fill=(13, 13, 13, 255), font=font_xl)

# Tagline
tagline = 'Infraestructura disenada, no improvisada'
tag_y = text_y + 130
draw.text((text_x, tag_y), tagline, fill=(102, 102, 102, 255), font=font_sm)

og_bg.save(os.path.join(OUT_DIR, 'social', 'opita-code-og-image.png'))
print(f'  og-image: {os.path.getsize(os.path.join(OUT_DIR, "social", "opita-code-og-image.png"))} bytes')

# 7) Wordmark lockups (SVG) — use the master SVG + add text
# For now, use the master as the symbol. Wordmark SVGs come next.

print('\n=== Summary ===')
print(f'Source: {SRC_PNG}')
print(f'Output: {OUT_DIR}')
for root, dirs, files in os.walk(OUT_DIR):
    for f in files:
        path = os.path.join(root, f)
        size_kb = os.path.getsize(path) / 1024
        print(f'  {os.path.relpath(path, OUT_DIR)}: {size_kb:.1f} KB')
