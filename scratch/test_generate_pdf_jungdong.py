import json
import os
from unittest.mock import patch
from trade_viewer import get_recent_transactions, get_kakao_address_info, print_comparison_table

def main():
    addr = "마포구 중동 393"
    print(f"Testing PDF generation for: {addr}")
    addr_info = get_kakao_address_info(addr)
    if not addr_info:
        print("Failed to get address info.")
        return
        
    transactions = get_recent_transactions(
        addr_info['sigunguCd'], 
        addr_info['bun'], 
        addr_info['ji'], 
        '1', 
        bjdong_nm=addr_info.get('bjdongNm')
    )
    
    if transactions is None:
        print("Failed to get transactions.")
        return
        
    print(f"Retrieved {len(transactions)} transactions.")
    
    # Mock input to return:
    # 1. '3' for 2-year analysis period
    # 2. '1' for expansion/strict mode
    with patch('builtins.input', side_effect=['3', '1']):
        trades, jeonses, wolses, prop_type_name, selected_label, is_expanded = print_comparison_table(
            transactions, 
            '1', 
            target_floor=5, 
            target_area=84.9, 
            address_name=addr,
            sigunguCd=addr_info['sigunguCd'], 
            bun=addr_info['bun'], 
            ji=addr_info['ji'],
            bjdong_nm=addr_info.get('bjdongNm'), 
            target_build_year=None,
            target_house_type=None,
            save_report=True
        )
        
    print("PDF report generation complete!")

if __name__ == '__main__':
    main()
