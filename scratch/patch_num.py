import re

def patch_num(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_func = """def get_numeric_averages(subset, is_rent, is_wolse=False):
    sum_price = 0
    count = 0
    for item in subset:
        if is_wolse:
            deposit_str = str(item.get("deposit", "")).strip().replace(",", "")
            monthly_str = str(item.get("monthlyRent", "")).strip().replace(",", "")
            dep = int(deposit_str) if deposit_str else 0
            mon = int(monthly_str) if monthly_str else 0
            amt = dep + mon * 100
        else:
            _, amt, _ = format_price(item, is_rent=is_rent)
            
        if amt:
            sum_price += amt
            count += 1
            
    if count == 0:
        return 0
    return int(sum_price / count)"""

    content = re.sub(
        r'def get_numeric_averages\(subset, is_rent, is_wolse\):.*?return int\(sum_price / count\)',
        new_func,
        content,
        flags=re.DOTALL
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

patch_num('trade_viewer.py')
