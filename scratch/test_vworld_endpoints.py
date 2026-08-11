import urllib.request
import json

vworld_key = "80194C85-0EE3-3220-A3C1-3268AD8756B9"
pnu = "1144012500102000094"  # 성산동 200-94

url = f"http://api.vworld.kr/ned/data/getLandUseAttr?key={vworld_key}&domain=http://localhost&pnu={pnu}&format=json&numOfRows=20&pageNo=1"
req = urllib.request.Request(url)
req.add_header("Referer", "http://localhost")

try:
    with urllib.request.urlopen(req) as resp:
        raw_bytes = resp.read()
        
        # Test 1: Decode as UTF-8 and save
        try:
            text = raw_bytes.decode('utf-8')
            data = json.loads(text)
            with open('scratch/res_utf8.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Saved res_utf8.json")
        except Exception as e:
            print("UTF-8 save error:", e)
            
        # Test 2: Decode as CP949 and save
        try:
            text = raw_bytes.decode('cp949', errors='replace')
            data = json.loads(text)
            with open('scratch/res_cp949.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Saved res_cp949.json")
        except Exception as e:
            print("CP949 save error:", e)
            
except Exception as e:
    print("Request error:", e)
