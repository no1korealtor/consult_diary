import json

with open('d:/부동산업무/antigravity/consult_diary/scratch/get_building_info.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_func = '''
def get_basis_ouln_data(sigungu, bjdong, bun, ji):
    import urllib.request, json
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrBasisOulnInfo"
    query = f"?serviceKey={API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun}&ji={ji}&numOfRows=10&pageNo=1&_type=json"
    
    try:
        req = urllib.request.Request(url + query)
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            res_body = response.read().decode('utf-8')
            if not res_body.strip(): return 0
            data = json.loads(res_body)
            items = data.get("response", {}).get("body", {}).get("items", {})
            if not items: return 0
            
            item_list = items.get("item", [])
            if isinstance(item_list, dict): item_list = [item_list]
            
            if item_list:
                item = item_list[0]
                parking = 0
                for p_type in ['indrAutoUtcnt', 'indrMechUtcnt', 'oudrAutoUtcnt', 'oudrMechUtcnt']:
                    val = item.get(p_type, 0)
                    if val: parking += int(val)
                return parking
    except:
        pass
    return 0
'''

# insert before if __name__ == "__main__":
idx = content.find('def get_expos_data')
if idx != -1:
    content = content[:idx] + new_func + '\n' + content[idx:]

# update get_building_data to check get_basis_ouln_data if parking is 0
target = "building_info['canPark'] = \"Y\" if parking > 0 else \"N\""
replacement = '''building_info['canPark'] = "Y" if parking > 0 else "N"
            
            # 주차대수가 0이면 총괄표제부를 한번 더 확인
            if parking == 0:
                basis_parking = get_basis_ouln_data(sigungu, bjdong, bun, ji)
                if basis_parking > 0:
                    building_info['totalParking'] = str(basis_parking)
                    building_info['canPark'] = "Y"
'''
content = content.replace(target, replacement)

with open('d:/부동산업무/antigravity/consult_diary/scratch/get_building_info.py', 'w', encoding='utf-8') as f:
    f.write(content)
