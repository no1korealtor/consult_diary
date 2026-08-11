import re

def fix_all(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. fix_or.py (already written and tested)
    def replacer(match):
        obj_name = match.group(1)
        key1 = match.group(2)
        var_name = match.group(3)
        key2 = match.group(4)
        return f'{var_name} = {obj_name}.get("{key1}") or {obj_name}.get("{key2}")'
    pattern1 = re.compile(
        r'if not (\w+)\.get\("([^"]+)"\):\s*\n\s*\1\.get\("\2"\)\s*\n\s*(\w+) = \1\.get\("([^"]+)"\)',
        re.MULTILINE
    )
    content = pattern1.sub(replacer, content)

    # 2. fix_list_comp.py (already tested)
    content = re.sub(
        r'\[t for t in trades if not get_group_for_item\(t, apt_groups\) == g\]\s*\n\s*g_trades = ", "\.join\(cond_parts\)\s*\n\s*t = ", "\.join\(cond_parts\)',
        r'g_trades = [t for t in trades if get_group_for_item(t, apt_groups) == g]',
        content
    )
    content = re.sub(
        r'\[t for t in jeonses if not get_group_for_item\(t, apt_groups\) == g\]\s*\n\s*g_jeonses = None\s*\n\s*t = None',
        r'g_jeonses = [t for t in jeonses if get_group_for_item(t, apt_groups) == g]',
        content
    )
    content = re.sub(
        r'\[t for t in wolses if not get_group_for_item\(t, apt_groups\) == g\]\s*\n\s*g_wolses = None\s*\n\s*t = None',
        r'g_wolses = [t for t in wolses if get_group_for_item(t, apt_groups) == g]',
        content
    )

    # 3. fix get_subset_info (the default args)
    content = content.replace(
        'def get_subset_info(subset, is_rent, is_wolse):',
        'def get_subset_info(subset, is_rent=False, is_wolse=False):'
    )

    # 4. fix format_price
    new_format_price = """def format_price(item, is_rent):
    if is_rent:
        dep_val = item.get("deposit")
        if dep_val is None:
            dep_val = 0
        if isinstance(dep_val, str):
            dep_val = int(dep_val.replace(",", "").strip())
        
        rent_val = item.get("monthlyRent")
        if rent_val is None:
            rent_val = 0
        if isinstance(rent_val, str):
            rent_val = int(rent_val.replace(",", "").strip())
            
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
            amt_val = int(amt_val.replace(",", "").strip())
            
        if amt_val >= 10_000:
            eok = amt_val // 10_000
            man = amt_val % 10_000
            amt_display = f"{eok}억 {man:,}만" if man > 0 else f"{eok}억"
        else:
            amt_display = f"{amt_val:,}만"
        return (amt_display, amt_val, None)"""
    content = re.sub(r'def format_price\(item, is_rent\):.*?def get_apartment_size_groups\(', new_format_price + '\ndef get_apartment_size_groups(', content, flags=re.DOTALL)

    # 5. fix calculate_subset_stats
    new_calculate_subset_stats = """def calculate_subset_stats(subset, is_rent, is_wolse):
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
    }"""
    content = re.sub(r'def calculate_subset_stats\(subset, is_rent, is_wolse\):.*?def get_numeric_averages\(', new_calculate_subset_stats + '\ndef get_numeric_averages(', content, flags=re.DOTALL)

    # 6. fix filter_by_size_category
    new_filter_by_size_category = """def filter_by_size_category(items, target_area, prop_type_name, apt_groups):
    if target_area is None:
        return items
    try:
        t_area = float(target_area)
        filtered = []
        if prop_type_name == "아파트" and apt_groups:
            target_group = get_group_for_item({"excluUseAr": t_area}, apt_groups)
            if target_group:
                for item in items:
                    if get_group_for_item(item, apt_groups) == target_group:
                        filtered.append(item)
                return filtered
            return items
            
        if t_area < 26.0:
            cat = "under_26"
        elif t_area < 43.0:
            cat = "between_26_43"
        else:
            cat = "above_43"
            
        for item in items:
            area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
            try:
                area = float(area_val)
            except:
                area = 0.0
                
            if cat == "under_26" and area < 26.0:
                filtered.append(item)
            elif cat == "between_26_43" and 26.0 <= area < 43.0:
                filtered.append(item)
            elif cat == "above_43" and area >= 43.0:
                filtered.append(item)
                
        return filtered
    except:
        return items"""
    content = re.sub(r'def filter_by_size_category\(items, target_area, prop_type_name, apt_groups\):.*?def get_size_category_label\(', new_filter_by_size_category + '\ndef get_size_category_label(', content, flags=re.DOTALL)

    # 7. fix group_items
    new_group_items = """        def group_items(items):
            under_26 = []; between_26_43 = []; above_43 = []
            if not items:
                return (under_26, between_26_43, above_43)
            for item in items:
                area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                try:
                    area = float(area_val)
                except:
                    area = 0.0
                if area < 26.0:
                    under_26.append(item)
                elif area < 43.0:
                    between_26_43.append(item)
                else:
                    above_43.append(item)
            return (under_26, between_26_43, above_43)"""
    content = re.sub(r'        def group_items\(items\):.*?        report_lines.append\("■ \[매매\] 시세 요약"\)', new_group_items + '\n        report_lines.append("■ [매매] 시세 요약")', content, flags=re.DOTALL)

    # 8. fix classify_by_floor
    new_classify_by_floor = r"""def classify_by_floor(items):
    basement_list = []
    first_floor_list = []
    upper_floor_list = []
    if not items:
        return (basement_list, first_floor_list, upper_floor_list)
    for item in items:
        try:
            flr_str = str(item.get("floor", "")).strip()
            if not flr_str:
                flr_str = str(item.get("flrNo", "")).strip()
            if "지하" in flr_str or "B" in flr_str.upper() or "-" in flr_str:
                basement_list.append(item)
                continue
            import re
            clean_flr = re.sub(r"\\D", "", flr_str)
            if clean_flr:
                flr_num = int(clean_flr)
                if flr_num == 1:
                    first_floor_list.append(item)
                else:
                    upper_floor_list.append(item)
            else:
                upper_floor_list.append(item)
        except:
            upper_floor_list.append(item)
    return (basement_list, first_floor_list, upper_floor_list)"""
    content = re.sub(r'def classify_by_floor\(items\):.*?def get_numeric_averages\(', new_classify_by_floor.replace('\\\\', '\\\\\\\\') + '\ndef get_numeric_averages(', content, flags=re.DOTALL)

    # 9. fix get_cma_ref_price
    content = content.replace(
        '        return (base_avg / 0.65, "지하층 평균가 대비 지상층 추정가")\n    \n    return (None, None)',
        '        return (base_avg / 0.65, "지하층 평균가 대비 지상층 추정가")\n    return (None, None)\n    \n    return (None, None)'
    )
    if 'return (base_avg / 0.65, "지하층 평균가 대비 지상층 추정가")\n    return (None, None)' not in content:
        content = content.replace(
            '        return (base_avg / 0.65, "지하층 평균가 대비 지상층 추정가")',
            '        return (base_avg / 0.65, "지하층 평균가 대비 지상층 추정가")\n    return (None, None)'
        )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed all in {file_path}")

fix_all(r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py')
fix_all(r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py')
