import urllib.request, urllib.parse, json, os
from trade_viewer import GOV_API_KEY, get_kakao_address_info

addr = '경기 부천시 중동 393'
info = get_kakao_address_info(addr)
print('Kakao info:', info)
if info:
    bun_str = str(info['bun']).zfill(4) if info.get('bun') else '0000'
    ji_str = str(info['ji']).zfill(4) if info.get('ji') else '0000'
    url = 'https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo'
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd={info['sigunguCd']}&bjdongCd={info['bjdongCd']}&platGbCd=0&bun={bun_str}&ji={ji_str}&numOfRows=100&pageNo=1&_type=json"
    req = urllib.request.Request(url + query)
    try:
        with urllib.request.urlopen(req) as response:
            res = response.read().decode('utf-8')
            print('API response length:', len(res))
            data = json.loads(res)
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict): items = [items]
            for it in items:
                print('bldNm:', it.get('bldNm'), 'mainPurps:', it.get('mainPurpsCdNm'), 'hhldCnt:', it.get('hhldCnt'))
    except Exception as e:
        print('Error:', e)
