from svg.path import parse_path
import re

with open('_master.svg') as f:
    svg = f.read()
match = re.search(r'd="([^"]+)"', svg, re.DOTALL)
path_d = match.group(1)
path = parse_path(path_d)
print(f'Path elements: {len(path)}')

# Find bbox by sampling each segment
min_x, min_y, max_x, max_y = float('inf'), float('inf'), -float('inf'), -float('inf')
for seg in path:
    # Each segment has start and end points; for curves, sample midpoints
    try:
        x0, y0 = seg.start.real, seg.start.imag
        x1, y1 = seg.end.real, seg.end.imag
        for x, y in [(x0, y0), (x1, y1)]:
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x), max(max_y, y)
        # Sample 10 points along the curve for accurate bbox
        for t in [i/10 for i in range(1, 10)]:
            p = seg.point(t)
            min_x, min_y = min(min_x, p.real), min(min_y, p.imag)
            max_x, max_y = max(max_x, p.real), max(max_y, p.imag)
    except Exception as e:
        pass

print(f'BBox: x=[{min_x:.1f}, {max_x:.1f}] y=[{min_y:.1f}, {max_y:.1f}]')
print(f'Width: {max_x-min_x:.1f}, Height: {max_y-min_y:.1f}')
print(f'Normalized viewBox: 0 0 {max_x-min_x:.0f} {max_y-min_y:.0f}')
print(f'Translate offset: ({min_x:.2f}, {min_y:.2f})')
print(f'Path has {sum(1 for s in path if type(s).__name__ == "CubicBezier")} cubic Beziers')
