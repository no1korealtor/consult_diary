import re

def fix_decompiled_or(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern:
    # if not item.get("A"):
    #     item.get("A")
    # var = item.get("B")
    
    # We want to replace it with:
    # var = item.get("A") or item.get("B")

    pattern1 = re.compile(
        r'if not (\w+)\.get\("([^"]+)"\):\s*\n\s*\1\.get\("\2"\)\s*\n\s*(\w+) = \1\.get\("([^"]+)"\)',
        re.MULTILINE
    )
    
    # Also handle the cases where it is assigned to `item_by` etc.
    # We can use a more generic substitution:
    def replacer(match):
        obj_name = match.group(1)
        key1 = match.group(2)
        var_name = match.group(3)
        key2 = match.group(4)
        return f'{var_name} = {obj_name}.get("{key1}") or {obj_name}.get("{key2}")'
    
    new_content = pattern1.sub(replacer, content)
    
    # Sometimes it's just `item_by = item.get("constructionYear")` without assignment in the regex?
    # Let's check another pattern.
    # What if the original was `var = item.get("A") or item.get("B")`
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Fixed {file_path}")

fix_decompiled_or(r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py')
fix_decompiled_or(r'd:\부동산업무\antigravity\consult_diary\building_viewer.py')
fix_decompiled_or(r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py')
fix_decompiled_or(r'd:\부동산업무\antigravity\consult_diary\scratch\building_viewer.py')
