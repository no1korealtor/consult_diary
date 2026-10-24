# -*- coding: utf-8 -*-
target_file = "AutoBot_Clean/trade_viewer.py"
with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add villa land chart to PDF in save_briefing_report_pdf
marker_pdf = """        except Exception as e:
            print(f"산포도 생성 중 오류: {e}")
        if prop_type_name not in ["아파트", "오피스텔"]:"""

villa_pdf_code = """        except Exception as e:
            print(f"산포도 생성 중 오류: {e}")
        if prop_type_name in ["연립/다세대/빌라", "다세대", "빌라"]:
            try:
                from market_analyser import create_villa_land_scatter_plot_drawing, build_villa_land_stat_table
                all_villa_trades = [t for t in (trades + jeonses + wolses) if t.get('_trade_type') == '매매']
                land_chart = create_villa_land_scatter_plot_drawing(all_villa_trades, title=f"{address_dong} 빌라 대지지분 평당가 산점도")
                if land_chart:
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("■ 🎯 [개발지/모아타운 핵심 지표] 대지지분 평당가 분석 및 5년 신축/구축 듀얼 곡선", h2_style))
                    story.append(Spacer(1, 4))
                    story.append(land_chart)
                    story.append(Spacer(1, 6))
                    land_table = build_villa_land_stat_table(all_villa_trades, table_cell_center, table_hdr_style)
                    if land_table:
                        story.append(land_table)
                        story.append(Spacer(1, 8))
            except Exception as e:
                print(f"빌라 지분 분석 차트 생성 중 오류: {e}")
        if prop_type_name not in ["아파트", "오피스텔"]:"""

if marker_pdf in code and "create_villa_land_scatter_plot_drawing" not in code:
    code = code.replace(marker_pdf, villa_pdf_code, 1)
    print("Villa land chart added to PDF in AutoBot_Clean/trade_viewer.py.")

# 2. Add bracket table to console in print_comparison_table
marker_console = """            print("═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
        if prop_type == "4":"""

villa_console_code = """            print("═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
        if prop_type == "2":
            try:
                from market_analyser import calculate_villa_land_bracket_stats
                l_stats = calculate_villa_land_bracket_stats(transactions)
                if l_stats and l_stats.get('brackets'):
                    print("\n 🎯 [개발지/모아타운 지분가 분석] 대지지분 구간별 평당가 비교 (최근 24개월)")
                    print("  ※ 5년 기준 구분: 모아타운 노후도 및 권리산정 기준 반영 (신축 프리미엄 vs 구축 적정선)")
                    print(" " + "─" * 78)
                    print(f"  {'대지지분 구간':<15} | {'총건수':<6} | {'구축(>5년) 평당가':<15} | {'신축(≤5년) 평당가':<15} | {'신축 프리미엄':<10}")
                    print(" " + "─" * 78)
                    for b in l_stats['brackets']:
                        tot_c = b['old_cnt'] + b['new_cnt']
                        c_str = f"{tot_c}건"
                        o_str = b['old_str'] if b['old_cnt'] > 0 else "-"
                        n_str = b['new_str'] if b['new_cnt'] > 0 else "-"
                        diff_s = b['gap_str'] if b['gap_str'] != "-" else "-"
                        print(f"  {b['label']:<15} | {c_str:<6} | {o_str:<15} | {n_str:<15} | {diff_s:<10}")
                    print(" " + "─" * 78)
            except Exception as e:
                pass
        if prop_type == "4":"""

if marker_console in code and "calculate_villa_land_bracket_stats" not in code:
    code = code.replace(marker_console, villa_console_code, 1)
    print("Console bracket table added to AutoBot_Clean/trade_viewer.py.")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied to AutoBot_Clean/trade_viewer.py successfully.")
