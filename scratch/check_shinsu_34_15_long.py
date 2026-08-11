# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import re
import json

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
        r = requests.get(api_url, params=query_params, timeout=5)
        if r.status_code == 200:
            try:
                return r.json()
            except:
                pass
    except:
        pass
    return None

def normalize_jibun(jibun_str):
    if not jibun_str: return ""
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
    
    # Check last 60 months (5 years)
    months = []
    now = datetime.now()
    year = now.year
    month = now.month
    for i in range(60):
        y = year
        m = month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append(f"{y}{str(m).zfill(2)}")
        
    print(f"Checking 5-year history for Shinsu-dong 34-15...")
    
    apis = {
        'RH_Trade (연립다세대 매매)': "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade",
        'RH_Rent (연립다세대 전월세)': "http://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent",
        'SH_Trade (단독다가구 매매)': "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade"
    }
    
    results = {name: [] for name in apis}
    
    for name, api_url in apis.items():
        for m in months:
            data = fetch_data(api_url, sigungu, m)
            if data and isinstance(data, dict):
                resp_val = data.get('response')
                if isinstance(resp_val, dict):
                    body_val = resp_val.get('body')
                    if isinstance(body_val, dict):
                        items = body_val.get('items')
                        if isinstance(items, dict):
                            item_val = items.get('item', [])
                            if item_val:
                                if isinstance(item_val, dict):
                                    item_val = [item_val]
                                for item in item_val:
                                    if 'SH_Trade' in name:
                                        if match_masked_jibun(item.get('jibun', ''), target_jibun):
                                            results[name].append(item)
                                    else:
                                        jibun = normalize_jibun(item.get('jibun', ''))
                                        if jibun == target_jibun:
                                            results[name].append(item)
                            
    print("\n================ 5-YEAR HISTORICAL RESULTS ================")
    found_any = False
    for name, items in results.items():
        if items:
            found_any = True
            print(f"\n* {name}: {len(items)} items found")
            for t in items:
                print(f"  - Date: {t.get('dealYear')}-{t.get('dealMonth')} | Area: {t.get('excluUseAr') or t.get('totalFloorAr')} | Amt/Deposit: {t.get('dealAmount') or t.get('deposit')} | Floor: {t.get('floor', '-')}")
    if not found_any:
        print("\nNo historical transaction records found in the last 5 years in any of the 3 APIs.")

if __name__ == '__main__':
    run_test()
