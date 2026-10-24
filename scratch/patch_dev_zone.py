import re

def patch_trade_viewer(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add is_dev_zone to print_comparison_table signature
    content = content.replace(
        "def print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd, bun, ji, bjdong_nm, target_build_year, target_house_type, save_report, desired_info=None, target_bld_nm=None):",
        "def print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd, bun, ji, bjdong_nm, target_build_year, target_house_type, save_report, desired_info=None, target_bld_nm=None, is_dev_zone=False):"
    )

    # 2. Modify run_trade_viewer to ask for is_dev_zone
    old_input = """        address = sys.argv[1] if len(sys.argv) > 1 else input("\\n[입력] 조회할 주소: ").strip()
        if not address or address.lower() == "q":
            return"""
    
    new_input = """        address = sys.argv[1] if len(sys.argv) > 1 else input("\\n[입력] 조회할 주소: ").strip()
        if not address or address.lower() == "q":
            return
            
        is_dev_zone = False
        if len(sys.argv) <= 1 and not pre_address_info:
            dev_zone_input = input(" [선택] 해당 지역이 정비사업 구역(개발지)입니까? (y/n, 기본: n): ").strip().lower()
            if dev_zone_input == 'y':
                is_dev_zone = True"""
    content = content.replace(old_input, new_input)

    # 3. Pass is_dev_zone to print_comparison_table call inside run_trade_viewer
    old_print_call = """        print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd=addr_info["sigunguCd"], bun=addr_info["bun"], ji=addr_info["ji"], bjdong_nm=addr_info.get("bjdongNm"), target_build_year=target_build_year, target_house_type=target_house_type, save_report=pre_address_info is None, target_bld_nm=bld_name)"""
    new_print_call = """        print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd=addr_info["sigunguCd"], bun=addr_info["bun"], ji=addr_info["ji"], bjdong_nm=addr_info.get("bjdongNm"), target_build_year=target_build_year, target_house_type=target_house_type, save_report=pre_address_info is None, target_bld_nm=bld_name, is_dev_zone=is_dev_zone)"""
    content = content.replace(old_print_call, new_print_call)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patch successful!")

if __name__ == '__main__':
    patch_trade_viewer(r"d:\부동산업무\antigravity\AutoBot_Clean\trade_viewer.py")
