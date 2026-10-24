import os
import re

file_path = "d:\\부동산업무\\antigravity\\consult_diary\\trade_viewer.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """        def build_summary_table(section_title, items, is_rent=False, is_wolse=False):
            sect_heading = Paragraph(section_title, h2_style)
            headers = [Paragraph("<b>면적 구분</b>", table_hdr_style), Paragraph("<b>거래 건수</b>", table_hdr_style), Paragraph("<b>실거래가 범위</b>", table_hdr_style), Paragraph("<b>최근 실거래(평단가)</b>", table_hdr_style), Paragraph("<b>가격 흐름(기울기)</b>", table_hdr_style)]
            table_content = [headers]
            has_rows = False
            
            target_label = get_size_category_label(target_area, prop_type_name, apt_groups) if target_area else ""
            
            target_apt_groups = set()
            if prop_type_name == "아파트" and apt_groups:
                all_txs_for_title = trades + jeonses + wolses
                for item in all_txs_for_title:
                    is_target = False
                    if target_bun:
                        t_jibun = normalize_jibun(item.get("jibun", ""))
                        t_target_jibun = str(int(target_bun))
                        if target_ji and int(target_ji) > 0:
                            t_target_jibun += f"-{int(target_ji)}"
                        if t_jibun == t_target_jibun:
                            is_target = True
                    elif target_bld_nm:
                        apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                        if apt_nm == target_bld_nm:
                            is_target = True
                            
                    if is_target:
                        g_for_item = get_group_for_item(item, apt_groups)
                        if g_for_item:
                            target_apt_groups.add(g_for_item["label"])

            if prop_type_name == "아파트" and apt_groups:
                for g in apt_groups:
                    g_subset = [t for t in items if get_group_for_item(t, apt_groups) == g]
                    stats = calculate_subset_stats(g_subset, is_rent, is_wolse)
                    if not stats:
                        continue
                    suffix = ""
                    label_str = g["label"]
                    if label_str == target_label or label_str in target_apt_groups:
                        label_str += "<br/><font color='#D69E2E'><b>[목적 평형]</b></font>"
                        
                    table_content.append([Paragraph(label_str, table_cell_style), Paragraph(f"{stats['count']}건", table_cell_style_center), Paragraph(stats["range"] + suffix, table_cell_style_right),
Paragraph(stats.get("recent_pyung", "-"), table_cell_style_right), Paragraph(stats.get("trend_desc", "-"), table_cell_style_right)])
                    has_rows = True
            else:
                under_26 = []; between_26_43 = []; above_43 = []
                for item in items:
                    area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                    try: area = float(area_val)
                    except: area = 0.0
                    if area < 26.0: under_26.append(item)
                    elif area < 43.0: between_26_43.append(item)
                    else: above_43.append(item)
                
                size_categories = [("원룸/1.5룸형 (전용 26㎡ 미만)", under_26), ("투룸형 (전용 26㎡ ~ 43㎡ 미만)", between_26_43),
                                   ("쓰리룸 이상형 (전용 43㎡ 이상)", above_43)]
                for label, subset in size_categories:
                    stats = calculate_subset_stats(subset, is_rent, is_wolse)
                    if not stats:
                        continue
                    suffix = ""
                    label_str = label
                    if label_str == target_label:
                        label_str += "<br/><font color='#D69E2E'><b>[목적 평형]</b></font>"
                        
                    table_content.append([Paragraph(label_str, table_cell_style),
                                          Paragraph(f"{stats['count']}건", table_cell_style_center),
                                          Paragraph(stats["range"] + suffix, table_cell_style_right),
                                          Paragraph(stats.get("recent_pyung", "-"), table_cell_style_right),
                                          Paragraph(stats.get("trend_desc", "-"), table_cell_style_right)])
                    has_rows = True
            
            if not has_rows:
                table_content.append([Paragraph(f"{period_label}간 신고된 거래 사례가 없습니다.", table_cell_style_center), "", "", "", ""])
            
            t = Table(table_content, colWidths=[150, 50, 120, 90, 90])
            t_style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                       ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                       ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                       ("TOPPADDING", (0, 0), (-1, -1), 5),
                       ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0"))]
            if has_rows:
                for idx in range(1, len(table_content)):
                    bg_color = colors.HexColor("#FFFFFF") if idx % 2 == 1 else colors.HexColor("#F7FAFC")
                    t_style.append(("BACKGROUND", (0, idx), (-1, idx), bg_color))
            else:
                t_style.append(("SPAN", (0, 1), (-1, 1)))
                t_style.append(("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")))
            t.setStyle(TableStyle(t_style))
            return (sect_heading, t)
        h, t = build_summary_table("■ [매매] 시세 요약", trades, is_rent=False)
        story.append(h)
        story.append(Spacer(1, 4))
        story.append(t)
        h, t = build_summary_table("■ [전세] 시세 요약", jeonses, is_rent=True)
        story.append(h)
        story.append(Spacer(1, 4))
        story.append(t)
        h, t = build_summary_table("■ [월세] 시세 요약 (보증금 + 월세 * 100 환산 기준)", wolses, is_rent=True, is_wolse=True)
        story.append(h)
        story.append(Spacer(1, 4))
        story.append(t)"""

new_block = """        def build_summary_table(section_title, items, is_rent=False, is_wolse=False):
            sect_heading = Paragraph(section_title, h2_style)
            
            target_items = []
            comp_items = []
            if is_expanded and prop_type_name == "아파트":
                for item in items:
                    is_target = False
                    if target_bun:
                        t_jibun = normalize_jibun(item.get("jibun", ""))
                        t_target_jibun = str(int(target_bun))
                        if target_ji and int(target_ji) > 0:
                            t_target_jibun += f"-{int(target_ji)}"
                        if t_jibun == t_target_jibun:
                            is_target = True
                    elif target_bld_nm:
                        apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                        if apt_nm == target_bld_nm:
                            is_target = True
                    if is_target:
                        target_items.append(item)
                    else:
                        comp_items.append(item)
            else:
                target_items = items
                
            def make_table(sub_items):
                headers = [Paragraph("<b>면적 구분</b>", table_hdr_style), Paragraph("<b>거래 건수</b>", table_hdr_style), Paragraph("<b>실거래가 범위</b>", table_hdr_style), Paragraph("<b>최근 실거래(평단가)</b>", table_hdr_style), Paragraph("<b>가격 흐름(기울기)</b>", table_hdr_style)]
                table_content = [headers]
                has_rows = False
                
                target_label = get_size_category_label(target_area, prop_type_name, apt_groups) if target_area else ""
                
                target_apt_groups = set()
                if prop_type_name == "아파트" and apt_groups:
                    for item in sub_items:
                        is_target = False
                        if target_bun:
                            t_jibun = normalize_jibun(item.get("jibun", ""))
                            t_target_jibun = str(int(target_bun))
                            if target_ji and int(target_ji) > 0:
                                t_target_jibun += f"-{int(target_ji)}"
                            if t_jibun == t_target_jibun:
                                is_target = True
                        elif target_bld_nm:
                            apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                            if apt_nm == target_bld_nm:
                                is_target = True
                                
                        if is_target:
                            g_for_item = get_group_for_item(item, apt_groups)
                            if g_for_item:
                                target_apt_groups.add(g_for_item["label"])

                if prop_type_name == "아파트" and apt_groups:
                    for g in apt_groups:
                        g_subset = [t for t in sub_items if get_group_for_item(t, apt_groups) == g]
                        stats = calculate_subset_stats(g_subset, is_rent, is_wolse)
                        if not stats:
                            continue
                        suffix = ""
                        label_str = g["label"]
                        if label_str == target_label or label_str in target_apt_groups:
                            label_str += "<br/><font color='#D69E2E'><b>[목적 평형]</b></font>"
                            
                        table_content.append([Paragraph(label_str, table_cell_style), Paragraph(f"{stats['count']}건", table_cell_style_center), Paragraph(stats["range"] + suffix, table_cell_style_right),
    Paragraph(stats.get("recent_pyung", "-"), table_cell_style_right), Paragraph(stats.get("trend_desc", "-"), table_cell_style_right)])
                        has_rows = True
                else:
                    under_26 = []; between_26_43 = []; above_43 = []
                    for item in sub_items:
                        area_val = item.get("excluUseAr") or item.get("totalFloorAr") or 0.0
                        try: area = float(area_val)
                        except: area = 0.0
                        if area < 26.0: under_26.append(item)
                        elif area < 43.0: between_26_43.append(item)
                        else: above_43.append(item)
                    
                    size_categories = [("원룸/1.5룸형 (전용 26㎡ 미만)", under_26), ("투룸형 (전용 26㎡ ~ 43㎡ 미만)", between_26_43),
                                       ("쓰리룸 이상형 (전용 43㎡ 이상)", above_43)]
                    for label, subset in size_categories:
                        stats = calculate_subset_stats(subset, is_rent, is_wolse)
                        if not stats:
                            continue
                        suffix = ""
                        label_str = label
                        if label_str == target_label:
                            label_str += "<br/><font color='#D69E2E'><b>[목적 평형]</b></font>"
                            
                        table_content.append([Paragraph(label_str, table_cell_style),
                                              Paragraph(f"{stats['count']}건", table_cell_style_center),
                                              Paragraph(stats["range"] + suffix, table_cell_style_right),
                                              Paragraph(stats.get("recent_pyung", "-"), table_cell_style_right),
                                              Paragraph(stats.get("trend_desc", "-"), table_cell_style_right)])
                        has_rows = True
                
                if not has_rows:
                    table_content.append([Paragraph(f"{period_label}간 신고된 거래 사례가 없습니다.", table_cell_style_center), "", "", "", ""])
                
                t = Table(table_content, colWidths=[150, 50, 120, 90, 90])
                t_style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                           ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                           ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0"))]
                if has_rows:
                    for idx in range(1, len(table_content)):
                        bg_color = colors.HexColor("#FFFFFF") if idx % 2 == 1 else colors.HexColor("#F7FAFC")
                        t_style.append(("BACKGROUND", (0, idx), (-1, idx), bg_color))
                else:
                    t_style.append(("SPAN", (0, 1), (-1, 1)))
                    t_style.append(("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")))
                t.setStyle(TableStyle(t_style))
                return t
                
            elements = [sect_heading, Spacer(1, 4)]
            if is_expanded and prop_type_name == "아파트" and comp_items:
                elements.append(Paragraph(f"<b>[대상 아파트] {target_bld_nm or '분석 대상'} 거래 사례</b>", ParagraphStyle("SubH", parent=styles["Normal"], fontName="KoreanFont", fontSize=10, textColor=colors.HexColor("#2C5282"), spaceAfter=4)))
                elements.append(make_table(target_items))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("<b>[비교 아파트] 인근 유사 매물 사례</b>", ParagraphStyle("SubH", parent=styles["Normal"], fontName="KoreanFont", fontSize=10, textColor=colors.HexColor("#2C5282"), spaceAfter=4)))
                elements.append(make_table(comp_items))
            else:
                elements.append(make_table(items))
            return elements

        story.extend(build_summary_table("■ [매매] 시세 요약", trades, is_rent=False))
        story.append(Spacer(1, 4))
        story.extend(build_summary_table("■ [전세] 시세 요약", jeonses, is_rent=True))
        story.append(Spacer(1, 4))
        story.extend(build_summary_table("■ [월세] 시세 요약 (보증금 + 월세 * 100 환산 기준)", wolses, is_rent=True, is_wolse=True))
        story.append(Spacer(1, 4))"""

if old_block in content:
    new_content = content.replace(old_block, new_block)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("PDF report updated successfully!")
else:
    print("Could not find the block to replace!")
