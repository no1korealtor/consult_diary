import re

def fix_title_selection(file_path, items_var_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    old_code = f'''                    selected_title = {items_var_name}[0]
                    if dong_name:
                        for t in {items_var_name}:
                            if match_dong(dong_name, t.get("dongNm", "")):
                                selected_title = t
                                break'''
                                
    # building_viewer.py indentation is less
    old_code2 = f'''        selected_title = {items_var_name}[0]
        if dong_name:
            for t in {items_var_name}:
                if match_dong(dong_name, t.get("dongNm", "")):
                    selected_title = t
                    break'''
    
    new_code = f'''                    if dong_name:
                        selected_title = {items_var_name}[0]
                        for t in {items_var_name}:
                            if match_dong(dong_name, t.get("dongNm", "")):
                                selected_title = t
                                break
                    else:
                        best_t = {items_var_name}[0]
                        max_h = 0
                        for t in {items_var_name}:
                            try:
                                h = int(t.get("hhldCnt", 0) or 0)
                            except:
                                h = 0
                            if h > max_h:
                                max_h = h
                                best_t = t
                        if max_h == 0:
                            for t in {items_var_name}:
                                b_nm = str(t.get("bldNm", ""))
                                d_nm = str(t.get("dongNm", ""))
                                if "아파트" in b_nm or "아파트" in d_nm:
                                    best_t = t
                                    break
                        selected_title = best_t'''
                        
    new_code2 = f'''        if dong_name:
            selected_title = {items_var_name}[0]
            for t in {items_var_name}:
                if match_dong(dong_name, t.get("dongNm", "")):
                    selected_title = t
                    break
        else:
            best_t = {items_var_name}[0]
            max_h = 0
            for t in {items_var_name}:
                try:
                    h = int(t.get("hhldCnt", 0) or 0)
                except:
                    h = 0
                if h > max_h:
                    max_h = h
                    best_t = t
            if max_h == 0:
                for t in {items_var_name}:
                    b_nm = str(t.get("bldNm", ""))
                    d_nm = str(t.get("dongNm", ""))
                    if "아파트" in b_nm or "아파트" in d_nm:
                        best_t = t
                        break
            selected_title = best_t'''

    if old_code in content:
        content = content.replace(old_code, new_code)
    elif old_code2 in content:
        content = content.replace(old_code2, new_code2)
    else:
        print(f"Could not find old code in {file_path}")
        return
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
fix_title_selection('d:/부동산업무/antigravity/consult_diary/trade_viewer.py', 'items')
fix_title_selection('d:/부동산업무/antigravity/consult_diary/building_viewer.py', 'titles')
