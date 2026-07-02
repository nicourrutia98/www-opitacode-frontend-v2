import re
with open('_traced-optimized.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path = match.group(1)
print(f'Pre-svgo Z count: {path.count("Z")}')
print(f'Pre-svgo M count: {path.count("M")}')
print(f'Pre-svgo m count: {path.count("m")}')
print(f'Pre-svgo z count: {path.count("z")}')
print(f'Pre-svgo First 300: {path[:300]}')
print(f'Pre-svgo Last 300: {path[-300:]}')
