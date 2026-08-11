import sys
from trade_viewer import get_recent_transactions

print("Querying transactions for 성산동...")
txs = get_recent_transactions("11440", "", "", "1", bjdong_nm="성산동", expand_similar=True)
print(f"Total transactions found: {len(txs)}")

# Group and print unique apartments
apt_info = {}
for t in txs:
    name = t.get('aptNm', '')
    if name:
        if name not in apt_info:
            apt_info[name] = {
                'dong': t.get('umdNm') or t.get('dong'),
                'jibun': t.get('jibun'),
                'count': 0
            }
        apt_info[name]['count'] += 1

print("\nList of apartments in 성산동 according to MOLIT database:")
for idx, (name, info) in enumerate(sorted(apt_info.items(), key=lambda x: x[1]['count'], reverse=True)):
    print(f"[{idx+1}] {name} (Dong: {info['dong']}, Jibun: {info['jibun']}, Count: {info['count']})")

