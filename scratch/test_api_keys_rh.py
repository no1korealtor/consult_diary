import urllib.request
import json

# Read the actual key from trade_viewer.py
GOV_API_KEY = ""
with open("trade_viewer.py", "r", encoding="utf-8") as f:
    for line in f:
        if "GOV_API_KEY =" in line:
            GOV_API_KEY = line.split("=")[1].strip().strip('"').strip("'")
            break

print("Using GOV_API_KEY:", GOV_API_KEY)

# 1. 연립다세대 매매 (RHTrade)
api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
query_trade = f"?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202405&numOfRows=10&pageNo=1&_type=json"
req_trade = urllib.request.Request(api_trade + query_trade)
req_trade.add_header("User-Agent", "Mozilla/5.0")

try:
    with urllib.request.urlopen(req_trade) as response:
        res = json.loads(response.read().decode('utf-8'))
        items = res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if items:
            if isinstance(items, dict): items = [items]
            print("\n--- RHTrade (매매) First Item Keys and Values ---")
            for k, v in items[0].items():
                print(f"  {k}: {v}")
        else:
            print("\nRHTrade returned no items.")
except Exception as e:
    print("RHTrade error:", e)

# 2. 연립다세대 전월세 (RHRent)
api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent"
query_rent = f"?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202405&numOfRows=10&pageNo=1&_type=json"
req_rent = urllib.request.Request(api_rent + query_rent)
req_rent.add_header("User-Agent", "Mozilla/5.0")

try:
    with urllib.request.urlopen(req_rent) as response:
        res = json.loads(response.read().decode('utf-8'))
        items = res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if items:
            if isinstance(items, dict): items = [items]
            print("\n--- RHRent (전월세) First Item Keys and Values ---")
            for k, v in items[0].items():
                print(f"  {k}: {v}")
        else:
            print("\nRHRent returned no items.")
except Exception as e:
    print("RHRent error:", e)
