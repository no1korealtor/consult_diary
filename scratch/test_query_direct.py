import urllib.request
import urllib.parse
import json
import requests

from trade_viewer import classify_property_type, get_recent_transactions, print_comparison_table
from building_viewer import get_kakao_address_info, get_building_title_info

def run_test():
    address = "마포구 신수동 34-15"
    print(f"--- Querying address: {address} ---")
    
    addr_info = get_kakao_address_info(address)
    print("Address Info from Kakao:", addr_info)
    
    if not addr_info:
        print("Failed to get Kakao address info")
        return
        
    print("\n--- Fetching Building Title Info ---")
    titles = get_building_title_info(addr_info['sigunguCd'], addr_info['bjdongCd'], addr_info['bun'], addr_info['ji'])
    print("Building Titles Count:", len(titles) if titles else 0)
    
    if titles:
        title = titles[0]
        print("Selected Title:", {
            'bldNm': title.get('bldNm'),
            'dongNm': title.get('dongNm'),
            'mainPurpsCdNm': title.get('mainPurpsCdNm'),
            'etcPurps': title.get('etcPurps'),
            'regstrGbCd': title.get('regstrGbCd'),
            'regstrGbCdNm': title.get('regstrGbCdNm'),
            'useAprDay': title.get('useAprDay')
        })
        
        main_purp = title.get('mainPurpsCdNm', '')
        bld_name = title.get('bldNm', '')
        etc_purp = title.get('etcPurps', '')
        prop_type = classify_property_type(main_purp, bld_name, etc_purp)
        print("Classified Property Type:", prop_type)
    else:
        print("No building titles found, defaulting to type 2 (Rowhouse/Villa)")
        prop_type = '2'
        
    print("\n--- Querying Transactions as Classified Type ---")
    # 1. As classified type
    txs = get_recent_transactions(addr_info['sigunguCd'], addr_info['bun'], addr_info['ji'], prop_type, addr_info.get('bjdongNm'))
    print(f"Transactions found as Type {prop_type}:", len(txs) if txs is not None else "None")
    
    # 2. Let's query as Single-Family/Multi-Family (Type 4) to see if there are transactions!
    print("\n--- Querying Transactions as Single-Family/Multi-Family (Type 4) ---")
    txs_4 = get_recent_transactions(addr_info['sigunguCd'], addr_info['bun'], addr_info['ji'], '4', addr_info.get('bjdongNm'))
    print("Transactions found as Type 4 (Single-family/Multi-family):", len(txs_4) if txs_4 is not None else "None")
    if txs_4:
        for t in txs_4[:5]:
            print(f"Type 4 Tx: {t.get('_trade_type')} | {t.get('dealYear')}-{t.get('dealMonth')} | Area: {t.get('totalFloorAr')} | Amt: {t.get('dealAmount') or t.get('deposit')}")
            
    # 3. Let's query as Rowhouse/Villa (Type 2) to see if there are transactions!
    print("\n--- Querying Transactions as Rowhouse/Villa (Type 2) ---")
    txs_2 = get_recent_transactions(addr_info['sigunguCd'], addr_info['bun'], addr_info['ji'], '2', addr_info.get('bjdongNm'))
    print("Transactions found as Type 2 (Rowhouse/Villa):", len(txs_2) if txs_2 is not None else "None")
    if txs_2:
        for t in txs_2[:5]:
            print(f"Type 2 Tx: {t.get('_trade_type')} | {t.get('dealYear')}-{t.get('dealMonth')} | Area: {t.get('excluUseAr')} | Amt: {t.get('dealAmount') or t.get('deposit')}")

if __name__ == '__main__':
    run_test()
