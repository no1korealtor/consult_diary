import re

with open('d:/부동산업무/antigravity/consult_diary/building_viewer.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Chunk 1
code = code.replace(
    "clean_address, dong_name, ho_name = parse_address_and_ho(address)\n        bld_nm = \"\"",
    "clean_address, dong_name, ho_name = parse_address_and_ho(address)\n        is_complex_analysis = False\n        bld_nm = \"\""
)

# Chunk 2
old_chunk2 = """        else:
            if len(titles) > 1:
                print("\\n [!] 해당 지번에 여러 개의 건물이 확인되었습니다.")
                
                # Filter for residential buildings
                residential_items = []
                other_items = []
                for t in titles:
                    b_nm = str(t.get("bldNm", ""))
                    d_nm = str(t.get("dongNm", ""))
                    purp = str(t.get("mainPurpsCdNm", ""))
                    try: h = int(t.get("hhldCnt", 0) or 0)
                    except: h = 0
                    
                    is_residential = h > 0 or "아파트" in b_nm or "아파트" in d_nm or "주택" in purp or "오피스텔" in purp
                    if h == 0 and ("근린" in purp or "상가" in b_nm or "상가" in d_nm or "주차" in purp or "영업" in purp):
                        is_residential = False
                        
                    if is_residential:
                        residential_items.append(t)
                    else:
                        other_items.append(t)
                        
                # If there are residential buildings, prefer them
                display_items = residential_items if residential_items else other_items
                if residential_items and other_items:
                    print("     (주거용 건물만 필터링하여 보여줍니다.)")
                    
                for idx, t in enumerate(display_items):
                    b_nm = str(t.get("bldNm", "")).strip() or "건물명 없음"
                    d_nm = str(t.get("dongNm", "")).strip() or "동 없음"
                    purp = str(t.get("mainPurpsCdNm", "")).strip() or "용도 불명"
                    h = t.get("hhldCnt", 0)
                    print(f"  {idx+1}: {b_nm} ({d_nm}) - {purp} (세대수: {h})")
                
                while True:
                    sel = input(f"\\n[입력] 분석할 주거용 건물 번호를 선택해 주세요 (1~{len(display_items)}, 자동선택 시 엔터): ").strip()
                    if not sel:
                        best_t = display_items[0]
                        max_h = 0
                        for t in display_items:
                            try: h = int(t.get("hhldCnt", 0) or 0)
                            except: h = 0
                            if h > max_h:
                                max_h = h
                                best_t = t
                        selected_title = best_t
                        break
                    if sel.isdigit() and 1 <= int(sel) <= len(display_items):
                        selected_title = display_items[int(sel)-1]
                        break
                    print(" [!] 올바른 번호를 입력해 주세요.")
            else:
                selected_title = titles[0]"""

new_chunk2 = """        else:
            if len(titles) > 1:
                print("\\n [!] 해당 지번에 여러 개의 건물이 확인되었습니다.")
                print(" [안내] 어떤 형태의 분석을 진행하시겠습니까?")
                print("  1: [개별 세대 CMA] 특정 동/호수를 지정하여 해당 호실의 적정가격을 산출합니다.")
                print("  2: [단지 종합 분석] 특정 동/호수 지정 없이, 단지 전체의 시세 흐름을 분석합니다.")
                purpose_sel = input("\\n[입력] 원하시는 분석 번호를 선택해 주세요 (1 또는 2, 기본값 1): ").strip()
                
                if purpose_sel == '2':
                    is_complex_analysis = True
                    best_t = titles[0]
                    max_h = 0
                    for t in titles:
                        try: h = int(t.get("hhldCnt", 0) or 0)
                        except: h = 0
                        if h > max_h:
                            max_h = h
                            best_t = t
                    selected_title = best_t
                else:
                    # Filter for residential buildings
                    residential_items = []
                    other_items = []
                    for t in titles:
                        b_nm = str(t.get("bldNm", ""))
                        d_nm = str(t.get("dongNm", ""))
                        purp = str(t.get("mainPurpsCdNm", ""))
                        try: h = int(t.get("hhldCnt", 0) or 0)
                        except: h = 0
                        
                        is_residential = h > 0 or "아파트" in b_nm or "아파트" in d_nm or "주택" in purp or "오피스텔" in purp
                        if h == 0 and ("근린" in purp or "상가" in b_nm or "상가" in d_nm or "주차" in purp or "영업" in purp):
                            is_residential = False
                            
                        if is_residential:
                            residential_items.append(t)
                        else:
                            other_items.append(t)
                            
                    # If there are residential buildings, prefer them
                    display_items = residential_items if residential_items else other_items
                    if residential_items and other_items:
                        print("     (주거용 건물만 필터링하여 보여줍니다.)")
                        
                    for idx, t in enumerate(display_items):
                        b_nm = str(t.get("bldNm", "")).strip() or "건물명 없음"
                        d_nm = str(t.get("dongNm", "")).strip() or "동 없음"
                        purp = str(t.get("mainPurpsCdNm", "")).strip() or "용도 불명"
                        h = t.get("hhldCnt", 0)
                        print(f"  {idx+1}: {b_nm} ({d_nm}) - {purp} (세대수: {h})")
                    
                    while True:
                        sel = input(f"\\n[입력] 분석할 주거용 건물 번호를 선택해 주세요 (1~{len(display_items)}, 자동선택 시 엔터): ").strip()
                        if not sel:
                            best_t = display_items[0]
                            max_h = 0
                            for t in display_items:
                                try: h = int(t.get("hhldCnt", 0) or 0)
                                except: h = 0
                                if h > max_h:
                                    max_h = h
                                    best_t = t
                            selected_title = best_t
                            break
                        if sel.isdigit() and 1 <= int(sel) <= len(display_items):
                            selected_title = display_items[int(sel)-1]
                            break
                        print(" [!] 올바른 번호를 입력해 주세요.")
            else:
                selected_title = titles[0]"""

code = code.replace(old_chunk2, new_chunk2)

# Chunk 3
code = code.replace(
    "elif is_jibbap and not ho_name:\n            print(\"\\n [안내] 해당 건물은 집합건축물(호별대장 있음)이지만 호실이 지정되지 않았습니다.\")",
    "elif is_jibbap and not ho_name and not is_complex_analysis:\n            print(\"\\n [안내] 해당 건물은 집합건축물(호별대장 있음)이지만 호실이 지정되지 않았습니다.\")"
)

# Chunk 4
old_chunk4 = """        print("\\n[희망 거래/보고서 형태 선택]")
        print("  1: 매매 (CMA 시세 분석)")
        print("  2: 전세 (CMA 시세 분석)")
        print("  3: 월세 (CMA 시세 분석)")
        print("  4: 종합 (전체 거래 동향 보고서 - 가격 비교 생략)")
        t_choice = input("[입력] 번호를 선택하세요 (1/2/3/4): ").strip()
        while t_choice not in ("1", "2", "3", "4"):
            print(" [!] 올바른 번호(1, 2, 3, 4)를 입력해 주세요.")
            t_choice = input("[입력] 번호를 선택하세요 (1/2/3/4): ").strip()"""

new_chunk4 = """        if is_complex_analysis:
            t_choice = "4"
            print("\\n -> [단지 종합 분석] 단지 전체 시세 흐름 조회를 시작합니다.")
        else:
            print("\\n[희망 거래/보고서 형태 선택]")
            print("  1: 매매 (CMA 시세 분석)")
            print("  2: 전세 (CMA 시세 분석)")
            print("  3: 월세 (CMA 시세 분석)")
            print("  4: 종합 (전체 거래 동향 보고서 - 가격 비교 생략)")
            t_choice = input("[입력] 번호를 선택하세요 (1/2/3/4): ").strip()
            while t_choice not in ("1", "2", "3", "4"):
                print(" [!] 올바른 번호(1, 2, 3, 4)를 입력해 주세요.")
                t_choice = input("[입력] 번호를 선택하세요 (1/2/3/4): ").strip()"""

code = code.replace(old_chunk4, new_chunk4)

with open('d:/부동산업무/antigravity/consult_diary/building_viewer.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("Patch applied to building_viewer.py")
