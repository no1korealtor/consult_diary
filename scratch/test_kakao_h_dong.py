import urllib.request
import urllib.parse
import json

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"

def check_address(addr):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = urllib.parse.urlencode({"query": addr})
    req = urllib.request.Request(f"{url}?{params}", headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            data = json.loads(res_text)
            if data.get("documents"):
                doc = data["documents"][0]
                addr_info = doc.get("address", {})
                road_info = doc.get("road_address", {})
                print(f"Address: {addr}")
                print(f"  B-Dong (Legal): {addr_info.get('region_3depth_name')}")
                print(f"  H-Dong (Admin): {addr_info.get('region_3depth_h_name')}")
                print(f"  H-Code (Admin Code): {addr_info.get('h_code')}")
                print(f"  B-Code (Legal Code): {addr_info.get('b_code')}")
            else:
                print(f"No results for {addr}")
    except Exception as e:
        print(f"Error: {e}")

check_address("성산동 634-5")
check_address("성산동 446") # Seongsan Siyoung
