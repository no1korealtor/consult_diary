import urllib.request, json
GOV_API_KEY='88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770'
url = f'https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo?serviceKey={GOV_API_KEY}&sigunguCd=11440&bjdongCd=12600&platGbCd=0&bun=0393&ji=0000&numOfRows=10&pageNo=1&_type=json'
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    items = data['response']['body']['items']['item']
    if type(items) != list: items = [items]
    for item in items:
        print(f"bldNm: {item.get('bldNm')}, hhldCnt: {item.get('hhldCnt')}, mainPurpsCdNm: {item.get('mainPurpsCdNm')}, etcPurps: {item.get('etcPurps')}")
