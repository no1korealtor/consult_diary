import os

with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Fix line 618 corruption
start = -1
end = -1
for i, line in enumerate(lines):
    if line.strip() == 'is_wolse = int(monthly_val) > 0':
        start = i
        pass
    if line.strip() == 'def save_briefing_report(address, trades, jeonses, wolses, prop_type_name, period_label, is_expanded, target_build_year, target_area, target_floor, desired_info, expansion_mode):':
        end = i
        break

replacement1 = """            is_wolse = int(monthly_val) > 0
            item["_trade_type"] = "월세" if is_wolse else "전세"
            matches.append(item)
    return matches
"""

# wait, we must not overwrite save_briefing_report! 
# We need to find the next function which is probably calculate_subset_stats or something!
# Let's see what was after filter_jeonse_wolse!
