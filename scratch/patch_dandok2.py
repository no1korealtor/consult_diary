import sys

path = r'd:\부동산업무\antigravity\consult_diary\scratch\trade_viewer.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

insight_injection = '''
    if prop_type_name == "단독/다가구":
        insights.append("• [분석 기준] 본 분석은 30년 이상 노후 주택으로 건물 가치를 배제하고, 실질적인 토지(대지면적) 거래가치를 기준으로 산출되었습니다.")
'''
insight_target = 'def generate_comparison_insights(trades, jeonses, wolses, prop_type_name=""):\n    insights = []\n'
if insight_target in content:
    content = content.replace(insight_target, insight_target + insight_injection)
    print("Found generate_comparison_insights")
else:
    print("Not found generate_comparison_insights")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patching complete.")
