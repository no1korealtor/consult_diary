import time
import concurrent.futures
from datetime import datetime
import urllib.request
import urllib.parse
import json
import re

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

def normalize_jibun(j):
    if not j: return ""
    j = str(j).strip()
    parts = re.split(r'[-]', j)
    norm_parts = []
    for p in parts:
        p_clean = re.sub(r'\D', '', p)
        if p_clean:
            norm_parts.append(str(int(p_clean)))
    return "-".join(norm_parts)

def get_recent_transactions_parallel(sigungu, bun, ji, prop_type, bjdong_nm=None):
    if prop_type == '1':
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcAptRent/getRTMSDataSvcAptRent"
    elif prop_type == '2':
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent"
    elif prop_type == '3':
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcOffiRent/getRTMSDataSvcOffiRent"
    else:
        api_trade = "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
        api_rent = "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"

    target_jibun = normalize_jibun(f"{bun}-{ji}")
    print(f" -> Parallel fetch target: {target_jibun}")

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

    matches = []
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        # Submit trade queries
        trade_futures = {
            executor.submit(fetch_trade_data_month, api_trade, sigungu, m): m 
            for m in months
        }
        # Submit rent queries
        rent_futures = {
            executor.submit(fetch_trade_data_month, api_rent, sigungu, m): m 
            for m in months
        }
        
        # Gather trades
        for future in concurrent.futures.as_completed(trade_futures):
            month = trade_futures[future]
            try:
                items = future.result()
                for item in items:
                    if normalize_jibun(item.get('jibun', '')) == target_jibun:
                        item['_trade_type'] = '매매'
                        matches.append(item)
            except Exception as e:
                print(f"Trade Exception for {month}: {e}")
                
        # Gather rents
        for future in concurrent.futures.as_completed(rent_futures):
            month = rent_futures[future]
            try:
                items = future.result()
                for item in items:
                    if normalize_jibun(item.get('jibun', '')) == target_jibun:
                        monthly_val = item.get('monthlyRent', 0)
                        if monthly_val is None: monthly_val = 0
                        is_wolse = int(str(monthly_val).replace(',', '')) > 0
                        item['_trade_type'] = '월세' if is_wolse else '전세'
                        matches.append(item)
            except Exception as e:
                print(f"Rent Exception for {month}: {e}")
                
    print(f"Fetched in parallel in {time.time() - start_time:.2f} seconds.")
    return matches

def count_by_months(items, months_limit):
    now = datetime.now()
    count = 0
    for item in items:
        try:
            year = int(item.get('dealYear', 0))
            month = int(item.get('dealMonth', 0))
            diff = (now.year - year) * 12 + (now.month - month)
            if diff < months_limit:
                count += 1
        except:
            pass
    return count

def main():
    # Test Mapo Hyundai Apartments (11440, bun=445, ji=5, prop_type='1')
    sigungu = "11440"
    bun = "445"
    ji = "5"
    prop_type = "1"
    
    matches = get_recent_transactions_parallel(sigungu, bun, ji, prop_type)
    print(f"Total matches found in 24 months: {len(matches)}")
    
    trades = [m for m in matches if m['_trade_type'] == '매매']
    jeonses = [m for m in matches if m['_trade_type'] == '전세']
    wolses = [m for m in matches if m['_trade_type'] == '월세']
    
    t_6 = count_by_months(trades, 6)
    j_6 = count_by_months(jeonses, 6)
    w_6 = count_by_months(wolses, 6)
    
    t_12 = count_by_months(trades, 12)
    j_12 = count_by_months(jeonses, 12)
    w_12 = count_by_months(wolses, 12)
    
    t_24 = count_by_months(trades, 24)
    j_24 = count_by_months(jeonses, 24)
    w_24 = count_by_months(wolses, 24)
    
    print("\n========================================================")
    print(" [실거래 수집 요약 (총 24개월)]")
    print("--------------------------------------------------------")
    print(f" - 최근  6개월: 매매 {t_6}건 / 전세 {j_6}건 / 월세 {w_6}건 (총 {t_6+j_6+w_6}건)")
    print(f" - 최근 12개월: 매매 {t_12}건 / 전세 {j_12}건 / 월세 {w_12}건 (총 {t_12+j_12+w_12}건)")
    print(f" - 최근 24개월: 매매 {t_24}건 / 전세 {j_24}건 / 월세 {w_24}건 (총 {t_24+j_24+w_24}건)")
    print("========================================================")

if __name__ == '__main__':
    main()
