import requests
import json
from datetime import datetime

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def fetch_data(api_url, sigungu, deal_ymd):
    query_params = {
        'serviceKey': GOV_API_KEY,
        'LAWD_CD': sigungu,
        'DEAL_YMD': deal_ymd,
        'numOfRows': 1000,
        'pageNo': 1,
        '_type': 'json'
    }
    try:
        r = requests.get(api_url, params=query_params, timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error fetching {deal_ymd}: {e}")
    return None

def normalize_jibun(jibun_str):
    if not jibun_str: return ""
    import re
    parts = re.split(r'[-]', str(jibun_str).strip())
    normalized_parts = []
    for p in parts:
        p_clean = re.sub(r'\D', '', p)
        if p_clean:
            normalized_parts.append(str(int(p_clean)))
    return "-".join(normalized_parts)

def match_masked_jibun(api_jibun, target_jibun):
    if not api_jibun or not target_jibun:
        return False
    import re
    api_clean = re.sub(r'\s+', '', str(api_jibun))
    target_clean = re.sub(r'\s+', '', str(target_jibun))
    
    api_parts = api_clean.split('-')
    target_parts = target_clean.split('-')
    
    if len(api_parts) != len(target_parts):
        return False
        
    for a, t in zip(api_parts, target_parts):
        if a == '*' or t == '*':
            continue
        if len(a) != len(t):
            return False
        for c1, c2 in zip(a, t):
            if c1 == '*' or c2 == '*':
                continue
            if c1 != c2:
                return False
    return True

def run_test():
    sigungu = "11440"
    target_jibun = "34-15"
    
    # Let's check last 12 months
    months = []
    now = datetime.now()
    year = now.year
    month = now.month
    for i in range(12):
        y = year
        m = month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append(f"{y}{str(m).zfill(2)}")
        
    print(f"Checking transaction data for {sigungu} / {target_jibun} over months: {months}")
    
    # 1. Rowhouse / Villa (Type 2)
    rh_trade_url = "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade"
    rh_rent_url = "http://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent"
    
    rh_trades = []
    rh_rents = []
    
    for m in months:
        # Trade
        data = fetch_data(rh_trade_url, sigungu, m)
        if data:
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict): items = [items]
            for item in items:
                jibun = normalize_jibun(item.get('jibun', ''))
                if jibun == target_jibun:
                    rh_trades.append(item)
                    
        # Rent
        data = fetch_data(rh_rent_url, sigungu, m)
        if data:
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict): items = [items]
            for item in items:
                jibun = normalize_jibun(item.get('jibun', ''))
                if jibun == target_jibun:
                    rh_rents.append(item)
                    
    print(f"\n--- Rowhouse/Villa Results for {target_jibun} ---")
    print(f"Total Trades: {len(rh_trades)}")
    for t in rh_trades:
        print(f"  [매매] {t.get('dealYear')}-{t.get('dealMonth')} | Area: {t.get('excluUseAr')} | Amt: {t.get('dealAmount')} | Floor: {t.get('floor')}")
    print(f"Total Rents: {len(rh_rents)}")
    for t in rh_rents:
        print(f"  [전월세] {t.get('dealYear')}-{t.get('dealMonth')} | Area: {t.get('excluUseAr')} | Deposit: {t.get('deposit')} | Monthly: {t.get('monthlyRent')}")

    # 2. Single-Family / Multi-Family (Type 4)
    sh_trade_url = "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
    sh_rent_url = "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"
    
    sh_trades = []
    sh_rents = []
    
    for m in months:
        # Trade
        data = fetch_data(sh_trade_url, sigungu, m)
        if data:
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict): items = [items]
            for item in items:
                # Single family trade returns masked jibun sometimes
                if match_masked_jibun(item.get('jibun', ''), target_jibun):
                    sh_trades.append(item)
                    
        # Rent
        data = fetch_data(sh_rent_url, sigungu, m)
        if data:
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict): items = [items]
            for item in items:
                # Single family rent does not return jibun in API!
                # We filter by buildYear and houseType in trade_viewer.py
                # Let's inspect the rent data to see if we can identify any transactions
                # Single family rent results for whole sigungu:
                sh_rents.append(item)
                
    print(f"\n--- Single-Family/Multi-Family Results for {target_jibun} ---")
    print(f"Total Trades: {len(sh_trades)}")
    for t in sh_trades:
        print(f"  [매매] {t.get('dealYear')}-{t.get('dealMonth')} | Area: {t.get('totalFloorAr')} | Amt: {t.get('dealAmount')}")
        
    print(f"Inspection of Sigungu {sigungu} Single-Family Rents:")
    # Filter Sigunu rents by buildYear (around 1990-2015) if we want, but let's see how many there are total
    # Let's see if we can find any that might correspond to this property
    # Let's write the whole Sigungu rent response for one month to understand if there is anything.
    print(f"Single-Family Sigungu rents collected: {len(sh_rents)} items total across 12 months.")

if __name__ == '__main__':
    run_test()
