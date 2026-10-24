with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace debug line
content = content.replace('if target_area else ""\n            print(f"DEBUG: target_area={target_area}, target_label={target_label}")', 'if target_area else ""')

# Add target_apt_groups logic
old_logic = '''            if prop_type_name == "아파트" and apt_groups:
                for g in apt_groups:'''
new_logic = '''            target_apt_groups = set()
            if prop_type_name == "아파트" and apt_groups and target_bld_nm:
                all_txs_for_title = trades + jeonses + wolses
                for item in all_txs_for_title:
                    apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                    if apt_nm == target_bld_nm:
                        g_for_item = get_group_for_item(item, apt_groups)
                        if g_for_item:
                            target_apt_groups.add(g_for_item["label"])

            if prop_type_name == "아파트" and apt_groups:
                for g in apt_groups:'''
content = content.replace(old_logic, new_logic)

# Replace label check
old_check = '''                    label_str = g["label"]
                    if label_str == target_label:
                        label_str += "<br/><font color='#D69E2E'><b>[목적 평형]</b></font>"'''
new_check = '''                    label_str = g["label"]
                    if label_str == target_label or label_str in target_apt_groups:
                        label_str += "<br/><font color='#D69E2E'><b>[목적 평형]</b></font>"'''
content = content.replace(old_check, new_check)

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
