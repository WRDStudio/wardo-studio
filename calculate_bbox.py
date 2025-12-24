import re
import xml.etree.ElementTree as ET

def parse_svg_path(path_str):
    # Simplified path parser for M, m, L, l, C, c, Z, z
    # This is not a full SVG parser but should handle the simple output from Potrace/similar tools
    # We only care about approximate bounding box
    
    # Split by commands
    commands = re.findall(r'([a-zA-Z])([^a-zA-Z]*)', path_str)
    
    points = []
    current_pos = (0, 0)
    
    for cmd, args_str in commands:
        args = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', args_str)]
        
        if cmd == 'M':
            current_pos = (args[0], args[1])
            points.append(current_pos)
        elif cmd == 'm':
            current_pos = (current_pos[0] + args[0], current_pos[1] + args[1])
            points.append(current_pos)
        elif cmd == 'L':
            for i in range(0, len(args), 2):
                current_pos = (args[i], args[i+1])
                points.append(current_pos)
        elif cmd == 'l':
            for i in range(0, len(args), 2):
                current_pos = (current_pos[0] + args[i], current_pos[1] + args[i+1])
                points.append(current_pos)
        elif cmd == 'C': # Cubic bezier
            for i in range(0, len(args), 6):
                # We just take the end point for bbox approximation
                current_pos = (args[i+4], args[i+5])
                points.append(current_pos)
        elif cmd == 'c':
            for i in range(0, len(args), 6):
                current_pos = (current_pos[0] + args[i+4], current_pos[1] + args[i+5])
                points.append(current_pos)
        elif cmd == 'Z' or cmd == 'z':
            pass
            
    return points

def calculate_bbox(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Find the group with transform
    # Namespace handling might be needed
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    g = root.find('.//svg:g', ns)
    if g is None:
        g = root.find('.//g') # Try without namespace
        
    if g is None:
        print("No group found")
        return

    transform = g.get('transform')
    print(f"Transform: {transform}")
    
    # Parse transform
    # translate(0.000000,1024.000000) scale(0.100000,-0.100000)
    tx, ty = 0, 0
    sx, sy = 1, 1
    
    if 'translate' in transform:
        t_args = re.findall(r'translate\(([^)]+)\)', transform)[0]
        tx, ty = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', t_args)]
        
    if 'scale' in transform:
        s_args = re.findall(r'scale\(([^)]+)\)', transform)[0]
        sx, sy = [float(x) for x in re.findall(r'[-+]?\d*\.?\d+', s_args)]
        
    print(f"Parsed Transform: tx={tx}, ty={ty}, sx={sx}, sy={sy}")
    
    path = g.find('.//svg:path', ns)
    if path is None:
        path = g.find('.//path')
        
    d = path.get('d')
    points = parse_svg_path(d)
    
    if not points:
        print("No points found")
        return
        
    # Apply transform to all points
    transformed_points = []
    for x, y in points:
        # Scale then Translate? Or Translate then Scale?
        # SVG transform attribute is applied right-to-left (or inner-to-outer)
        # But here it is a string "translate(...) scale(...)"
        # This means translate is applied *after* scale?
        # Actually in SVG "transform='A B'" means A(B(x))
        # So translate is applied to the result of scale.
        
        # x' = x * sx + tx
        # y' = y * sy + ty
        
        tx_pt = x * sx + tx
        ty_pt = y * sy + ty
        transformed_points.append((tx_pt, ty_pt))
        
    # Calculate bbox
    min_x = min(p[0] for p in transformed_points)
    max_x = max(p[0] for p in transformed_points)
    min_y = min(p[1] for p in transformed_points)
    max_y = max(p[1] for p in transformed_points)
    
    print(f"BBox: min_x={min_x}, min_y={min_y}, max_x={max_x}, max_y={max_y}")
    print(f"Width: {max_x - min_x}, Height: {max_y - min_y}")
    
    # Suggest viewBox
    # Add some padding
    padding = 10
    vb_x = min_x - padding
    vb_y = min_y - padding
    vb_w = (max_x - min_x) + 2 * padding
    vb_h = (max_y - min_y) + 2 * padding
    
    print(f"Suggested viewBox: {vb_x:.2f} {vb_y:.2f} {vb_w:.2f} {vb_h:.2f}")

calculate_bbox(r'c:\Users\Wardo\.gemini\antigravity\scratch\wardo-studio\public\images\WS-Bold.svg')
