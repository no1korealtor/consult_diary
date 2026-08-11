import json

with open('d:/부동산업무/antigravity/consult_diary/scratch/get_building_info.py', 'r', encoding='utf-8') as f:
    content = f.read()

# update get_expos_data to return violBldYn
target = "'flrNo': item.get('flrNo') # 층수"
replacement = "'flrNo': item.get('flrNo'), # 층수\n                        'violBldYn': item.get('violBldYn', 'N') # 위반여부"
content = content.replace(target, replacement)

target2 = "return {'area': item_list[0].get('area'), 'flrNo': item_list[0].get('flrNo')}"
replacement2 = "return {'area': item_list[0].get('area'), 'flrNo': item_list[0].get('flrNo'), 'violBldYn': item_list[0].get('violBldYn', 'N')}"
content = content.replace(target2, replacement2)

with open('d:/부동산업무/antigravity/consult_diary/scratch/get_building_info.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('d:/부동산업무/antigravity/consult_diary/scratch/serve_auto_upload.py', 'r', encoding='utf-8') as f:
    content_serve = f.read()

target_serve = """        # [위반건축물여부]
        is_violation = data.get('vlratEstmTotArea', 0) > 0
        v_text = "예" if is_violation else "아니오"
        select_vuetify_dropdown(["위반건축물", "위반"], v_text)"""

replacement_serve = """        # [위반건축물여부]
        # 표제부에서 확인
        is_violation = (data.get('violBldYn') == 'Y') or (data.get('vlratEstmTotArea', 0) > 0)
        
        # 전유부(상세주소) 정보가 있다면 전유부를 최우선 기준으로 덮어쓰기!
        if expos_data:
            if expos_data.get('violBldYn') == 'Y':
                is_violation = True
            else:
                is_violation = False
                
        v_text = "예" if is_violation else "아니오"
        select_vuetify_dropdown(["위반건축물", "위반"], v_text)"""

content_serve = content_serve.replace(target_serve, replacement_serve)

with open('d:/부동산업무/antigravity/consult_diary/scratch/serve_auto_upload.py', 'w', encoding='utf-8') as f:
    f.write(content_serve)
