
with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_str = '      • 평균 가격: {stats[\"avg\"]}{suffix}\\n      • 전용 평단가: {stats[\"pyung_unit\"]}'
new_str = '      • 평균 가격: {stats[\"avg\"]}{suffix} (평단가: {stats[\"pyung_unit\"]})\\n      • 최근 실거래가: {stats.get(\"recent_pyung\", \"-\")}\\n      • 최근 가격흐름: {stats.get(\"trend_desc\", \"-\")}'

content = content.replace(old_str, new_str)

with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)

