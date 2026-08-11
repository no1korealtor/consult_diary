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
        r = requests.get(api_url, params=query_params, timeout=10)
        if r.status_code == 200:
            try:
                res_data = r.json()
                return res_data
            except json.JSONDecodeError:
                print(f"JSON decode failed. Raw response: {r.text[:500]}")
        else:
            print(f"Non-200 status code: {r.status_code}. Raw response: {r.text[:500]}")
    except Exception as e:
        print(f"Error fetching {deal_ymd} from {api_url.split('/')[-1]}: {e}")
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

def run_test():
    sigungu = "11440"
    target_jibun = "34-15"
    
    # Check last 12 months
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
        
    print(f"Direct transaction check for Shinsu-dong 34-15 over: {months}")
    
    apis = {
        'RH_Trade (연립다세대 매매)': "http://apis.data.go.kr/1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade",
        'RH_Rent (연립다세대 전월세)': "http://apis.data.go.kr/1613000/RTMSDataSvcRHRent/getRTMSDataSvcRHRent",
        'SH_Trade (단독다가구 매매)': "http://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade",
        'SH_Rent (단독다가구 전월세)': "http://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent"
    }
    
    results = {name: [] for name in apis}
    
    for name, api_url in apis.items():
        for m in months:
            data = fetch_data(api_url, sigungu, m)
            if data:
                if not isinstance(data, dict):
                    print(f"[{name}] Warning: Data is not a dict: {repr(data)[:200]}")
                    continue
                resp_val = data.get('response')
                if not isinstance(resp_val, dict):
                    print(f"[{name}] Warning: response is not a dict: {repr(data)[:200]}")
                    continue
                body_val = resp_val.get('body')
                if not isinstance(body_val, dict):
                    print(f"[{name}] Warning: body is not a dict: {repr(data)[:200]}")
                    continue
                items = body_val.get('items')
                if not isinstance(items, dict):
                    # Sometimes items is empty string if there are no results
                    continue
                item_val = items.get('item', [])
                if not item_val:
                    continue
                if isinstance(item_val, dict):
                    item_val = [item_val]
                
                for item in item_val:
                    # For 단독다가구 전월세, jibun is not in the data, so let's see if we match anything else, 
                    # or print it if it matches our criteria (e.g. umdNm matches '신수동' and building year matches)
                    if 'SH_Rent' in name:
                        umd = item.get('umdNm') or item.get('dong') or ""
                        if '신수동' in umd:
                            # Just collect all Shinsu-dong single-family rents to inspect
                            results[name].append(item)
                    else:
                        jibun = normalize_jibun(item.get('jibun', ''))
                        if jibun == target_jibun:
                            results[name].append(item)
                            
    print("\n================ RESULT SUMMARY ================")
    for name, items in results.items():
        print(f"\n* {name}: {len(items)} items found")
        if 'SH_Rent' in name:
            # Let's see if there are any rents in Shinsu-dong
            print(f"  (Total Shinsu-dong single-family rents: {len(items)})")
            # Let's inspect them
            for item in items[:5]:
                print(f"    - Month: {item.get('dealYear')}-{item.get('dealMonth')} | Area: {item.get('totalFloorAr') or item.get('area')} | Deposit: {item.get('deposit')} | Rent: {item.get('monthlyRent')} | HouseType: {item.get('houseType')}")
        else:
            for item in items:
                print(f"    - Month: {item.get('dealYear')}-{item.get('dealMonth')} | Area: {item.get('excluUseAr') or item.get('totalFloorAr')} | Amt/Deposit: {item.get('dealAmount') or item.get('deposit')} | Floor: {item.get('floor')}")

if __name__ == '__main__':
    run_test()
