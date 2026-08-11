import urllib.request
import json
import re
import requests

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"

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
                    "bjdongNm": addr.get("region_3depth_name", ""),
                    "bun": addr.get("main_address_no", ""),
                    "ji": addr.get("sub_address_no", "0"),
                    "road_address": doc.get("road_address", {}).get("address_name", "") if doc.get("road_address") else ""
                }
    except Exception as e:
        print(f"카카오 API 에러: {e}")
    return None

def test_pnu():
    addr_info = get_kakao_address_info("새터산5길 36")
    if not addr_info:
        print("Failed to get address info")
        return
        
    bun_val = str(addr_info['bun']).zfill(4) if addr_info['bun'] else "0000"
    ji_val = str(addr_info['ji']).zfill(4) if addr_info['ji'] else "0000"
    pnu = f"{addr_info['sigunguCd']}{addr_info['bjdongCd']}1{bun_val}{ji_val}"
    
    # Query VWorld
    url = f"http://api.vworld.kr/ned/data/getLandUseAttr?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=100&pageNo=1"
    req = urllib.request.Request(url)
    req.add_header("Referer", "http://localhost")
    
    out_lines = []
    out_lines.append(f"Address Info: {addr_info}")
    out_lines.append(f"PNU: {pnu}")
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get('landUses', {}).get('field', [])
            if not items:
                items = data.get('response', {}).get('landUses', {}).get('field', [])
            out_lines.append(f"Number of items: {len(items)}")
            for item in items:
                name = item.get('prposAreaDstrcCodeNm', '')
                code = item.get('prposAreaDstrcCode', '')
                out_lines.append(f" - {name} ({code})")
    except Exception as e:
        out_lines.append(f"VWorld query error: {e}")
        
    with open("test_address_info_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print("Done")

if __name__ == "__main__":
    test_pnu()
