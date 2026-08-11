import urllib.request
import json

vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
pnu = "1144012500102000094"  # 성산동 200-94 (단독/다세대 유형 확인 가능)

def test_endpoint(api_name, pnu_val):
    url = f"http://api.vworld.kr/ned/data/{api_name}?key={vworld_key}&domain=http://localhost&pnu={pnu_val}&format=json&numOfRows=10&pageNo=1"
    req = urllib.request.Request(url)
    req.add_header("Referer", "http://localhost")
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode('utf-8')
            data = json.loads(text)
            print(f"\n=== {api_name} ===")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    except Exception as e:
        print(f"\n=== {api_name} ERROR ===")
        print(e)

if __name__ == "__main__":
    # Test Land Characteristics (includes 공시지가)
    test_endpoint("getLandCharacteristics", pnu)
    
    # Test Individual Housing Price (개별주택가격)
    test_endpoint("getIndvdHousingPriceAttr", pnu)
    
    # Test Apartment Housing Price (공동주택가격 - 아파트용 PNU 필요할 수도 있음)
    # 성산시영아파트 101동 PNU: 1144012500101450001
    test_endpoint("getApartHousingPriceAttr", "1144012500101450001")
