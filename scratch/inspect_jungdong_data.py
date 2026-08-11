import urllib.request
import json

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def get_building_title_info(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=10&pageNo=1&_type=json"
    
    req = urllib.request.Request(url + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Accept", "application/json, text/plain, */*")
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            return json.loads(res_text)
    except Exception as e:
        return {"error": str(e)}

def get_expos_info_list(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
    
    req = urllib.request.Request(url + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Accept", "application/json, text/plain, */*")
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            return json.loads(res_text)
    except Exception as e:
        return {"error": str(e)}

# Mapo-gu Jung-dong 395
title_res = get_building_title_info("11440", "12600", "0395", "0000")
print("=== TITLES ===")
items = title_res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
if isinstance(items, dict):
    items = [items]
for it in items:
    print(f"BldNm: {it.get('bldNm')}, DongNm: {it.get('dongNm')}, grndFlrCnt: {it.get('grndFlrCnt')}, hhldCnt: {it.get('hhldCnt')}")

expos_res = get_expos_info_list("11440", "12600", "0395", "0000")
print("\n=== EXPOS SAMPLE ===")
ex_items = expos_res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
if isinstance(ex_items, dict):
    ex_items = [ex_items]
print(f"Total expos items: {len(ex_items)}")
distinct_dongs = set()
for it in ex_items:
    distinct_dongs.add(it.get('dongNm'))
print("Distinct Dongs in Expos:", distinct_dongs)
