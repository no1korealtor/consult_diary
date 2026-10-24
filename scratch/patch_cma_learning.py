import os

def patch_cma_learning(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    save_func_code = """
import json
from datetime import datetime

def save_learned_comps(address_name, bjdong_nm, transactions, prop_type, is_dev_zone):
    db_path = "learned_cma_db.json"
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        except:
            db = []
    else:
        db = []
        
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target_address": address_name,
        "bjdong_nm": bjdong_nm,
        "prop_type": prop_type,
        "is_dev_zone": is_dev_zone,
        "transaction_count": len(transactions),
        "transactions": transactions
    }
    db.append(record)
    
    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"\\n [DB 저장 완료] 나만의 중개 DB(learned_cma_db.json)에 거래 사례 {len(transactions)}건이 학습(저장)되었습니다.")
    except Exception as e:
        print(f"\\n [!] DB 저장 실패: {e}")

"""

    # Inject the function definition before if __name__ == "__main__":
    if "def save_learned_comps" not in content:
        content = content.replace('if __name__ == "__main__":', save_func_code + '\nif __name__ == "__main__":')

    # Inject the function call inside run_trade_viewer
    old_call = """        print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd=addr_info["sigunguCd"], bun=addr_info["bun"], ji=addr_info["ji"], bjdong_nm=addr_info.get("bjdongNm"), target_build_year=target_build_year, target_house_type=target_house_type, save_report=pre_address_info is None, target_bld_nm=bld_name, is_dev_zone=is_dev_zone)
    else:"""
    
    new_call = """        print_comparison_table(transactions, prop_type, target_floor, target_area, address_name, sigunguCd=addr_info["sigunguCd"], bun=addr_info["bun"], ji=addr_info["ji"], bjdong_nm=addr_info.get("bjdongNm"), target_build_year=target_build_year, target_house_type=target_house_type, save_report=pre_address_info is None, target_bld_nm=bld_name, is_dev_zone=is_dev_zone)
        
        if pre_address_info is None:
            save_learned_comps(address_name, addr_info.get("bjdongNm"), transactions, prop_type, is_dev_zone)
    else:"""
    
    if "save_learned_comps(address_name" not in content:
        content = content.replace(old_call, new_call)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Patch CMA Learning successful!")

if __name__ == '__main__':
    patch_cma_learning(r"d:\부동산업무\antigravity\AutoBot_Clean\trade_viewer.py")
