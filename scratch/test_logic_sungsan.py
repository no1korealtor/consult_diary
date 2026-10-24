from get_building_info import get_building_data, get_expos_data, get_floor_data
import urllib.parse
import urllib.request
import json

address_query = "성산동 200-109"
query = urllib.parse.quote(address_query)
vworld_url = f"http://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:900913&size=1&page=1&query={query}&type=address&category=parcel&format=json&errorformat=json&key=80194C85-0EE3-3220-A3C1-3268AD8756B9"

req = urllib.request.Request(vworld_url)
req.add_header('Referer', 'http://localhost')
res = urllib.request.urlopen(req)
vworld_data = json.loads(res.read().decode('utf-8'))

items = vworld_data.get('response', {}).get('result', {}).get('items', [])
pnu = items[0].get('id', '')
sigunguCd = pnu[0:5]
bjdongCd = pnu[5:10]
bun = pnu[11:15]
ji = pnu[15:19]

dong_name = ""
ho_name = "201"

bldg_data = get_building_data(sigunguCd, bjdongCd, bun, ji)
expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, dong_name, ho_name) if ho_name else None

if not expos_data and bldg_data.get('regstrGbCd') == '1' and ho_name:
    floor_str = ""
    if ho_name.upper().startswith('B'):
        num = ho_name[1:-2] if len(ho_name) > 3 else (ho_name[1:] if len(ho_name)>1 else '1')
        if not num: num = '1'
        floor_str = f"지하{num}"
    elif len(ho_name) >= 3:
        floor_str = ho_name[:-2]
    elif len(ho_name) in (1, 2):
        floor_str = ho_name
        
    if floor_str:
        print(f"[*] 다가구/단독 주택 감지됨. 층별개요 조회 시도 (추정 층: {floor_str}층)")
        expos_data = get_floor_data(sigunguCd, bjdongCd, bun, ji, floor_str)

totArea = bldg_data.get('totArea', '')
flrNo = expos_data.get('flrNo', '') if expos_data else ''
area = expos_data.get('area', '') if expos_data else totArea
supply_area = expos_data.get('supply_area', '') if expos_data else area

print("bldg totArea:", totArea)
print("final flrNo:", flrNo)
print("final area:", area)
print("final supply_area:", supply_area)
