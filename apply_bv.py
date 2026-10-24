import os

with open('building_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_call = '''save_briefing_report(display_addr, trades, jeonses, wolses, prop_type_name, period_label=selected_label, is_expanded=is_expanded, target_build_year=target_build_year, target_area=target_area, target_floor=target_floor, desired_info=desired_info, target_bld_nm=bld_data.get("bld_nm"))'''
new_call = '''save_briefing_report(display_addr, trades, jeonses, wolses, prop_type_name, period_label=selected_label, is_expanded=is_expanded, target_build_year=target_build_year, target_area=target_area, target_floor=target_floor, desired_info=desired_info, target_bld_nm=bld_data.get("bld_nm"), target_bun=addr_info.get("bun"), target_ji=addr_info.get("ji"))'''
content = content.replace(old_call, new_call)

with open('building_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
