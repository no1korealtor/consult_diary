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
    
    res = requests.get(f"{url}/rest/v1/users?id=eq.1039d621-af0f-4a8b-8e6e-76c3f83e2a0f", headers=headers)
    print("STATUS:", res.status_code)
    try:
        data = res.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(res.text)
