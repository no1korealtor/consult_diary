import re

def patch_trade_viewer(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Modify calculate_subset_stats definition to accept is_dev_zone
    content = content.replace(
        "def calculate_subset_stats(subset, is_rent, is_wolse):",
        "def calculate_subset_stats(subset, is_rent, is_wolse, is_dev_zone=False):"
    )

    # 2. Modify save_briefing_report to accept and pass is_dev_zone
    content = content.replace(
        "def save_briefing_report(address, trades, jeonses, wolses, prop_type_name, apt_name, is_expanded, target_build_year=None, target_area=None, target_floor=None, desired_info=None, expansion_mode=None, target_bld_nm=None):",
        "def save_briefing_report(address, trades, jeonses, wolses, prop_type_name, apt_name, is_expanded, target_build_year=None, target_area=None, target_floor=None, desired_info=None, expansion_mode=None, target_bld_nm=None, is_dev_zone=False):"
    )
    content = content.replace(
        "trade_stats = calculate_subset_stats(target_trades, is_rent=False, is_wolse=False)",
        "trade_stats = calculate_subset_stats(target_trades, is_rent=False, is_wolse=False, is_dev_zone=is_dev_zone)"
    )

    # 3. Update the call to save_briefing_report inside print_comparison_table
    content = content.replace(
        "save_briefing_report(display_addr, trades, jeonses, wolses, prop_type_name, selected_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode, target_bld_nm=target_bld_nm)",
        "save_briefing_report(display_addr, trades, jeonses, wolses, prop_type_name, selected_label, is_expanded, target_build_year, target_area, target_floor=target_floor, desired_info=desired_info, expansion_mode=expansion_mode, target_bld_nm=target_bld_nm, is_dev_zone=is_dev_zone)"
    )

    # 4. Modify print_grouped_stats inside print_comparison_table
    old_grouped = """        def print_grouped_stats(items, label_prefix, is_rent, is_wolse):
            if not items:
                return
            under_26 = []; between_26_43 = []; above_43 = []
            for item in items:
                area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                try: area = float(area_val)
                except: area = 0.0
                if area < 26.0: under_26.append(item)
                elif area < 43.0: between_26_43.append(item)
                else: above_43.append(item)
            print(divider_line)
            print(f" [평균 및 가격 범위 요약] 전체 {len(items)}건 중:")"""

    new_grouped = """        def print_grouped_stats(items, label_prefix, is_rent, is_wolse):
            if not items:
                return
            under_1 = []; under_2 = []; under_3 = []; above_3 = []
            
            for item in items:
                if is_dev_zone:
                    land_val = item.get("landAr") or 0.0
                    try: val = float(land_val)
                    except: val = 0.0
                    if val < 13.2: under_1.append(item)
                    elif val < 26.4: under_2.append(item)
                    elif val < 39.6: under_3.append(item)
                    else: above_3.append(item)
                else:
                    area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                    try: val = float(area_val)
                    except: val = 0.0
                    if val < 26.0: under_1.append(item)
                    elif val < 43.0: under_2.append(item)
                    else: above_3.append(item)
            print(divider_line)
            print(f" [평균 및 가격 범위 요약] 전체 {len(items)}건 중:")"""

    content = content.replace(old_grouped, new_grouped)
    
    # 5. Modify the block that prints the subset stats
    old_print_subset = """            else:
                print_subset_stats(under_26, "전용 26㎡ 미만 (원룸/1.5룸형)")
                print_subset_stats(between_26_43, "전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형)")
                print_subset_stats(above_43, "전용 43㎡ 이상 (쓰리룸 이상형)")"""
                
    new_print_subset = """            else:
                if is_dev_zone:
                    print_subset_stats(under_1, "대지지분 4평 미만 (초소형/뚜껑)")
                    print_subset_stats(under_2, "대지지분 4평~8평 (소형 빌라)")
                    print_subset_stats(under_3, "대지지분 8평~12평 (다세대 중형)")
                    print_subset_stats(above_3, "대지지분 12평 이상 (단독/대형)")
                else:
                    print_subset_stats(under_1, "전용 26㎡ 미만 (원룸/1.5룸형)")
                    print_subset_stats(under_2, "전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형)")
                    print_subset_stats(above_3, "전용 43㎡ 이상 (쓰리룸 이상형)")"""
    content = content.replace(old_print_subset, new_print_subset)

    # 6. Modify calculate_subset_stats body for PDF stats
    old_pdf_grouped = """    under_26 = []; between_26_43 = []; above_43 = []
    for item in subset:
        area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
        try: area = float(area_val)
        except: area = 0.0
        if area < 26.0: under_26.append(item)
        elif area < 43.0: between_26_43.append(item)
        else: above_43.append(item)
        
    def get_group_stats(group_items, group_label):"""

    new_pdf_grouped = """    under_1 = []; under_2 = []; under_3 = []; above_3 = []
    for item in subset:
        if is_dev_zone:
            land_val = item.get("landAr") or 0.0
            try: val = float(land_val)
            except: val = 0.0
            if val < 13.2: under_1.append(item)
            elif val < 26.4: under_2.append(item)
            elif val < 39.6: under_3.append(item)
            else: above_3.append(item)
        else:
            area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
            try: val = float(area_val)
            except: val = 0.0
            if val < 26.0: under_1.append(item)
            elif val < 43.0: under_2.append(item)
            else: above_3.append(item)
        
    def get_group_stats(group_items, group_label):"""
    
    content = content.replace(old_pdf_grouped, new_pdf_grouped)

    # 7. and the pdf list
    old_pdf_list = """    if not is_apt:
        res.append(get_group_stats(under_26, "전용 26㎡ 미만 (원룸/1.5룸형)"))
        res.append(get_group_stats(between_26_43, "전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형)"))
        res.append(get_group_stats(above_43, "전용 43㎡ 이상 (쓰리룸 이상형)"))
        res = [r for r in res if r is not None]
    return res"""
    
    new_pdf_list = """    if not is_apt:
        if is_dev_zone:
            res.append(get_group_stats(under_1, "대지지분 4평 미만 (초소형/뚜껑)"))
            res.append(get_group_stats(under_2, "대지지분 4평~8평 (소형 빌라)"))
            res.append(get_group_stats(under_3, "대지지분 8평~12평 (다세대 중형)"))
            res.append(get_group_stats(above_3, "대지지분 12평 이상 (단독/대형)"))
        else:
            res.append(get_group_stats(under_1, "전용 26㎡ 미만 (원룸/1.5룸형)"))
            res.append(get_group_stats(under_2, "전용 26㎡ 이상 ~ 43㎡ 미만 (투룸형)"))
            res.append(get_group_stats(above_3, "전용 43㎡ 이상 (쓰리룸 이상형)"))
        res = [r for r in res if r is not None]
    return res"""
    content = content.replace(old_pdf_list, new_pdf_list)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patch 2 successful!")

if __name__ == '__main__':
    patch_trade_viewer(r"d:\부동산업무\antigravity\AutoBot_Clean\trade_viewer.py")
