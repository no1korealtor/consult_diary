import urllib.request
import urllib.parse
import json

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"

def search_kakao(query):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = urllib.parse.urlencode({"query": query, "size": 30})
    req = urllib.request.Request(f"{url}?{params}", headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            data = json.loads(res_text)
            print(f"Total count for '{query}': {data.get('meta', {}).get('total_count')}")
            for idx, doc in enumerate(data.get("documents", [])):
                print(f"[{idx+1}] Address Name: {doc.get('address_name')}")
                addr = doc.get("address", {})
                print(f"    Region: {addr.get('region_1depth_name')} {addr.get('region_2depth_name')} {addr.get('region_3depth_name') or addr.get('region_3depth_h_name')}")
                print(f"    B-code: {addr.get('b_code')}, H-code: {addr.get('h_code')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    search_kakao("중동")
