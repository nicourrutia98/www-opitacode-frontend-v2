"""
Transform potrace path from 36864pt space to 0 0 512 512.
Handles implicit continuation of cubic Béziers.
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

TX = -6158.992421
TY = 43018.075684
SX = 9.605926
SY = -9.604491

def transform_point(x, y):
    return round(x * SX + TX, 2), round(y * SY + TY, 2)

with open('_traced.svg', 'r') as f:
    content = f.read()

match = re.search(r'<path d="([^"]+)"', content, re.DOTALL)
path_d = re.sub(r'\s+', ' ', match.group(1)).strip()

# Tokenize: each M/m/C/c/L/l/Z/z is a command, rest are numbers
tokens = re.findall(r'[MmCcLlZz]|-?\d+\.?\d*', path_d)
print(f'Total tokens: {len(tokens)}')

i = 0
current_x, current_y = 0.0, 0.0
start_x, start_y = 0.0, 0.0
output = []
last_cmd = None  # track for implicit continuation

def parse_numbers(n):
    """Read n numbers from tokens, return as floats."""
    nonlocal i
    nums = [float(tokens[i + k]) for k in range(n)]
    i += n
    return nums

while i < len(tokens):
    tok = tokens[i]

    # If it's a number, it's an implicit continuation of the previous command
    if tok in 'MmCcLlZz':
        cmd = tok
        i += 1
        last_cmd = cmd
    else:
        # Implicit continuation
        if last_cmd in ('c', 'C'):
            cmd = last_cmd
        elif last_cmd in ('m', 'M'):
            cmd = 'M' if last_cmd == 'M' else 'm'  # m continues as m, M continues as L
            if last_cmd == 'm':
                # implicit m after M = relative lineto, but with M first time, subsequent is lineto absolute
                # In SVG, 'M x y' is move, then 'x y' (no command) is implicit L
                cmd = 'L'  # implicit absolute lineto
        elif last_cmd in ('l', 'L'):
            cmd = last_cmd
        else:
            print(f'Unknown token: {tok} at {i}, last_cmd={last_cmd}')
            break

    if cmd in 'Mm':
        x, y = parse_numbers(2)
        if cmd == 'M':
            new_x, new_y = transform_point(x, y)
            current_x, current_y = new_x, new_y
            start_x, start_y = new_x, new_y
            output.append(f'M{new_x} {new_y}')
            last_cmd = 'M'  # subsequent will be implicit L
        else:  # 'm' (relative)
            new_x = current_x + x * SX
            new_y = current_y + y * SY
            current_x, current_y = new_x, new_y
            start_x, start_y = new_x, new_y
            output.append(f'm{new_x:.2f} {new_y:.2f}')
            last_cmd = 'm'  # subsequent will be implicit l
    elif cmd in 'Cc':
        c1x, c1y, c2x, c2y, ex, ey = parse_numbers(6)
        if cmd == 'C':
            new_c1 = transform_point(c1x, c1y)
            new_c2 = transform_point(c2x, c2y)
            new_e = transform_point(ex, ey)
            current_x, current_y = new_e
            output.append(f'C{new_c1[0]} {new_c1[1]} {new_c2[0]} {new_c2[1]} {new_e[0]} {new_e[1]}')
        else:  # 'c' (relative)
            new_c1x = c1x * SX
            new_c1y = c1y * SY
            new_c2x = c2x * SX
            new_c2y = c2y * SY
            new_ex = ex * SX
            new_ey = ey * SY
            current_x += new_ex
            current_y += new_ey
            output.append(f'c{new_c1x:.2f} {new_c1y:.2f} {new_c2x:.2f} {new_c2y:.2f} {new_ex:.2f} {new_ey:.2f}')
    elif cmd in 'Ll':
        x, y = parse_numbers(2)
        if cmd == 'L':
            new_x, new_y = transform_point(x, y)
        else:
            new_x = current_x + x * SX
            new_y = current_y + y * SY
        current_x, current_y = new_x, new_y
        output.append(f'L{new_x:.2f} {new_y:.2f}' if cmd == 'L' else f'l{new_x:.2f} {new_y:.2f}')
    elif cmd in 'Zz':
        output.append('Z')
        current_x, current_y = start_x, start_y

new_d = ' '.join(output)
print(f'New path: {len(new_d)} bytes')

# Save and render
import cairosvg
test_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path fill="#0D0D0D" fill-rule="evenodd" d="{new_d}"/>
</svg>'''
with open('_master-test.svg', 'w') as f:
    f.write(test_svg)
cairosvg.svg2png(url='_master-test.svg', write_to='_master-test.png', output_width=512, output_height=512)
print(f'Rendered: {len(test_svg)} bytes SVG')

with open('_path-transformed.txt', 'w') as f:
    f.write(new_d)
