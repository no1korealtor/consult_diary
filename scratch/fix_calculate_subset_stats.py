import re

def fix_calculate_subset_stats(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_func = """def calculate_subset_stats(subset, is_rent, is_wolse):
    if not subset:
        return None
    sum_price = 0; sum_area_pyung = 0.0; count_area = 0; trade_amts = []
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
        
    min_amt = min(trade_amts)
    max_amt = max(trade_amts)
    avg_amt = sum(trade_amts) / len(trade_amts)
    
    def local_format(val):
        if val >= 10_000:
            eok = int(val // 10_000)
            man = int(val % 10_000)
            if man > 0:
                return f"{eok}억 {man:,}만"
            return f"{eok}억"
        return f"{int(val):,}만"
        
    price_range = f"{local_format(min_amt)} ~ {local_format(max_amt)}" if min_amt != max_amt else local_format(min_amt)
    avg_price = local_format(avg_amt)
    
    avg_pyung_str = "계산 불가"
    if count_area > 0 and sum_area_pyung > 0:
        avg_pyung_price = (sum_price / count_area) / (sum_area_pyung / count_area)
        avg_pyung_str = local_format(avg_pyung_price)
        
    return {
        "count": len(trade_amts),
        "range": price_range,
        "avg": avg_price,
        "pyung_unit": avg_pyung_str
    }
"""

    pattern = re.compile(r'def calculate_subset_stats\(subset, is_rent, is_wolse\):.*?def get_numeric_averages\(', re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub(new_func + 'def get_numeric_averages(', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {file_path}")
    else:
        print(f"Could not find calculate_subset_stats in {file_path}")

fix_calculate_subset_stats(r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py')
fix_calculate_subset_stats(r'd:\부동산업무\antigravity\consult_diary\building_viewer.py')
fix_calculate_subset_stats(r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py')
fix_calculate_subset_stats(r'd:\부동산업무\antigravity\consult_diary\scratch\building_viewer.py')
