from trade_viewer import get_recent_transactions

print("--- Query 1: Without filters ---")
txs_all = get_recent_transactions("11440", "402", "0", "4", "망원동")
print(f"Total without filters: {len(txs_all)}")

if txs_all:
    first_item = txs_all[0]
    by = first_item.get('buildYear')
    ht = first_item.get('houseType')
    print(f"First item buildYear: {by}, houseType: {ht}")
    
    if by:
        by_int = int(by)
        print(f"\n--- Query 2: Filtering by buildYear {by_int} ---")
        txs_by = get_recent_transactions("11440", "402", "0", "4", "망원동", target_build_year=by_int)
        print(f"Total with buildYear={by_int}: {len(txs_by)}")
        for t in txs_by[:5]:
            print(f"  Date: {t.get('dealYear')}-{t.get('dealMonth')}, Type: {t.get('_trade_type')}, buildYear: {t.get('buildYear')}, houseType: {t.get('houseType')}, Area: {t.get('totalFloorAr') or t.get('excluUseAr')}")
            
    if ht:
        print(f"\n--- Query 3: Filtering by houseType '{ht}' and buildYear '{by}' ---")
        txs_both = get_recent_transactions("11440", "402", "0", "4", "망원동", target_build_year=by_int, target_house_type=ht)
        print(f"Total with both: {len(txs_both)}")
