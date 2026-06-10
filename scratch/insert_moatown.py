import urllib.request
import json
import re

html_path = r'd:\부동산업무\antigravity\consult_diary\moatown.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

start_tag = '<div class="blog-content" id="exportContent">'
end_tag = '<div class="public-footer">'

start_idx = html.find(start_tag)
end_idx = html.find(end_tag)

if start_idx != -1 and end_idx != -1:
    content = html[start_idx + len(start_tag):end_idx]
    
    # Remove tags using regex
    content = re.sub(r'<div id="scrapTag">.*?</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<h1>.*?</h1>', '', content, flags=re.DOTALL)
    content = re.sub(r'<h2 class="subtitle">.*?</h2>', '', content, flags=re.DOTALL)
    content = re.sub(r'<hr>', '', content)
    
    content = content.strip()
    
    data = {
        "title": "모아타운, 도대체 무엇이 궁금한가?",
        "category": "기타",
        "summary": json.dumps(["모아타운과 모아주택의 차이", "가로주택정비사업과의 비교", "권리산정기준일과 분양권 요건", "현금청산 기준"], ensure_ascii=False),
        "full_text": content,
        "is_active": True
    }
    
    url = "https://clzrbyplzjdrrscctcsl.supabase.co/rest/v1/practical_tips"
    headers = {
        "apikey": "sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k",
        "Authorization": "Bearer sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode('utf-8')
            print("Inserted successfully:", res_data)
    except Exception as e:
        print("Error inserting:", e)
else:
    print("Could not extract content")
