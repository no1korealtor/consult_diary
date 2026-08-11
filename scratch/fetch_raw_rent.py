import urllib.request
import json
import re
from datetime import datetime

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def fetch_trade_data_month(api_url, sigungu, deal_ymd):
    query = f"?serviceKey={GOV_API_KEY}&LAWD_CD={sigungu}&DEAL_YMD={deal_ymd}&numOfRows=1000&pageNo=1&_type=json"
    req = urllib.request.Request(api_url + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            if not res_text.strip(): return []
            json_data = json.loads(res_text)
            items = json_data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items: return []
            if isinstance(items, dict):
                return [items]
            return items
    except Exception as e:
        print(f"Error on {deal_ymd}: {e}")
        return []

api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
now = datetime.now()
current_year = now.year
current_month = now.month

print("Fetching last 12 months rent data for 중동 395...")
target_jibun = "395"

for i in range(12):
    year = current_year
    month = current_month - i
    while month <= 0:
        month += 12
        year -= 1
    deal_ymd = f"{year}{str(month).zfill(2)}"
    
    items = fetch_trade_data_month(api_rent, "11440", deal_ymd)
    for item in items:
        # Check if jibun matches 395
        jibun = str(item.get('jibun', '')).strip()
        # Clean jibun
        jibun_clean = re.sub(r'\D', '', jibun)
        if jibun == target_jibun or jibun_clean == target_jibun:
            apt_nm = item.get('aptNm', '')
            print(f"[{deal_ymd}] Full item: {json.dumps(item, ensure_ascii=False)}")
