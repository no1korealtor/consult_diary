# -*- coding: utf-8 -*-
import os

target_file = "AutoBot_Clean/market_analyser.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Imports
code = code.replace(
    "import json\nfrom datetime import datetime\n\n# ReportLab imports for PDF generation\nfrom reportlab.lib.pagesizes import A4\nfrom reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle",
    "import json\nimport math\nfrom datetime import datetime\n\n# ReportLab imports for PDF generation\nfrom reportlab.lib.pagesizes import A4\nfrom reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether"
)

# 2. Extract functions from consult_diary/market_analyser.py
with open("consult_diary/market_analyser.py", "r", encoding="utf-8") as f:
    diary_code = f.read()

start_fn = "def fit_log_curve_points(pts):"
end_fn = "def create_jeonse_ratio_trend_drawing(transactions"

fn_block = diary_code[diary_code.find(start_fn):diary_code.find(end_fn)].strip()

# Insert before def generate_market_report_pdf
target_marker = "def generate_market_report_pdf(pdf_filename, bjdong_nm, villa_txs, member_info=None, region_prefix=\"서울특별시 마포구\"):"
if target_marker in code and "def fit_log_curve_points" not in code:
    code = code.replace(target_marker, fn_block + "\n\n" + target_marker)
    print("Helper functions inserted.")
else:
    print("Marker not found or already inserted.")

# 3. Update build_prop_section signature
old_sig = "    def build_prop_section(label, txs, prop_type):"
new_sig = "    def build_prop_section(label, txs, prop_type, full_txs=None):"
if old_sig in code:
    code = code.replace(old_sig, new_sig)
    print("build_prop_section signature updated.")

# 4. Insert villa land chart block inside build_prop_section
basement_marker = 'sect_story.append(Paragraph("※ 지하층(반지하)은 전세보증금 규모가 작아 전월세 전환율이 지상층 대비 높게 산출되는 특징이 있으나, 환금성 및 채광/습기 등 특수성을 고려해야 합니다.", b_expl_style))'

villa_chart_code = """sect_story.append(Paragraph("※ 지하층(반지하)은 전세보증금 규모가 작아 전월세 전환율이 지상층 대비 높게 산출되는 특징이 있으나, 환금성 및 채광/습기 등 특수성을 고려해야 합니다.", b_expl_style))

            # --- 모아타운·개발지 대지지분 평당가 분석 차트 및 5년 신축/구축 듀얼 곡선 ---
            target_land_txs = full_txs if full_txs else txs
            land_chart = create_villa_land_scatter_plot_drawing(target_land_txs, title="개발지/모아타운 대지지분 평당가 산점도")
            if land_chart:
                land_block = [
                    Spacer(1, 12),
                    Paragraph("■ 🎯 [개발지/모아타운 핵심 지표] 대지지분 평당가 분석 및 5년 신축/구축 듀얼 곡선", h2_style),
                    Spacer(1, 4),
                    land_chart,
                    Spacer(1, 6)
                ]
                land_table = build_villa_land_stat_table(target_land_txs, table_cell_center, table_hdr_style)
                if land_table:
                    land_block.append(land_table)
                    land_block.append(Spacer(1, 6))
                sect_story.append(KeepTogether(land_block))"""

if basement_marker in code and "land_chart = create_villa_land_scatter_plot_drawing" not in code:
    code = code.replace(basement_marker, villa_chart_code, 1)
    print("Villa land chart block inserted into build_prop_section.")

# 5. Pass full_txs=villa_txs to build_prop_section
old_call = 'story.extend(build_prop_section("🏡 연립/다세대/빌라 (지상층·최근 6개월 기준)", filtered_villa_txs, \'2\'))'
new_call = 'story.extend(build_prop_section("🏡 연립/다세대/빌라 (지상층·최근 6개월 기준)", filtered_villa_txs, \'2\', full_txs=villa_txs))'
if old_call in code:
    code = code.replace(old_call, new_call)
    print("build_prop_section call updated with full_txs.")

# 6. Add console & txt bracket breakdown in run_market_analysis
cma_comment = '    # CMA 추천 매물 (Best Value Pick)'
bracket_console_code = """    # 대지지분 평단가 5년 신축/구축 듀얼 분석 (모아타운/개발지 핵심 지표)
    land_stats = calculate_villa_land_bracket_stats(villa_txs)
    if land_stats and land_stats.get('brackets'):
        add_line("\\n[🎯 개발지/모아타운 핵심 지표: 대지지분 구간별 평당가 분석 (최근 24개월 전수)]")
        add_line("  ※ 모아타운·재개발 투자 5년 보유 규정 및 노후도 기준 반영 (5년 이하 신축 vs 5년 초과 구축 비교)")
        add_line(f" {'구간':<15} | {'총건수':<6} | {'구축(>5년) 평당가':<14} | {'신축(≤5년) 평당가':<14} | {'신축 프리미엄':<10}")
        add_line(" " + "-" * 68)
        for b in land_stats['brackets']:
            tot_cnt = b['old_cnt'] + b['new_cnt']
            cnt_str = f"{tot_cnt}건"
            old_str = b['old_str'] if b['old_cnt'] > 0 else "-"
            new_str = b['new_str'] if b['new_cnt'] > 0 else "-"
            diff_str = b['gap_str'] if b['gap_str'] != "-" else "-"
            add_line(f"  {b['label']:<13} | {cnt_str:<6} | {old_str:<14} | {new_str:<14} | {diff_str:<10}")
        add_line(" " + "-" * 68)

    # CMA 추천 매물 (Best Value Pick)"""

if cma_comment in code and "land_stats = calculate_villa_land_bracket_stats" not in code:
    code = code.replace(cma_comment, bracket_console_code)
    print("Console & TXT breakdown added.")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied to AutoBot_Clean/market_analyser.py successfully.")
