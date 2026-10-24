# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, "AutoBot_Clean")

from market_analyser import generate_market_report_pdf, load_member_info
from trade_viewer import get_recent_transactions

sigunguCd = "11440"
bjdong = "중동"
print(f"Fetching transactions for {bjdong}...")
txs = get_recent_transactions(sigunguCd, '', '', '2', bjdong_nm=bjdong, expand_similar=True)
print(f"Fetched {len(txs)} transactions.")

test_pdf = "AutoBot_Clean/reports/test_new_report.pdf"
member_info = load_member_info()
print("Generating PDF...")
generate_market_report_pdf(test_pdf, "성산2동 (성산동, 중동)", txs, member_info, region_prefix="서울특별시 마포구")
print(f"Generated {test_pdf}, size: {os.path.getsize(test_pdf):,} bytes")

import fitz
doc = fitz.open(test_pdf)
print(f"PDF Page count: {len(doc)}")
for i in range(len(doc)):
    txt = doc[i].get_text()
    has_target = "대지지분 평당가 분석" in txt or "신축/구축 듀얼 곡선" in txt
    print(f"Page {i+1}: length={len(txt)}, contains_land_analysis={has_target}")
