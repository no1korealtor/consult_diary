import sys
import traceback
from trade_viewer import save_briefing_report

sys.stdout.reconfigure(encoding='utf-8')
trades = [{'excluUseAr': '84.9', 'dealAmount': '85,000', 'dealYear': 2026, 'dealMonth': 5, 'dealDay': '15', 'floor': '5'}]
try:
    print("Before call")
    save_briefing_report('서울 중구 신당동 395', trades, [], [], '아파트', '1년', False, None, 0.0, 0, None, 'none')
    print("After call")
except Exception as e:
    print("CAUGHT IN OUTER SCRIPT!")
    traceback.print_exc()
