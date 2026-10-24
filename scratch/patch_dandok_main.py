import sys
import datetime

path = r'd:\부동산업무\antigravity\consult_diary\trade_viewer.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    injection = '''
    if prop_type_name == "단독/다가구":
        import datetime
        cy = datetime.datetime.now().year
        for lst in [trades, jeonses, wolses]:
            for t in lst:
                try:
                    by_str = t.get("buildYear")
                    if by_str:
                        by = int(str(by_str).strip())
                        if cy - by >= 30:
                            t["excluUseAr"] = float(t.get("plottage") or t.get("excluUseAr") or t.get("totalFloorAr") or 0.0)
                except:
                    pass
'''

    target_str = 'def save_briefing_report_pdf(address, trades, jeonses, wolses, prop_type_name, filename_pdf, apt_groups, period_label, is_expanded, target_build_year, target_area, target_floor, desired_info, expansion_mode):\n'

    if target_str in content:
        content = content.replace(target_str, target_str + injection)
        print("Found save_briefing_report_pdf")
    else:
        print("Not found save_briefing_report_pdf")

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

    print("Patching complete for main trade_viewer.py.")
except Exception as e:
    print("Error:", e)
