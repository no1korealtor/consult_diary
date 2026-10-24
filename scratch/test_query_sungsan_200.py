import urllib.request
import urllib.parse
import json
import re

from get_building_info import get_building_data, get_expos_data

query = urllib.parse.quote("성산동 200-109")
vworld_url = f"http://api.vworld.kr/req/search?service=search&request=search&version=2.0&crs=EPSG:900913&size=1&page=1&query={query}&type=address&category=parcel&format=json&errorformat=json&key=80194C85-0EE3-3220-A3C1-3268AD8756B9"

req = urllib.request.Request(vworld_url)
req.add_header('Referer', 'http://localhost')
res = urllib.request.urlopen(req)
vworld_data = json.loads(res.read().decode('utf-8'))

items = vworld_data.get('response', {}).get('result', {}).get('items', [])
print("VWorld:", items)

if items:
    pnu = items[0].get('id', '')
    sigunguCd = pnu[0:5]
    bjdongCd = pnu[5:10]
    bun = pnu[11:15]
    ji = pnu[15:19]
    print(f"pnu: {pnu}")
    print(f"sigunguCd: {sigunguCd}, bjdongCd: {bjdongCd}, bun: {bun}, ji: {ji}")

    # For testing, let's say "102호" or something. The user didn't specify. I'll just check what get_expos_data returns if we pass no dong/ho.
    bldg_data = get_building_data(sigunguCd, bjdongCd, bun, ji)
    print("Building Data:", bldg_data)
    
    # Just try to get expos data for dong "", ho ""
    expos_data = get_expos_data(sigunguCd, bjdongCd, bun, ji, "", "101")
    print("Expos Data (101):", expos_data)

    expos_data2 = get_expos_data(sigunguCd, bjdongCd, bun, ji, "", "202")
    print("Expos Data (202):", expos_data2)
