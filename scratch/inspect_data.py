import urllib.request
import json
import re

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
            json_data = json.loads(res_text)
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items: return []
            if isinstance(items, dict):
                return [items]
            return items
    except Exception as e:
        print("Error fetching title:", e)
        return []

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
            json_data = json.loads(res_text)
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items: return []
            if isinstance(items, dict):
                return [items]
            return items
    except Exception as e:
        print("Error fetching expos:", e)
        return []

# Sigungu and bjdong for 서울 마포구 중동 395
# sigunguCd: 11440, bjdongCd: 12600, bun: 395, ji: 0
titles = get_building_title_info("11440", "12600", 395, 0)
print(f"Titles found: {len(titles)}")
for idx, t in enumerate(titles):
    print(f"Title {idx}: bldNm={t.get('bldNm')}, dongNm={t.get('dongNm')}, platArea={t.get('platArea')}, grndFlrCnt={t.get('grndFlrCnt')}")

expos = get_expos_info_list("11440", "12600", 395, 0)
print(f"\nExpos records found: {len(expos)}")
dongs_in_expos = set()
for e in expos[:20]:
    print(f"Expos sample: dongNm={e.get('dongNm')}, flrNo={e.get('flrNo')}, hoNm={e.get('hoNm')}, mainPurpsCdNm={e.get('mainPurpsCdNm')}")
    dongs_in_expos.add(e.get('dongNm'))

print(f"\nUnique dongs in first 100 expos records: {dongs_in_expos}")
