import requests
import json
import re

with open("auth-helper.js", "r", encoding="utf-8") as f:
    content = f.read()

url_match = re.search(r"AUTH_URL\s*=\s*['\"]([^'\"]+)['\"]", content)
key_match = re.search(r"AUTH_KEY\s*=\s*['\"]([^'\"]+)['\"]", content)

if url_match and key_match:
    url = url_match.group(1)
    key = key_match.group(1)
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
    
    res = requests.get(f"{url}/rest/v1/users?select=*&limit=1", headers=headers)
    print("STATUS:", res.status_code)
    try:
        data = res.json()
        if data:
            print("Columns:", list(data[0].keys()))
            print("Sample record:", data[0])
        else:
            print("No users found.")
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Raw response:", res.text)
else:
    print("Could not find AUTH_URL or AUTH_KEY in auth-helper.js")
