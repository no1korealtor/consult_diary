# -*- coding: utf-8 -*-
import requests

KAKAO_API_KEY = "133155e52871811db4337080ae0a2d13"
url = "https://dapi.kakao.com/v2/local/search/address.json"
headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}

q = u"성산동 200-94"
res = requests.get(url, headers=headers, params={"query": q.encode('utf-8')})
data = res.json()
total = data.get("meta", {}).get("total_count", 0)
print(f"Query: {q} -> total_count: {total}")
if total > 0:
    doc = data["documents"][0]
    addr = doc.get("address", {})
    print(f"Resolved Address: {doc.get('address_name')}")
    print(f"sigunguCd: {addr.get('b_code')[:5]}")
    print(f"bjdongCd: {addr.get('b_code')[5:10]}")
    print(f"bun: {addr.get('main_address_no')}")
    print(f"ji: {addr.get('sub_address_no')}")
    print(f"bjdongNm: {addr.get('region_3depth_name')}")
