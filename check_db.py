import requests
import json
import re

with open("auth-helper.js", "r", encoding="utf-8") as f:
    content = f.read()

url_match = re.search(r"SUPABASE_URL\s*=\s*['\"]([^'\"]+)['\"]", content)
key_match = re.search(r"SUPABASE_ANON_KEY\s*=\s*['\"]([^'\"]+)['\"]", content)

if url_match and key_match:
    url = url_match.group(1)
    key = key_match.group(1)
    
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}"
    }
    
    res = requests.get(f"{url}/rest/v1/user_tip_status?limit=1", headers=headers)
    print(res.status_code)
    print(res.json())