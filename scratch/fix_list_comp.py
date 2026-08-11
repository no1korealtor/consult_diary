import re

def fix_list_comp(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern for trades:
    # [t for t in trades if not get_group_for_item(t, apt_groups) == g]
    # g_trades = ", ".join(cond_parts)
    # t = ", ".join(cond_parts)
    # report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_trades, is_rent=False)}")
    
    pattern_trades = re.compile(
        r'\[t for t in trades if not get_group_for_item\(t, apt_groups\) == g\]\s*\n\s*g_trades = ", "\.join\(cond_parts\)\s*\n\s*t = ", "\.join\(cond_parts\)',
        re.MULTILINE
    )
    content = pattern_trades.sub(r'g_trades = [t for t in trades if get_group_for_item(t, apt_groups) == g]', content)
    
    # Pattern for jeonses:
    pattern_jeonses = re.compile(
        r'\[t for t in jeonses if not get_group_for_item\(t, apt_groups\) == g\]\s*\n\s*g_jeonses = ", "\.join\(cond_parts\)\s*\n\s*t = ", "\.join\(cond_parts\)',
        re.MULTILINE
    )
    content = pattern_jeonses.sub(r'g_jeonses = [t for t in jeonses if get_group_for_item(t, apt_groups) == g]', content)

    # Pattern for wolses:
    pattern_wolses = re.compile(
        r'\[t for t in wolses if not get_group_for_item\(t, apt_groups\) == g\]\s*\n\s*g_wolses = ", "\.join\(cond_parts\)\s*\n\s*t = ", "\.join\(cond_parts\)',
        re.MULTILINE
    )
    content = pattern_wolses.sub(r'g_wolses = [t for t in wolses if get_group_for_item(t, apt_groups) == g]', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {file_path}")

fix_list_comp(r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py')
fix_list_comp(r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py')
