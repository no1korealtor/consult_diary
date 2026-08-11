import sys

def patch_filter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "def filter_by_size_category(" not in content:
        filter_func = """
def filter_by_size_category(items, target_area, prop_type_name, apt_groups):
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
        return items
"""
        content = filter_func + "\n" + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print(f"Already patched {file_path}")

patch_filter('trade_viewer.py')
