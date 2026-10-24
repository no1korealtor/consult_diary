# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, "AutoBot_Clean")

from trade_viewer import get_recent_transactions
from market_analyser import calculate_villa_land_bracket_stats

sigunguCd = "11440"
txs_jung = get_recent_transactions(sigunguCd, '', '', '2', bjdong_nm='중동', expand_similar=True)
txs_sung = get_recent_transactions(sigunguCd, '', '', '2', bjdong_nm='성산동', expand_similar=True)
all_txs = txs_jung + txs_sung

stats = calculate_villa_land_bracket_stats(all_txs)
print(f"Total valid transactions: {stats['total_valid']}")
print(f"Old count: {stats['old_count']}, New count: {stats['new_count']}")
for b in stats['brackets']:
    print(f"  {b['label']:<15} | {b['old_cnt']+b['new_cnt']}건 | 구축: {b['old_str']} | 신축: {b['new_str']} | 차이: {b['gap_str']}")
