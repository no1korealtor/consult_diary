import requests
import json
import urllib.request

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def get_expos_info_full(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
    
    try:
        req = urllib.request.Request(url + query)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json, text/plain, */*")
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            json_data = json.loads(res_text)
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            return items
    except Exception as e:
        print(f"정부 API 에러: {e}")
        return None

def main():
    # 마포구 중동 377 codes: sigunguCd: 11440, bjdongCd: 12600, bun: 377, ji: 0
    items = get_expos_info_full("11440", "12600", "377", "0")
    if not items:
        print("전유부 정보 없음")
        return
    
    if isinstance(items, dict):
        items = [items]
        
    out = []
    for item in items:
        out.append({
            "dongNm": item.get('dongNm'),
            "hoNm": item.get('hoNm'),
            "flrNo": item.get('flrNo'),
            "flrNoNm": item.get('flrNoNm'),
            "mainPurpsCdNm": item.get('mainPurpsCdNm'),
            "violBldYn": item.get('violBldYn')
        })
        
    with open("expos_result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
