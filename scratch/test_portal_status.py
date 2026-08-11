import urllib.request
import json
import time

GOV_API_KEY = "S%2B2v1m048n2W8YtZ%2FsT1zJ4R3z627uQ3a36K2uC4bO5G4m8Ue3a2oP9wD%2F7vK2e8%2BbO%2Bx1n8k4%2F3t8g%2Bx1a2w%3D%3D"

# Read actual key from trade_viewer.py if available
try:
    with open("trade_viewer.py", "r", encoding="utf-8") as f:
        for line in f:
            if "GOV_API_KEY =" in line:
                GOV_API_KEY = line.split("=")[1].strip().strip('"').strip("'")
                break
except Exception as e:
    print("Could not load key from trade_viewer.py, using default. Error:", e)

print("Using key:", GOV_API_KEY[:20] + "...")

# We will test two things:
# 1. TCP connection / HTTP request to apis.data.go.kr (ping/head)
# 2. Actual API call with 5 seconds timeout

urls = {
    "SHTrade (단독/다가구 매매)": f"https://apis.data.go.kr/1613000/RTMSDataSvcSHTrade/getRTMSDataSvcSHTrade?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202405&numOfRows=1&pageNo=1&_type=json",
    "SHRent (단독/다가구 전월세)": f"https://apis.data.go.kr/1613000/RTMSDataSvcSHRent/getRTMSDataSvcSHRent?serviceKey={GOV_API_KEY}&LAWD_CD=11440&DEAL_YMD=202405&numOfRows=1&pageNo=1&_type=json",
    "Public Data Portal Main Page (data.go.kr)": "https://www.data.go.kr"
}

for name, url in urls.items():
    print(f"\nTesting {name}...")
    start_time = time.time()
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            elapsed = time.time() - start_time
            print(f"  Result: Success! Status Code: {status}, Time taken: {elapsed:.2f}s")
            # Try to read a bit of data
            data = response.read(500)
            print(f"  Data snippet: {data[:100]}...")
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start_time
        print(f"  Result: HTTP Error {e.code}: {e.reason} (Time: {elapsed:.2f}s)")
    except urllib.error.URLError as e:
        elapsed = time.time() - start_time
        print(f"  Result: Network/URL Error: {e.reason} (Time: {elapsed:.2f}s)")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  Result: Unexpected Error: {e} (Time: {elapsed:.2f}s)")
