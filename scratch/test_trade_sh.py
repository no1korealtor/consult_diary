import urllib.request
import urllib.parse
import json

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def test_api(name, url):
    query = f"?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202606&numOfRows=5&pageNo=1&_type=json"
    print(f"\n--- Testing {name} ---")
    req = urllib.request.Request(url + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            data = json.loads(res_text)
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if items:
                if isinstance(items, dict):
                    items = [items]
                print("First item keys:", list(items[0].keys()))
                print("First item sample:", items[0])
            else:
                print("No items returned.")
    except Exception as e:
        print("Error:", e)

test_api("SHTrade (단독/다가구 매매)", "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade")
test_api("SHRent (단독/다가구 전월세)", "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent")
