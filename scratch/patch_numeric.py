import re

def patch():
    with open('trade_viewer.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. get_avg_display
    content = content.replace('def get_avg_display(subset, is_rent, is_wolse):', 'def get_avg_display(subset, is_rent, is_wolse=False):')
    
    # 2. get_numeric_averages signature
    content = content.replace('def get_numeric_averages(subset, is_rent, is_wolse):', 'def get_numeric_averages(subset, is_rent, is_wolse=False):')
    
    # 3. get_numeric_averages body
    new_body = """
def get_numeric_averages(subset, is_rent, is_wolse=False):
    if not subset:
        return None
    sum_price = 0
    sum_area_pyung = 0.0
    count_area = 0
    trade_amts = []
    
    for item in subset:
        if is_wolse:
            deposit_str = str(item.get("deposit", "")).strip().replace(",", "")
            monthly_str = str(item.get("monthlyRent", "")).strip().replace(",", "")
            dep = int(deposit_str) if deposit_str else 0
            mon = int(monthly_str) if monthly_str else 0
            amt = dep + mon * 100
        else:
            _, amt, _ = format_price(item, is_rent=is_rent)
            
        if not amt:
            continue
            
        trade_amts.append(amt)
        area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
        try:
            area = float(area_val)
        except:
            area = 0.0
            
        if area > 0:
            sum_price += amt
            sum_area_pyung += area * 0.3025
            count_area += 1

    if not trade_amts:
        return None

    avg_price = int(sum(trade_amts) / len(trade_amts))
    avg_pyung_price = None
    if count_area > 0 and sum_area_pyung > 0:
        avg_pyung_price = int(sum_price / sum_area_pyung)
        
    avg_price_str = f"{avg_price:,}만"
    if avg_price >= 10000:
        eok = avg_price // 10000
        man = avg_price % 10000
        if man > 0:
            avg_price_str = f"{eok}억 {man:,}만"
        else:
            avg_price_str = f"{eok}억"
            
    avg_pyung_str = ""
    if avg_pyung_price:
        if avg_pyung_price >= 10000:
            e = avg_pyung_price // 10000
            m = avg_pyung_price % 10000
            if m > 0:
                avg_pyung_str = f"{e}억 {m:,}만/평"
            else:
                avg_pyung_str = f"{e}억/평"
        else:
            avg_pyung_str = f"{avg_pyung_price:,}만/평"
            
    return {
        "count": len(subset),
        "avg_price": avg_price,
        "avg": avg_price_str,
        "avg_pyung_price": avg_pyung_price,
        "pyung_unit": avg_pyung_str
    }
"""
    
    # We replace from def get_numeric_averages to the end of the function (before def filter_by_size_category)
    content = re.sub(
        r'def get_numeric_averages\(subset, is_rent, is_wolse=False\):.*?def filter_by_size_category\(',
        new_body.strip() + '\ndef filter_by_size_category(',
        content,
        flags=re.DOTALL
    )

    with open('trade_viewer.py', 'w', encoding='utf-8') as f:
        f.write(content)

patch()
