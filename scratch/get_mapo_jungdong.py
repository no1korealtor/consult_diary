import requests
import json
import urllib.request

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def get_kakao_address_info(address_str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address_str}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        if data.get("documents"):
            doc = data["documents"][0]
            addr = doc.get("address", {})
            if not addr: return None
            
            b_code = addr.get("b_code", "")
            if len(b_code) >= 10:
                return {
                    "sigunguCd": b_code[:5],
                    "bjdongCd": b_code[5:10],
                    "bun": addr.get("main_address_no", ""),
                    "ji": addr.get("sub_address_no", "0")
                }
    except Exception as e:
        print(f"카카오 API 에러: {e}")
    return None

def get_building_info(sigungu, bjdong, bun, ji):
    bun_str = str(bun).zfill(4) if bun else "0000"
    ji_str = str(ji).zfill(4) if ji else "0000"
    
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={sigungu}&bjdongCd={bjdong}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=10&pageNo=1&_type=json"
    
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
    addr = "마포구 중동 377"
    addr_info = get_kakao_address_info(addr)
    if not addr_info:
        return
    
    items = get_building_info(addr_info['sigunguCd'], addr_info['bjdongCd'], addr_info['bun'], addr_info['ji'])
    if not items:
        return
        
    out = []
    for idx, item in enumerate(items):
        out.append({
            "bldNm": item.get('bldNm'),
            "dongNm": item.get('dongNm'),
            "platArea": item.get('platArea'),
            "totArea": item.get('totArea'),
            "strctCdNm": item.get('strctCdNm'),
            "mainPurpsCdNm": item.get('mainPurpsCdNm'),
            "grndFlrCnt": item.get('grndFlrCnt'),
            "ugrndFlrCnt": item.get('ugrndFlrCnt'),
            "hhldCnt": item.get('hhldCnt'),
            "fmlyCnt": item.get('fmlyCnt'),
            "useAprDay": item.get('useAprDay'),
            "violBldYn": item.get('violBldYn'),
            "mainPurpsCd": item.get('mainPurpsCd'),
            "strctCd": item.get('strctCd')
        })
        
    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
