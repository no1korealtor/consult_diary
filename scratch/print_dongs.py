import urllib.request
import json

GOV_API_KEY = "88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770"

def inspect_titles():
    url = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
    # Query up to 100 rows to see everything
    query = f"?serviceKey={GOV_API_KEY}&sigunguCd=11440&bjdongCd=12600&platGbCd=0&bun=0395&ji=0000&numOfRows=100&pageNo=1&_type=json"
    
    req = urllib.request.Request(url + query)
    req.add_header("User-Agent", "Mozilla/5.0")
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode('utf-8')
            print("Raw response:")
            print(text[:1000])
            data = json.loads(text)
            items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if isinstance(items, dict):
                items = [items]
            
            print(f"Total titles found: {len(items)}")
            for idx, item in enumerate(items):
                print(f"[{idx}] bldNm: {item.get('bldNm')}, dongNm: {item.get('dongNm')}, grndFlrCnt: {item.get('grndFlrCnt')}, mainPurpsCdNm: {item.get('mainPurpsCdNm')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    inspect_titles()
