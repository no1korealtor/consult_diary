from trade_viewer import get_recent_transactions, print_comparison_table
import json
import unittest.mock

sigungu = "11440"
bun = "138"
ji = "0"
prop_type = "2"
bjdong_nm = "성산동"
target_build_year = 2021
target_area = 30.95
target_floor = 3

print("Running get_recent_transactions for 성산동 138...")
transactions = get_recent_transactions(
    sigungu, bun, ji, prop_type, bjdong_nm,
    target_build_year=target_build_year,
    expand_similar=True,
    target_area=target_area
)

print(f"Total transactions found: {len(transactions) if transactions else 0}")
if transactions:
    trades = [t for t in transactions if t.get('_trade_type') == '매매']
    jeonses = [t for t in transactions if t.get('_trade_type') == '전세']
    wolses = [t for t in transactions if t.get('_trade_type') == '월세']
    print(f"Trades: {len(trades)}")
    print(f"Jeonses: {len(jeonses)}")
    print(f"Wolses: {len(wolses)}")

    desired_info = {
        "trade_type": "전세",
        "price": 15000,
        "monthly_rent": 0,
        "phone_number": "010-9128-0586"
    }

    with unittest.mock.patch('builtins.input', return_value='2'):
        trades_ret, jeonses_ret, wolses_ret, prop_type_name, selected_label, is_expanded = print_comparison_table(
            transactions, prop_type, target_floor, target_area, "성산동 138",
            sigunguCd=sigungu, bun=bun, ji=ji, bjdong_nm=bjdong_nm,
            target_build_year=target_build_year,
            save_report=True, desired_info=desired_info
        )
        
    print("\n--- Output of print_comparison_table call ---")
    print(f"Trades returned: {len(trades_ret)}")
    print(f"Jeonses returned: {len(jeonses_ret)}")
    print(f"Wolses returned: {len(wolses_ret)}")

    import os
    report_files = os.listdir("시세브리핑")
    print("\nGenerated report files:", report_files)
    for rf in report_files:
        if "138" in rf and rf.endswith(".txt"):
            print(f"\n--- Content of 시세브리핑/{rf} ---")
            with open(f"시세브리핑/{rf}", "r", encoding="utf-8") as f:
                print(f.read())
