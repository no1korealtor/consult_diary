import sys
import io
import re

with open('d:/부동산업무/antigravity/consult_diary/scratch/serve_auto_upload.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_building_data import
content = content.replace('from get_building_info import get_building_data', 'from get_building_info import get_building_data, get_expos_data')

# Insert detail address parsing
insert_idx = content.find('print(f" -> 추출된 법정동코드:')
detail_code = '''
        # 상세주소(호수) 추출
        detail_val = ""
        for inp in inputs:
            ph = inp.get_attribute("placeholder") or ""
            lbl = inp.get_attribute("aria-label") or ""
            if "예시" in ph or "동, 층, 호수" in ph or "상세" in lbl:
                detail_val = inp.get_attribute("value") or ""
                break
                
        dong_name = ""
        ho_name = ""
        if detail_val:
            import re
            dong_match = re.search(r'([0-9]+)동', detail_val)
            ho_match = re.search(r'([0-9]+)호', detail_val)
            if dong_match: dong_name = dong_match.group(1)
            if ho_match: ho_name = ho_match.group(1)
            
'''
content = content[:insert_idx] + detail_code + content[insert_idx:]

# Update API call
content = content.replace('data = get_building_data(sigunguCd, bjdongCd, bun, ji)', 'data = get_building_data(sigunguCd, bjdongCd, bun, ji)\n        expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, dong_name, ho_name) if ho_name else None')

# Update print
content = content.replace('print(f" -> 성공! 연면적: {data[\'totArea\']}㎡, 총주차: {data[\'totalParking\']}대, 승인년도: {data[\'aprYear\']}년")', 'print(f" -> 성공! 연면적: {data[\'totArea\']}㎡, 총주차: {data[\'totalParking\']}대, 승인년도: {data[\'aprYear\']}년")\n        if expos_data:\n            print(f" -> [전유부 성공!] {dong_name}동 {ho_name}호 전용면적: {expos_data.get(\'area\')}㎡, 층: {expos_data.get(\'flrNo\')}층")')

with open('d:/부동산업무/antigravity/consult_diary/scratch/serve_auto_upload.py', 'w', encoding='utf-8') as f:
    f.write(content)
