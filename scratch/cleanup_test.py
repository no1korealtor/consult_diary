import urllib.request
import json

url = 'https://clzrbyplzjdrrscctcsl.supabase.co/rest/v1/study_words?subject=eq.YOUTUBE_LINK'
headers = {
    'apikey': 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k',
    'Authorization': 'Bearer sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(url, headers=headers, method='GET')
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        print("Current YouTube Links:")
        for item in data:
            print(f"ID: {item['id']}, Title: {item['word']}, URL: {item['meaning']}")
            
            # Delete if it's a test channel
            if "test" in item['word'].lower() or "<script>" in item['word'].lower() or "channel" in item['word'].lower():
                delete_url = f"https://clzrbyplzjdrrscctcsl.supabase.co/rest/v1/study_words?id=eq.{item['id']}"
                del_req = urllib.request.Request(delete_url, headers=headers, method='DELETE')
                with urllib.request.urlopen(del_req) as del_res:
                    print(f"Deleted test link: {item['word']}")
except Exception as e:
    print(f"Error: {e}")
