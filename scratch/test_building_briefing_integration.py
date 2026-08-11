import os
import shutil
from datetime import datetime
from building_viewer import save_building_report

def test_integration():
    import time
    # 1. Clean old reports
    if os.path.exists("건축물대장"):
        try:
            shutil.rmtree("건축물대장")
            time.sleep(0.3)
        except:
            pass
        
    # 2. Mock data
    address = "서울특별시 마포구 모래내로7길 52-3"
    
    bld_data = {
        "address": address,
        "bld_nm": "성산빌라",
        "dong_nm": "",
        "ho_name": "201",
        "is_jibbap": True,
        "plat_area": "150.5",
        "lndcgr": "대",
        "use_zone": "제2종일반주거지역",
        "land_price_year": 2026,
        "land_price_m2": 4500000,
        "arch_area": "80.2",
        "tot_area": "350.5",
        "vl_rat_tot_area": "320.2",
        "structure": "철근콘크리트구조",
        "main_purp": "공동주택",
        "grnd_cnt": "4",
        "ugrnd_cnt": "0",
        "hhld": 8,
        "fmly": 0,
        "parking": 6,
        "apr_day": "2015-05-12",
        "viol_str": "정상 (위반 없음)",
        "indiv_house_price_year": None,
        "indiv_house_price": None,
        "reg_info": {
            "moatown": True,
            "moatown_name": "성산동 모아타운",
            "redev": False,
            "redev_name": "",
            "permit": False,
            "permit_name": "",
            "regulated": False,
            "regulated_name": ""
        },
        "ho_details": {
            "flr_no": 2,
            "area": 42.5,
            "supply_area": 55.2,
            "land_share": "18.5",
            "viol_yn": "N",
            "apt_price_year": 2026,
            "apt_price": 250000000
        },
        "expos_list_count": 8,
        "floor_map": {
            "1": ["101", "102"],
            "2": ["201", "202"],
            "3": ["301", "302"],
            "4": ["401", "402"]
        },
        "distinct_dongs": None
    }
    
    # 3. Call save_building_report
    print("Running save_building_report...")
    save_building_report(address, bld_data)
    
    # 4. Assert files are created
    safe_addr = "서울특별시_마포구_모래내로7길_52-3"
    txt_path = f"건축물대장/건축물대장_{safe_addr}.txt"
    pdf_path = f"건축물대장/건축물대장_{safe_addr}.pdf"
    
    assert os.path.exists(txt_path), "TXT building report not created!"
    assert os.path.exists(pdf_path), "PDF building report not created!"
    
    with open(txt_path, "r", encoding="utf-8") as f:
        txt_content = f.read()
    
    assert "**빌라" in txt_content, "Building name was not masked as expected (**빌라)"
    assert "***호" in txt_content, "Ho name was not masked as expected (***호)"
    assert "엘리베이터: ❌ 없음 (⚠️ 4층 이상 엘리베이터 없음 - 감가요인)" in txt_content, "Elevator depreciation warning not found in txt!"
    
    # 5. Test with elevator present
    bld_data["elvt_cnt"] = 1
    bld_data["ride_elvt"] = 1
    bld_data["emgen_elvt"] = 0
    save_building_report(address, bld_data)
    
    with open(txt_path, "r", encoding="utf-8") as f:
        txt_content_with_elvt = f.read()
        
    assert "엘리베이터: 있음 (승용 1대 / 비상용 0대)" in txt_content_with_elvt, "Elevator count info not found in txt!"
    assert "감가요인" not in txt_content_with_elvt, "Depreciation warning should not be in txt when elevator exists!"
    
    print(f"Success! TXT size: {os.path.getsize(txt_path)} bytes")
    print(f"Success! PDF size: {os.path.getsize(pdf_path)} bytes")
    print("Building briefing integration test passed successfully!")

if __name__ == "__main__":
    test_integration()
