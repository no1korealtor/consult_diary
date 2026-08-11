import urllib.request
import urllib.parse
import json

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
url = "https://dapi.kakao.com/v2/local/search/address.json"
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

params = urllib.parse.urlencode({"query": "중동 395"})
req = urllib.request.Request(f"{url}?{params}", headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        for doc in data.get("documents", []):
            print("Address Name:", doc.get("address_name"))
            print("Road Address:", doc.get("road_address", {}).get("address_name") if doc.get("road_address") else "None")
            print("B Code:", doc.get("address", {}).get("b_code"))
            print("---")
except Exception as e:
    print("Error:", e)
