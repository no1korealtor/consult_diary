with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add target_apt_groups logic to save_briefing_report
old_txt_logic = '''        def group_items(items):'''
new_txt_logic = '''        target_apt_groups = set()
        if prop_type_name == "아파트" and apt_groups and target_bld_nm:
            all_txs_for_title = trades + jeonses + wolses
            for item in all_txs_for_title:
                apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                if apt_nm == target_bld_nm:
                    g_for_item = get_group_for_item(item, apt_groups)
                    if g_for_item:
                        target_apt_groups.add(g_for_item["label"])
                        
        def group_items(items):'''
content = content.replace(old_txt_logic, new_txt_logic)

# For trades
old_trades = '''                g_trades = [t for t in trades if get_group_for_item(t, apt_groups) == g]
                if g_trades:
                    report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_trades, is_rent=False)}")'''
new_trades = '''                g_trades = [t for t in trades if get_group_for_item(t, apt_groups) == g]
                if g_trades:
                    label_str = g['label']
                    if label_str in target_apt_groups:
                        label_str += " [목적 아파트 평형]"
                    report_lines.append(f"  {idx + 1}) {label_str}: {get_subset_info(g_trades, is_rent=False)}")'''
content = content.replace(old_trades, new_trades)

# For jeonses
old_jeonses = '''                g_jeonses = [t for t in jeonses if get_group_for_item(t, apt_groups) == g]
                if g_jeonses:
                    report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_jeonses, is_rent=True)}")'''
new_jeonses = '''                g_jeonses = [t for t in jeonses if get_group_for_item(t, apt_groups) == g]
                if g_jeonses:
                    label_str = g['label']
                    if label_str in target_apt_groups:
                        label_str += " [목적 아파트 평형]"
                    report_lines.append(f"  {idx + 1}) {label_str}: {get_subset_info(g_jeonses, is_rent=True)}")'''
content = content.replace(old_jeonses, new_jeonses)

# For wolses
old_wolses = '''                g_wolses = [t for t in wolses if get_group_for_item(t, apt_groups) == g]
                if g_wolses:
                    report_lines.append(f"  {idx + 1}) {g['label']}: {get_subset_info(g_wolses, is_rent=True, is_wolse=True)}")'''
new_wolses = '''                g_wolses = [t for t in wolses if get_group_for_item(t, apt_groups) == g]
                if g_wolses:
                    label_str = g['label']
                    if label_str in target_apt_groups:
                        label_str += " [목적 아파트 평형]"
                    report_lines.append(f"  {idx + 1}) {label_str}: {get_subset_info(g_wolses, is_rent=True, is_wolse=True)}")'''
content = content.replace(old_wolses, new_wolses)


with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
