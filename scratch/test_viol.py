import urllib.request, json
url_info = 'http://apis.data.go.kr/1613000/BldRgstHubService/getBrExposInfo'
query = '?serviceKey=88ec4e85897c086c4c9438db67c35f2bc10d730913b9ba6be67a9ea755e70770&sigunguCd=11440&bjdongCd=12500&platGbCd=0&bun=0145&ji=0003&numOfRows=100&pageNo=1&_type=json'
req = urllib.request.Request(url_info + query)
req.add_header('User-Agent', 'Mozilla/5.0')
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

res = urllib.request.urlopen(req)
body = res.read()
if not body:
    print("API returned empty body. Government server might be down.")
    sys.exit(0)

try:
    data = json.loads(body.decode('utf-8'))
except json.JSONDecodeError:
    print(f"Failed to parse JSON. Government server returned invalid/500 response: {body}")
    sys.exit(0)

items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
if not items:
    print("No items returned from building register API.")
    sys.exit(0)

if isinstance(items, dict): items = [items]
for i in items:
    print(f"Ho: {i.get('hoNm')}, Viol: {i.get('violBldYn')}")
