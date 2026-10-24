# -*- coding: utf-8 -*-
with open("AutoBot_Clean/trade_viewer.py", "r", encoding="utf-8") as f:
    text = f.read()

bad_str = 'print("\n 🎯 [개발지/모아타운 지분가 분석] 대지지분 구간별 평당가 비교 (최근 24개월)")'
good_str = 'print("\\n 🎯 [개발지/모아타운 지분가 분석] 대지지분 구간별 평당가 비교 (최근 24개월)")'

text = text.replace(bad_str, good_str)

with open("AutoBot_Clean/trade_viewer.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed newline in trade_viewer.py")
