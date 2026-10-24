import re

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix classify_property_type
content = content.replace(
'''def classify_property_type(main_purp, bld_name, etc_purp):
    main_purp = main_purp or ""; bld_name = bld_name or ""; etc_purp = etc_purp or ""; combined = main_purp + " " + bld_name + " " + etc_purp.lower()
    if "아파트" in combined:
        return "1"
    elif "오피스텔" in combined:
        return "3"
    elif "단독" in combined or "다가구" in combined:
        return "4"
    elif "다세대" in combined and "연립" in combined and "빌라" in combined and "도시형" in combined or "공동주택" in combined:
        return "2"''',
'''def classify_property_type(main_purp, bld_name, etc_purp, hhld_cnt=0):
    main_purp = main_purp or ""; bld_name = bld_name or ""; etc_purp = etc_purp or ""; combined = main_purp + " " + bld_name + " " + etc_purp.lower()
    if "아파트" in combined or hhld_cnt >= 30:
        return "1"
    elif "오피스텔" in combined:
        return "3"
    elif "단독" in combined or "다가구" in combined:
        return "4"
    elif "다세대" in combined or "연립" in combined or "빌라" in combined or "도시형" in combined or "공동주택" in combined:
        return "2"'''
)

content = content.replace(
'''                    main_purp = selected_title.get("mainPurpsCdNm", "")
                    bld_name = selected_title.get("bldNm", "")
                    etc_purp = selected_title.get("etcPurps", "")
                    apr = str(selected_title.get("useAprDay", "")).strip()
                    if apr and len(apr) >= 4:
                        target_build_year = int(apr[:4])
            prop_type = classify_property_type(main_purp, bld_name, etc_purp)''',
'''                    main_purp = selected_title.get("mainPurpsCdNm", "")
                    bld_name = selected_title.get("bldNm", "")
                    etc_purp = selected_title.get("etcPurps", "")
                    hhld_cnt = int(selected_title.get("hhldCnt", 0) or 0)
                    apr = str(selected_title.get("useAprDay", "")).strip()
                    if apr and len(apr) >= 4:
                        target_build_year = int(apr[:4])
            prop_type = classify_property_type(main_purp, bld_name, etc_purp, hhld_cnt)'''
)

# 2. Fix parse_address_and_ho
content = content.replace(
'''    jibun_idx = -1
    for idx, w in enumerate(words):
        clean_w = w.strip(",.")
        if re.match(r"^산?\d+(-\d+)?$", clean_w):
            jibun_idx = idx
    if jibun_idx == -1:''',
'''    jibun_idx = -1
    for idx, w in enumerate(words):
        clean_w = w.strip(",.")
        if re.match(r"^산?\d+(-\d+)?$", clean_w):
            jibun_idx = idx
            break
    if jibun_idx == -1:'''
)

# 3. Fix trades, jeonses, wolses decompiled mess
content = content.replace(
'''                    [t for t in transactions if not t.get("_trade_type") == "매매"]
                    trades = address_name
                    t = None
                    [t for t in transactions if not t.get("_trade_type") == "전세"]
                    jeonses = None
                    t = None
                    [t for t in transactions if not t.get("_trade_type") == "월세"]
                    wolses = None
                    t = None''',
'''                    trades = [t for t in transactions if t.get("_trade_type") == "매매"]
                    jeonses = [t for t in transactions if t.get("_trade_type") == "전세"]
                    wolses = [t for t in transactions if t.get("_trade_type") == "월세"]'''
)

# 4. Fix area_val
content = re.sub(
    r'(\s+)if not item\.get\(\"excluUseAr\"\):\s+item\.get\(\"excluUseAr\"\)\s+area_val = item\.get\(\"totalFloorAr\"\)\s+area = None\s+if area_val is None:\s+area = float\(area_val\)\s+pyung = round\(area \* 0\.3025, 1\)\s+area_display = f\"\{area:\.2f\}㎡ \(\{pyung\}평\)\"\s+else:\s+area_display = \"-\"',
    r'''\1area_val = item.get("excluUseAr") or item.get("totalFloorAr")
\1area = None
\1if area_val is not None:
\1    try:
\1        area = float(area_val)
\1        pyung = round(area * 0.3025, 1)
\1        area_display = f"{area:.2f}㎡ ({pyung}평)"
\1    except:
\1        area_display = "-"
\1else:
\1    area_display = "-"''',
    content
)

# 5. Fix land_val
content = re.sub(
    r'(\s+)if land_val is None:\s+land_area = float\(land_val\)\s+if land_area > 0:\s+land_pyung = round\(land_area \* 0\.3025, 1\)\s+land_display = f\"\{land_area:\.2f\}㎡ \(\{land_pyung\}평\)\"',
    r'''\1if land_val is not None:
\1    try:
\1        land_area = float(land_val)
\1        if land_area > 0:
\1            land_pyung = round(land_area * 0.3025, 1)
\1            land_display = f"{land_area:.2f}㎡ ({land_pyung}평)"
\1    except:
\1        pass''',
    content
)

# 6. Fix floor
content = re.sub(
    r'(\s+)floor = int\(floor_str\)\s+floor_display = f\"\{dong_prefix\}\{floor\}층\"',
    r'''\1floor = None
\1try:
\1    floor = int(floor_str)
\1    floor_display = f"{dong_prefix}{floor}층"
\1except:
\1    floor_display = f"{dong_prefix}{floor_str}층" if floor_str else dong_prefix.strip()''',
    content
)

# 7. Fix base_floor condition
content = content.replace("if base_floor is None and floor is None:", "if base_floor is not None and floor is not None:")
content = content.replace("base_floor = floor", "base_floor = floor\n                                else:\n                                    base_floor = None")
content = content.replace("base_floor = target_floor", "")
# Wait, actually let's initialize base_floor = target_floor cleanly.
content = re.sub(r'(\s+)diff_parts = \[\]', r'\1diff_parts = []\n\1base_floor = target_floor', content)

with open('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(content)
