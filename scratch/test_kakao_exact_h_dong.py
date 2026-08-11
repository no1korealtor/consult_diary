import urllib.request
import urllib.parse
import json

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"

def get_h_dong(addr):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = urllib.parse.urlencode({"query": addr})
    req = urllib.request.Request(f"{url}?{params}", headers=headers)
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        h_name = data["documents"][0]["address"]["region_3depth_h_name"]
        print(f"Address: {addr} -> h_name: {h_name.encode('unicode-escape').decode('utf-8')}")

get_h_dong("성산동 634-5")
get_h_dong("성산동 446")
