import re
with open('opita-code-symbol.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path = match.group(1)
z_count = path.count('Z')
m_count = path.count('M')
c_count = path.count('C')
print(f'M: {m_count}, C: {c_count}, Z: {z_count}')
print(f'Length: {len(path)}')
print(f'First 300: {path[:300]}')
print(f'Last 300: {path[-300:]}')
