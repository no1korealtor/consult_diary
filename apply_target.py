import os

with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update save_briefing_report_pdf signature
old_sig1 = '''def save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, filename_pdf, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor, desired_info, expansion_mode, target_bld_nm=None):'''
new_sig1 = '''def save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, filename_pdf, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor, desired_info, expansion_mode, target_bld_nm=None, target_bun=None, target_ji=None):'''
content = content.replace(old_sig1, new_sig1)

# 2. Update target_apt_groups logic in save_briefing_report_pdf
old_logic1 = '''            target_apt_groups = set()
            if prop_type_name == "아파트" and apt_groups and target_bld_nm:
                all_txs_for_title = trades + jeonses + wolses
                for item in all_txs_for_title:
                    apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                    if apt_nm == target_bld_nm:
                        g_for_item = get_group_for_item(item, apt_groups)
                        if g_for_item:
                            target_apt_groups.add(g_for_item["label"])'''
new_logic1 = '''            target_apt_groups = set()
            if prop_type_name == "아파트" and apt_groups:
                all_txs_for_title = trades + jeonses + wolses
                for item in all_txs_for_title:
                    is_target = False
                    if target_bun and target_ji:
                        t_bun = str(item.get("bun", "")).zfill(4)
                        t_ji = str(item.get("ji", "")).zfill(4)
                        if t_bun == str(target_bun).zfill(4) and t_ji == str(target_ji).zfill(4):
                            is_target = True
                    elif target_bld_nm:
                        apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                        if apt_nm == target_bld_nm:
                            is_target = True
                            
                    if is_target:
                        g_for_item = get_group_for_item(item, apt_groups)
                        if g_for_item:
                            target_apt_groups.add(g_for_item["label"])'''
content = content.replace(old_logic1, new_logic1)

# 3. Update save_briefing_report signature
old_sig2 = '''def save_briefing_report(address, trades, jeonses, wolses, prop_type_name, period_label="최근 12개월", is_expanded=False, target_build_year=None, target_area=None, target_floor=None, desired_info=None, expansion_mode=None, target_bld_nm=None):'''
new_sig2 = '''def save_briefing_report(address, trades, jeonses, wolses, prop_type_name, period_label="최근 12개월", is_expanded=False, target_build_year=None, target_area=None, target_floor=None, desired_info=None, expansion_mode=None, target_bld_nm=None, target_bun=None, target_ji=None):'''
content = content.replace(old_sig2, new_sig2)

# 4. Update target_apt_groups logic in save_briefing_report
old_logic2 = '''        target_apt_groups = set()
        if prop_type_name == "아파트" and apt_groups and target_bld_nm:
            all_txs_for_title = trades + jeonses + wolses
            for item in all_txs_for_title:
                apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                if apt_nm == target_bld_nm:
                    g_for_item = get_group_for_item(item, apt_groups)
                    if g_for_item:
                        target_apt_groups.add(g_for_item["label"])'''
new_logic2 = '''        target_apt_groups = set()
        if prop_type_name == "아파트" and apt_groups:
            all_txs_for_title = trades + jeonses + wolses
            for item in all_txs_for_title:
                is_target = False
                if target_bun and target_ji:
                    t_bun = str(item.get("bun", "")).zfill(4)
                    t_ji = str(item.get("ji", "")).zfill(4)
                    if t_bun == str(target_bun).zfill(4) and t_ji == str(target_ji).zfill(4):
                        is_target = True
                elif target_bld_nm:
                    apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                    if apt_nm == target_bld_nm:
                        is_target = True
                        
                if is_target:
                    g_for_item = get_group_for_item(item, apt_groups)
                    if g_for_item:
                        target_apt_groups.add(g_for_item["label"])'''
content = content.replace(old_logic2, new_logic2)

# 5. Update call inside save_briefing_report
old_call1 = '''save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, pdf_filename, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode, target_bld_nm=target_bld_nm)'''
new_call1 = '''save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, pdf_filename, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode, target_bld_nm=target_bld_nm, target_bun=target_bun, target_ji=target_ji)'''
content = content.replace(old_call1, new_call1)

# 6. Update call inside print_comparison_table
old_call2 = '''save_briefing_report_pdf(address_name, trades, jeonses, wolses, prop_type_name, pdf_filename, apt_groups, period_label, True, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode, target_bld_nm=target_bld_nm)'''
new_call2 = '''save_briefing_report_pdf(address_name, trades, jeonses, wolses, prop_type_name, pdf_filename, apt_groups, period_label, True, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode, target_bld_nm=target_bld_nm, target_bun=bun, target_ji=ji)'''
content = content.replace(old_call2, new_call2)

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
