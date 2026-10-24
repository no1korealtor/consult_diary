import urllib.request
import json

sigungu = '11440'

# check last 12 months for '현대'
for m in range(1, 13):
    month = f"2023{m:02d}"
    url = f'http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade?serviceKey=F8v9%2BB70Y%2B8dmsw19h%2BQx2L4r%2B9c%2B34U%2Fn1e%2Bf2xUifqL741mH%2FIH5O0K4C5nE8%2BS8W%2FYzE2yE78Yc%2B3FfBqBw%3D%3D&LAWD_CD={sigungu}&DEAL_YMD={month}&numOfRows=1000&_type=json'
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict): items = [items]
            for item in items:
                umd = item.get('umdNm') or item.get('dong')
                if umd and '중동' in umd:
                    apt_name = item.get('aptNm') or item.get('mhouseNm')
                    if apt_name == '현대':
                        print(f"아파트명: {apt_name}, 법정동: {umd}, 지번: {item.get('jibun')}")
                        exit()
    except Exception as e:
        print(e)
