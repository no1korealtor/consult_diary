import urllib.request
import json
import os

GOV_API_KEY = "S%2B2v1m048n2W8YtZ%2FsT1zJ4R3z627uQ3a36K2uC4bO5G4m8Ue3a2oP9wD%2F7vK2e8%2BbO%2Bx1n8k4%2F3t8g%2Bx1a2w%3D%3D" # Let's find the key from trade_viewer.py

# Read the actual key from trade_viewer.py
with open("trade_viewer.py", "r", encoding="utf-8") as f:
    for line in f:
        if "GOV_API_KEY =" in line:
            GOV_API_KEY = line.split("=")[1].strip().strip('"').strip("'")
            break

print("Using GOV_API_KEY:", GOV_API_KEY)

# 1. 단독/다가구 매매 (SHTrade)
api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
query_trade = f"?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202405&numOfRows=10&pageNo=1&_type=json"
req_trade = urllib.request.Request(api_trade + query_trade)
req_trade.add_header("User-Agent", "Mozilla/5.0")

try:
    with urllib.request.urlopen(req_trade) as response:
        res = json.loads(response.read().decode('utf-8'))
        items = res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if items:
            if isinstance(items, dict): items = [items]
            print("\n--- SHTrade (매매) First Item Keys and Values ---")
            for k, v in items[0].items():
                print(f"  {k}: {v}")
        else:
            print("\nSHTrade returned no items.")
except Exception as e:
    print("SHTrade error:", e)

# 2. 단독/다가구 전월세 (SHRent)
api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"
query_rent = f"?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202405&numOfRows=10&pageNo=1&_type=json"
req_rent = urllib.request.Request(api_rent + query_rent)
req_rent.add_header("User-Agent", "Mozilla/5.0")

try:
    with urllib.request.urlopen(req_rent) as response:
        res = json.loads(response.read().decode('utf-8'))
        items = res.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        if items:
            if isinstance(items, dict): items = [items]
            print("\n--- SHRent (전월세) First Item Keys and Values ---")
            for k, v in items[0].items():
                print(f"  {k}: {v}")
        else:
            print("\nSHRent returned no items.")
except Exception as e:
    print("SHRent error:", e)
