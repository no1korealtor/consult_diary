import sys

def patch_final(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    funcs = """
def classify_by_floor(items):
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
            clean_flr = re.sub(r"\D", "", flr_str)
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
    return (basement_list, first_floor_list, upper_floor_list)

def get_cma_ref_price(items, floor_cat, is_rent=False, is_wolse=False):
    base_t, first_t, upper_t = classify_by_floor(items)
    target_list = upper_t
    if floor_cat == "base":
        target_list = base_t
    elif floor_cat == "first":
        target_list = first_t
        
    stats = calculate_subset_stats(target_list, is_rent, is_wolse)
    if not stats:
        return (None, "비교 사례 부족")
        
    try:
        avg_val = int(stats['avg'].replace(",", "").replace("만", "").replace("억 ", "0000").replace("억", "0000"))
    except:
        avg_val = 0
        
    desc_map = {"base": "지하층", "first": "1층", "upper": "2층이상(지상층)"}
    return (avg_val, f"{desc_map.get(floor_cat, '')} 평균가")

def mask_phone_number(phone):
    if not phone: return ""
    import re
    return re.sub(r'(\d{2,3})-(\d{3,4})-(\d{4})', r'\1-****-\3', phone)

def format_member_name(name):
    return name

def load_member_info():
    return None

def get_apartment_size_groups(items):
    return []

def get_group_for_item(item, groups):
    return None
"""
    if "def classify_by_floor(" not in content:
        content = funcs + "\n" + content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {file_path}")
    else:
        print("already patched")

patch_final('trade_viewer.py')
