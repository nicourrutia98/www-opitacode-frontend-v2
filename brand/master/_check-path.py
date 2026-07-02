from svg.path import parse_path
import re
from collections import Counter

with open('_master-opt.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path_d = match.group(1)
path = parse_path(path_d)

types = Counter(type(seg).__name__ for seg in path)
print(f'Segment types: {dict(types)}')

# Show first 5 segments
for i, seg in enumerate(path[:5]):
    print(f'  {i}: {type(seg).__name__} - {seg}')

# Check the original path d for Z commands
z_count = path_d.count('Z')
z_lower = path_d.count('z')
print(f'\nOriginal path Z count: {z_count} (uppercase), {z_lower} (lowercase)')

# Look at the actual svg output (what svgo produced)
with open('_master-opt.svg') as f:
    content = f.read()
print(f'\nFirst 1000 chars of _master-opt.svg:')
print(content[:1000])
