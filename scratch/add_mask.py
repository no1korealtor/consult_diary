import sys

def patch_mask(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "def mask_address_string(" not in content:
        mask_func = """
def mask_address_string(addr_str):
    import re
    if not addr_str:
        return ""
    
    parts = addr_str.split()
    if len(parts) >= 2:
        last_part = parts[-1]
        
        # 102-12 -> 102-**
        if "-" in last_part:
            sub_parts = last_part.split("-")
            masked_last = sub_parts[0] + "-**"
            parts[-1] = masked_last
        # 395 -> 3**
        elif last_part.isdigit() and len(last_part) >= 2:
            masked_last = last_part[0] + "**"
            parts[-1] = masked_last
        # 가동 -> 가*
        elif last_part.endswith("동"):
            masked_last = last_part[0] + "*" + "동"
            parts[-1] = masked_last
        # default: ***
        else:
            if len(last_part) > 1:
                parts[-1] = last_part[0] + "**"
            else:
                parts[-1] = "***"
                
    return " ".join(parts)
"""
        content = mask_func + "\n" + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print(f"Already patched {file_path}")

patch_mask('trade_viewer.py')
