import urllib.request
import urllib.parse
import json

from get_building_info import API_KEY

sigunguCd = "11440"
bjdongCd = "12500"
bun = "0200"
ji = "0109"

url_floor = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrFlrOulnInfo"
query = f"?serviceKey={API_KEY}&sigunguCd={sigunguCd}&bjdongCd={bjdongCd}&platGbCd=0&bun={bun}&ji={ji}&numOfRows=100&pageNo=1&_type=json"

req = urllib.request.Request(url_floor + query)
req.add_header('User-Agent', 'Mozilla/5.0')
res = urllib.request.urlopen(req)
res_body = res.read().decode('utf-8')
data = json.loads(res_body)
print(json.dumps(data, indent=2, ensure_ascii=False))
