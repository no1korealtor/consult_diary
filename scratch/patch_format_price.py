import re

def patch_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_func = """def format_price(item, is_rent):
    if is_rent:
        dep_val = item.get("deposit")
        if dep_val is None:
            dep_val = 0
        if isinstance(dep_val, str):
            dep_val = int(dep_val.replace(",", "").strip()) if dep_val else 0
            
        rent_val = item.get("monthlyRent")
        if rent_val is None:
            rent_val = 0
        if isinstance(rent_val, str):
            rent_val = int(rent_val.replace(",", "").strip()) if rent_val else 0
            
        if dep_val >= 10_000:
            eok = dep_val // 10_000
            man = dep_val % 10_000
            dep_display = f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
        else:
            dep_display = f"{dep_val:,}만"
            
        if rent_val > 0:
            return (f"{dep_display}/{rent_val}만", dep_val, rent_val)
        return (dep_display, dep_val, 0)
    else:
        amt_val = item.get("dealAmount")
        if amt_val is None:
            amt_val = 0
        if isinstance(amt_val, str):
            amt_val = int(amt_val.replace(",", "").strip()) if amt_val else 0
            
        if amt_val >= 10_000:
            eok = amt_val // 10_000
            man = amt_val % 10_000
            amt_display = f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
        else:
            amt_display = f"{amt_val:,}만"
        return (amt_display, amt_val, None)"""

    content = re.sub(
        r'def format_price\(item, is_rent\):.*?def get_apartment_size_groups\(',
        new_func + '\ndef get_apartment_size_groups(',
        content,
        flags=re.DOTALL
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {file_path}")

patch_file('trade_viewer.py')
