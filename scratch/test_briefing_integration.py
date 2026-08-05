import os
import shutil
from trade_viewer import save_briefing_report

def test_integration():
    import time
    # 1. Clean old reports
    if os.path.exists("시세브리핑"):
        try:
            shutil.rmtree("시세브리핑", ignore_errors=True)
            time.sleep(0.3)
        except:
            pass
        
    # 2. Mock data
    address = "서울특별시 마포구 중동 395"
    prop_type_name = "아파트"
    
    trades = [
        {"excluUseAr": "84.9", "dealAmount": "85,000", "dealYear": 2026, "dealMonth": 5, "dealDay": 10},
        {"excluUseAr": "84.8", "dealAmount": "86,000", "dealYear": 2026, "dealMonth": 6, "dealDay": 12},
        {"excluUseAr": "59.9", "dealAmount": "62,000", "dealYear": 2026, "dealMonth": 5, "dealDay": 11}
    ]
    
    jeonses = [
        {"excluUseAr": "84.9", "deposit": "52,000", "monthlyRent": "0", "dealYear": 2026, "dealMonth": 5, "dealDay": 20},
        {"excluUseAr": "59.9", "deposit": "42,000", "monthlyRent": "0", "dealYear": 2026, "dealMonth": 6, "dealDay": 1}
    ]
    
    wolses = [
        {"excluUseAr": "84.9", "deposit": "10,000", "monthlyRent": "180", "dealYear": 2026, "dealMonth": 5, "dealDay": 22}
    ]
    
    # 3. Call save_briefing_report
    print("Running save_briefing_report...")
    save_briefing_report(address, trades, jeonses, wolses, prop_type_name, "1년", False, None, 0.0, 0, None, "none")
    
    # 4. Assert files are created
    safe_addr = "서울특별시마포구중동395"
    txt_path = f"시세브리핑/시세브리핑_{safe_addr}.txt"
    pdf_path = f"시세브리핑/시세브리핑_{safe_addr}.pdf"
    
    assert os.path.exists(txt_path), "TXT briefing report not created!"
    assert os.path.exists(pdf_path), "PDF briefing report not created!"
    
    print(f"Success! TXT size: {os.path.getsize(txt_path)} bytes")
    print(f"Success! PDF size: {os.path.getsize(pdf_path)} bytes")
    print("Integration test passed successfully!")

def test_custom_price_evaluation():
    import time
    # 1. Clean old reports
    if os.path.exists("시세브리핑"):
        try:
            shutil.rmtree("시세브리핑", ignore_errors=True)
            time.sleep(0.3)
        except:
            pass
        
    address = "서울특별시 마포구 중동 395"
    prop_type_name = "아파트"
    
    # 84.9 size category average is 85,500
    trades = [
        {"excluUseAr": "84.9", "dealAmount": "85,000", "dealYear": 2026, "dealMonth": 5, "dealDay": 10},
        {"excluUseAr": "84.9", "dealAmount": "86,000", "dealYear": 2026, "dealMonth": 6, "dealDay": 12}
    ]
    jeonses = []
    wolses = []
    
    # Evaluation case 1: Appropriate
    desired_info_appr = {"trade_type": "매매", "price": 85000, "monthly_rent": 0, "phone_number": "010-1234-5678"}
    save_briefing_report(
        address, trades, jeonses, wolses, prop_type_name, 
        target_area=84.9, target_floor=3, desired_info=desired_info_appr
    )
    
    safe_addr = "서울특별시마포구중동395"
    txt_path = f"시세브리핑/시세브리핑_{safe_addr}.txt"
    pdf_path = f"시세브리핑/시세브리핑_{safe_addr}.pdf"
    
    assert os.path.exists(txt_path), "TXT briefing report not created!"
    assert os.path.exists(pdf_path), "PDF briefing report not created!"
    
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "희망 거래가 분석 및 적정성 평가" in content
    
    print("Success! Custom price evaluation generated.")
    assert "매매 8억 5,000만" in content
    assert "의뢰인 연락처  : 010-****-5678" in content
    assert "적절함" in content
    
    # Evaluation case 2: High
    desired_info_high = {"trade_type": "매매", "price": 95000, "monthly_rent": 0}
    save_briefing_report(
        address, trades, jeonses, wolses, prop_type_name, 
        target_area=84.9, target_floor=3, desired_info=desired_info_high
    )
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "높음" in content
    
    # Evaluation case 3: Low
    desired_info_low = {"trade_type": "매매", "price": 70000, "monthly_rent": 0}
    save_briefing_report(
        address, trades, jeonses, wolses, prop_type_name, 
        target_area=84.9, target_floor=3, desired_info=desired_info_low
    )
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "저렴함" in content
    
    print("Custom price evaluation test passed successfully!")

def test_optional_price_evaluation():
    address = "서울특별시 마포구 중동 395"
    prop_type_name = "아파트"
    
    trades = [
        {"excluUseAr": "84.9", "dealAmount": "85,000", "dealYear": 2026, "dealMonth": 5, "dealDay": 10},
        {"excluUseAr": "84.9", "dealAmount": "86,000", "dealYear": 2026, "dealMonth": 6, "dealDay": 12}
    ]
    jeonses = []
    wolses = []
    
    # Desired info exists, but price and monthly_rent are 0
    desired_info_empty = {"trade_type": "매매", "price": 0, "monthly_rent": 0, "phone_number": "010-1234-5678"}
    save_briefing_report(
        address, trades, jeonses, wolses, prop_type_name, 
        target_area=84.9, target_floor=3, desired_info=desired_info_empty
    )
    
    safe_addr = "서울특별시마포구중동395"
    txt_path = f"시세브리핑/시세브리핑_{safe_addr}.txt"
    pdf_path = f"시세브리핑/시세브리핑_{safe_addr}.pdf"
    
    assert os.path.exists(txt_path), "TXT briefing report not created!"
    assert os.path.exists(pdf_path), "PDF briefing report not created!"
    
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()
        

    assert "희망 거래가 분석 및 적정성 평가" in content
    assert "미지정 (시세 정보 브리핑)" in content
    assert "정보 (인근 시세 및 실거래 브리핑)" in content
    
    print("Optional price evaluation test passed successfully!")

if __name__ == "__main__":
    test_integration()
    test_custom_price_evaluation()
    test_optional_price_evaluation()
