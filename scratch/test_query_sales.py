import urllib.request
import json
from datetime import datetime
import re

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"
api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"

def fetch_trade_data_month(sigungu, deal_ymd):
    query = f"?serviceKey={GOV_API_KEY}&LAWD_CD={sigungu}&DEAL_YMD={deal_ymd}&numOfRows=1000&pageNo=1&_type=json"
    req = urllib.request.Request(api_trade + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            if not res_text.strip(): return []
            json_data = json.loads(res_text)
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items: return []
            if isinstance(items, dict): return [items]
            return items
    except Exception as e:
        print(f"Error on {deal_ymd}: {e}")
        return []

now = datetime.now()
current_year = now.year
current_month = now.month

print("Searching for sales at '중동 395' for the last 18 months:")
for i in range(18):
    year = current_year
    month = current_month - i
    while month <= 0:
        month += 12
        year -= 1
    deal_ymd = f"{year}{str(month).zfill(2)}"
    
    items = fetch_trade_data_month("11440", deal_ymd)
    for item in items:
        jibun = str(item.get('jibun', '')).strip()
        if jibun == '395':
            print(f"Date: {item.get('dealYear')}-{item.get('dealMonth')}-{item.get('dealDay')}, "
                  f"Amount: {item.get('dealAmount')}, Floor: {item.get('floor')}, Area: {item.get('excluUseAr')}")
print("Search complete.")
