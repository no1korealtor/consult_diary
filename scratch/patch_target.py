import os

file_path = "d:\\부동산업무\\antigravity\\consult_diary\\trade_viewer.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """            target_items = []
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
                                target_apt_groups.add(g_for_item["label"])"""

new_block = """            target_items = []
            comp_items = []
            if prop_type_name == "아파트":
                for item in items:
                    is_target = False
                    apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                    if target_bld_nm and apt_nm:
                        if apt_nm == target_bld_nm:
                            is_target = True
                    else:
                        if target_bun:
                            t_jibun = normalize_jibun(item.get("jibun", ""))
                            t_target_jibun = str(int(target_bun))
                            if target_ji and int(target_ji) > 0:
                                t_target_jibun += f"-{int(target_ji)}"
                            if t_jibun == t_target_jibun:
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
                        apt_nm = (item.get("aptNm") or item.get("mhouseNm") or "").strip()
                        if target_bld_nm and apt_nm:
                            if apt_nm == target_bld_nm:
                                is_target = True
                        else:
                            if target_bun:
                                t_jibun = normalize_jibun(item.get("jibun", ""))
                                t_target_jibun = str(int(target_bun))
                                if target_ji and int(target_ji) > 0:
                                    t_target_jibun += f"-{int(target_ji)}"
                                if t_jibun == t_target_jibun:
                                    is_target = True
                                
                        if is_target:
                            g_for_item = get_group_for_item(item, apt_groups)
                            if g_for_item:
                                target_apt_groups.add(g_for_item["label"])"""

old_block2 = """            elements = [sect_heading, Spacer(1, 4)]
            if is_expanded and prop_type_name == "아파트" and comp_items:
                elements.append(Paragraph(f"<b>[대상 아파트] {target_bld_nm or '분석 대상'} 거래 사례</b>", ParagraphStyle("SubH", parent=styles["Normal"], fontName="KoreanFont", fontSize=10, textColor=colors.HexColor("#2C5282"), spaceAfter=4)))
                elements.append(make_table(target_items))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("<b>[비교 아파트] 인근 유사 매물 사례</b>", ParagraphStyle("SubH", parent=styles["Normal"], fontName="KoreanFont", fontSize=10, textColor=colors.HexColor("#2C5282"), spaceAfter=4)))
                elements.append(make_table(comp_items))
            else:
                elements.append(make_table(items))
            return elements"""

new_block2 = """            elements = [sect_heading, Spacer(1, 4)]
            if prop_type_name == "아파트" and comp_items:
                elements.append(Paragraph(f"<b>[대상 아파트] {target_bld_nm or '분석 대상'} 거래 사례</b>", ParagraphStyle("SubH", parent=styles["Normal"], fontName="KoreanFont", fontSize=10, textColor=colors.HexColor("#2C5282"), spaceAfter=4)))
                elements.append(make_table(target_items))
                elements.append(Spacer(1, 8))
                elements.append(Paragraph("<b>[비교 아파트] 인근 유사 매물 사례</b>", ParagraphStyle("SubH", parent=styles["Normal"], fontName="KoreanFont", fontSize=10, textColor=colors.HexColor("#2C5282"), spaceAfter=4)))
                elements.append(make_table(comp_items))
            else:
                elements.append(make_table(items))
            return elements"""

if old_block in content and old_block2 in content:
    content = content.replace(old_block, new_block)
    content = content.replace(old_block2, new_block2)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("PDF logic patched successfully!")
else:
    print("Could not find blocks to replace!")
