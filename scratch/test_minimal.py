import os
import sys

from trade_viewer import save_briefing_report

sys.stdout.reconfigure(encoding='utf-8')

address = "서울 중구 신당동 395"
prop_type_name = "아파트"
trades = [{"excluUseAr": "84.9", "dealAmount": "85,000", "dealYear": 2026, "dealMonth": 5, "dealDay": "15", "floor": "5"}]
jeonses = []
wolses = []

print("Running save_briefing_report...")
save_briefing_report(address, trades, jeonses, wolses, prop_type_name, "1년", False, None, 0.0, 0, None, "none")
print("Files in 시세브리핑:")
if os.path.exists("시세브리핑"):
    print(os.listdir("시세브리핑"))
else:
    print("Directory not found")
