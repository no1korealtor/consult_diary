import sys

# Patch building_viewer.py
with open('building_viewer.py', 'r', encoding='utf-8') as f:
    bv_content = f.read()

old_bv_block = """        else:
            best_t = titles[0]
            max_h = 0
            for t in titles:
                try:
                    h = int(t.get("hhldCnt", 0) or 0)
                except:
                    h = 0
                if h > max_h:
                    max_h = h
                    best_t = t
            if max_h == 0:
                for t in titles:
                    b_nm = str(t.get("bldNm", ""))
                    d_nm = str(t.get("dongNm", ""))
                    if "아파트" in b_nm or "아파트" in d_nm:
                        best_t = t
                        break
            selected_title = best_t"""

new_bv_block = """        else:
            if len(titles) > 1:
                print("\\n [!] 해당 지번에 여러 개의 건물이 확인되었습니다.")
                for idx, t in enumerate(titles):
                    b_nm = str(t.get("bldNm", "")).strip() or "건물명 없음"
                    d_nm = str(t.get("dongNm", "")).strip() or "동 없음"
                    purp = str(t.get("mainPurpsCdNm", "")).strip() or "용도 불명"
                    h = t.get("hhldCnt", 0)
                    print(f"  {idx+1}: {b_nm} ({d_nm}) - {purp} (세대수: {h})")
                
                while True:
                    sel = input(f"\\n[입력] 분석할 건물 번호를 선택해 주세요 (1~{len(titles)}, 기본값: 1): ").strip()
                    if not sel:
                        selected_title = titles[0]
                        break
                    if sel.isdigit() and 1 <= int(sel) <= len(titles):
                        selected_title = titles[int(sel)-1]
                        break
                    print(" [!] 올바른 번호를 입력해 주세요.")
            else:
                selected_title = titles[0]"""

bv_content = bv_content.replace(old_bv_block, new_bv_block)
with open('building_viewer.py', 'w', encoding='utf-8') as f:
    f.write(bv_content)

# Patch trade_viewer.py
with open('trade_viewer.py', 'r', encoding='utf-8') as f:
    tv_content = f.read()

old_tv_block = """                    else:
                        best_t = items[0]
                        max_h = 0
                        for t in items:
                            try:
                                h = int(t.get("hhldCnt", 0) or 0)
                            except:
                                h = 0
                            if h > max_h:
                                max_h = h
                                best_t = t
                        if max_h == 0:
                            for t in items:
                                b_nm = str(t.get("bldNm", ""))
                                d_nm = str(t.get("dongNm", ""))
                                if "아파트" in b_nm or "아파트" in d_nm:
                                    best_t = t
                                    break
                        selected_title = best_t"""

new_tv_block = """                    else:
                        if len(items) > 1 and len(sys.argv) <= 1:
                            print("\\n [!] 해당 지번에 여러 개의 건물이 확인되었습니다.")
                            for idx, t in enumerate(items):
                                b_nm = str(t.get("bldNm", "")).strip() or "건물명 없음"
                                d_nm = str(t.get("dongNm", "")).strip() or "동 없음"
                                purp = str(t.get("mainPurpsCdNm", "")).strip() or "용도 불명"
                                h = t.get("hhldCnt", 0)
                                print(f"  {idx+1}: {b_nm} ({d_nm}) - {purp} (세대수: {h})")
                            
                            while True:
                                sel = input(f"\\n[입력] 분석할 건물 번호를 선택해 주세요 (1~{len(items)}, 자동선택 시 엔터): ").strip()
                                if not sel:
                                    best_t = items[0]
                                    max_h = 0
                                    for t in items:
                                        try: h = int(t.get("hhldCnt", 0) or 0)
                                        except: h = 0
                                        if h > max_h:
                                            max_h = h
                                            best_t = t
                                    selected_title = best_t
                                    break
                                if sel.isdigit() and 1 <= int(sel) <= len(items):
                                    selected_title = items[int(sel)-1]
                                    break
                                print(" [!] 올바른 번호를 입력해 주세요.")
                        else:
                            best_t = items[0]
                            max_h = 0
                            for t in items:
                                try: h = int(t.get("hhldCnt", 0) or 0)
                                except: h = 0
                                if h > max_h:
                                    max_h = h
                                    best_t = t
                            if max_h == 0:
                                for t in items:
                                    b_nm = str(t.get("bldNm", ""))
                                    d_nm = str(t.get("dongNm", ""))
                                    if "아파트" in b_nm or "아파트" in d_nm:
                                        best_t = t
                                        break
                            selected_title = best_t"""

tv_content = tv_content.replace(old_tv_block, new_tv_block)
with open('trade_viewer.py', 'w', encoding='utf-8') as f:
    f.write(tv_content)

print("Patch applied to both viewers!")
