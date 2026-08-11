import urllib.request
import urllib.parse
import json

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"
api_url = "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"
query = f"?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202606&numOfRows=10&pageNo=1&_type=json"

print("Sending request to:", api_url + query)

req = urllib.request.Request(api_url + query)
req.add_header("User-Agent", "Mozilla/5.0")

try:
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        res_text = response.read().decode('utf-8')
        print("Response text:")
        print(res_text)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.reason)
    try:
        print(e.read().decode('utf-8'))
    except Exception:
        pass
except Exception as e:
    print("Error:", e)
