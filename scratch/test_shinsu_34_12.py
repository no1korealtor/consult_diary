# -*- coding: utf-8 -*-
import requests
import json

url = 'http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo'
key = '88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770'

query_params = {
    'serviceKey': key,
    'sigunguCd': '11440',
    'bjdongCd': '11100',
    'platGbCd': '0',
    'bun': '0034',
    'ji': '0012',
    'numOfRows': 10,
    'pageNo': 1,
    '_type': 'json'
}

with open("test_shinsu_34_12_result.txt", "w", encoding="utf-8") as f_out:
    try:
        r = requests.get(url, params=query_params, timeout=10)
        f_out.write(f"Status Code: {r.status_code}\n")
        f_out.write(f"Response: {r.text}\n")
    except Exception as e:
        f_out.write(f"Error: {e}\n")
print("Done querying shinsu 34-12")
