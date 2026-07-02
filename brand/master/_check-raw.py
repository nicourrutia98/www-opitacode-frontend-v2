import re
with open('_traced-raw.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path = match.group(1)
print(f'Z: {path.count("Z")}, z: {path.count("z")}')
print(f'M: {path.count("M")}, m: {path.count("m")}')
print(f'First 200: {path[:200]}')
print(f'Last 200: {path[-200:]}')
print(f'First 50 after first M: {path[200:400]}')
