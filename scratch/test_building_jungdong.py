import urllib.request

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"
title_url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
title_query = f"?serviceKey={GOV_API_KEY}&sigunguCd=11440&bjdongCd=12600&platGbCd=0&bun=0395&ji=0000&numOfRows=10&pageNo=1&_type=json"

req = urllib.request.Request(title_url + title_query)
req.add_header("User-Agent", "Mozilla/5.0")

try:
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
