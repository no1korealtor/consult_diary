import urllib.request
import urllib.parse
import json

DB_URL = 'https://clzrbyplzjdrrscctcsl.supabase.co'
DB_KEY = 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k'

headers = {
    'apikey': DB_KEY,
    'Authorization': f'Bearer {DB_KEY}',
    'Content-Type': 'application/json'
}

def get(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

query1 = urllib.parse.quote('ilike.*조항준*')
users = get(f'{DB_URL}/rest/v1/users?name={query1}&select=*')
print("Users:", len(users))

if users:
    myId = users[0]['id']
    query2 = urllib.parse.quote('like.오늘의 업무%')
    schedules = get(f'{DB_URL}/rest/v1/schedules?user_id=eq.{myId}&memo={query2}&select=id,schedule_date,created_at&order=created_at.desc&limit=10')
    print("Schedules found:", len(schedules))
    for s in schedules:
        print(s['id'], s['schedule_date'], s['created_at'])
        tasks = get(f"{DB_URL}/rest/v1/schedule_tasks?schedule_id=eq.{s['id']}&select=*")
        print("  Tasks:", json.dumps(tasks, ensure_ascii=False))
