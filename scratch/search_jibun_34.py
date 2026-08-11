# -*- coding: utf-8 -*-
import requests
import json

url = 'http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo'
key = '88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770'

with open("search_jibun_34_result.txt", "w", encoding="utf-8") as f_out:
    for ji in range(100):
        query_params = {
            'serviceKey': key,
            'sigunguCd': '11440',
            'bjdongCd': '11100',
            'platGbCd': '0',
            'bun': '0034',
            'ji': str(ji).zfill(4),
            'numOfRows': 10,
            'pageNo': 1,
            '_type': 'json'
        }
        try:
            r = requests.get(url, params=query_params, timeout=3)
            if r.status_code == 200:
                data = r.json()
                items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
                if items:
                    if isinstance(items, dict):
                        items = [items]
                    for item in items:
                        ji_str = f"34-{ji}"
                        bld_nm = item.get('bldNm', '')
                        main_purp = item.get('mainPurpsCdNm', '')
                        plat_area = item.get('platArea', '')
                        f_out.write(f"Jibun: {ji_str} | bldNm: {bld_nm} | mainPurp: {main_purp} | platArea: {plat_area}\n")
        except Exception as e:
            pass
    print("Done search Jibun 34")
