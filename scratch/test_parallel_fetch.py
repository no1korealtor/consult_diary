import time
import concurrent.futures
from datetime import datetime
import urllib.request
import urllib.parse
import json

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
            if isinstance(items, dict): return [items]
            return items
    except Exception as e:
        return []

def main():
    api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    sigungu = "11440" # 마포구
    
    # Generate last 24 months YYYYMM
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    months = []
    for i in range(24):
        year = current_year
        month = current_month - i
        while month <= 0:
            month += 12
            year -= 1
        months.append(f"{year}{str(month).zfill(2)}")
        
    print(f"Starting sequential query for 12 months (comparison reference)...")
    start_seq = time.time()
    seq_results = []
    for m in months[:12]:
        seq_results.extend(fetch_trade_data_month(api_trade, sigungu, m))
    end_seq = time.time()
    print(f"Sequential 12 months time: {end_seq - start_seq:.2f} seconds. Fetched {len(seq_results)} items.")

    print(f"\nStarting parallel query for 24 months using ThreadPoolExecutor...")
    start_par = time.time()
    par_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        # Submit all tasks
        futures = {executor.submit(fetch_trade_data_month, api_trade, sigungu, m): m for m in months}
        for future in concurrent.futures.as_completed(futures):
            month = futures[future]
            try:
                res = future.result()
                par_results.extend(res)
            except Exception as exc:
                print(f"Month {month} generated an exception: {exc}")
    end_par = time.time()
    print(f"Parallel 24 months time: {end_par - start_par:.2f} seconds. Fetched {len(par_results)} items.")

if __name__ == '__main__':
    main()
