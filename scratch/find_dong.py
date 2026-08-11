# -*- coding: utf-8 -*-
import requests
import json

url = 'https://dapi.kakao.com/v2/local/search/address.json'
headers = {'Authorization': 'KakaoAK 133155e52871811db4337080ae0a2d13'}
dongs = ['아현동', '공덕동', '신공덕동', '도화동', '용강동', '토정동', '마포동', '대흥동', '염리동', '노고산동', '신수동', '현석동', '구수동', '창전동', '상수동', '하중동', '신정동', '당인동', '서교동', '동교동', '합정동', '망원동', '연남동', '성산동', '중동', '상암동']

with open("find_dong_result.txt", "w", encoding="utf-8") as f_out:
    for d in dongs:
        q = f'마포구 {d} 34-15'
        res = requests.get(url, headers=headers, params={'query': q})
        data = res.json()
        if data.get('meta', {}).get('total_count', 0) > 0:
            addr = data['documents'][0]['address_name']
            f_out.write(f"Match: {d} -> {addr}\n")
            print("Found match in data")
