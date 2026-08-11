from trade_viewer import get_recent_transactions

# Let's query recent transactions for Mapo-gu, Mangwon-dong (sigungu: 11440, bun: 402, ji: 0, prop_type: '4')
# '4' is Single house/Multi-family (단독/다가구)
print("Querying for prop_type '4' (단독/다가구)")
transactions = get_recent_transactions("11440", "402", "0", "4", "망원동")
if transactions is not None:
    print(f"Total transactions found: {len(transactions)}")
    trades = [t for t in transactions if t.get('_trade_type') == '매매']
    jeonses = [t for t in transactions if t.get('_trade_type') == '전세']
    wolses = [t for t in transactions if t.get('_trade_type') == '월세']
    print(f"매매: {len(trades)}, 전세: {len(jeonses)}, 월세: {len(wolses)}")
else:
    print("Failed or returned None")
