import urllib.request
import json

url = 'https://clzrbyplzjdrrscctcsl.supabase.co/rest/v1/study_words'
headers = {
    'apikey': 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k',
    'Authorization': 'Bearer sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

data = [
    {
        'word': '전류 (A)',
        'meaning': '<div style=\"font-size:24px; color:#ff758c; font-weight:bold;\">전기가 흐르는 양</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">전선 속으로 전기가 일정하게 흐르면서 전기 에너지가 전달돼요.</div>',
        'example': '<div style=\"text-align:left; background:#eafbf0; padding:15px; border-radius:15px; border:2px solid #84fab0;\">💧 <b>물을 이용한 비유</b><br><br>🌊 물이 세게 많이 흐른다 = <b style=\"color:#ff758c\">전류가 크다</b><br>💧 물이 약하게 적게 흐른다 = <b style=\"color:#ff758c\">전류가 작다</b></div>',
        'subject': '과학',
        'category': '전기',
        'image_url': ''
    },
    {
        'word': '전압 (V)',
        'meaning': '<div style=\"font-size:24px; color:#ff758c; font-weight:bold;\">전기를 밀어주는 힘</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">전압이 클수록 전기를 더 세게 밀어주기 때문에 전류가 더 잘 흐르게 돼요.</div>',
        'example': '<div style=\"text-align:left; background:#fff0f5; padding:15px; border-radius:15px; border:2px solid #ff9a9e;\">💧 <b>물을 이용한 비유</b><br><br>🎢 높은 곳에서 물을 내리면 = <b style=\"color:#ff758c\">전압이 크다</b><br>🛝 낮은 곳에서 물을 내리면 = <b style=\"color:#ff758c\">전압이 작다</b></div>',
        'subject': '과학',
        'category': '전기',
        'image_url': ''
    },
    {
        'word': '저항 (Ω)',
        'meaning': '<div style=\"font-size:24px; color:#ff758c; font-weight:bold;\">전기의 흐름을 방해하는 정도</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">저항이 클수록 전기의 흐름이 어려워져 전류가 적게 흐르게 돼요.</div>',
        'example': '<div style=\"text-align:left; background:#f0f5ff; padding:15px; border-radius:15px; border:2px solid #a1c4fd;\">💧 <b>물을 이용한 비유</b><br><br>🕳️ 넓은 파이프 = <b style=\"color:#ff758c\">저항이 작다</b> (물이 잘 흐름)<br>🪡 좁은 파이프 = <b style=\"color:#ff758c\">저항이 크다</b> (물이 안 흐름)</div>',
        'subject': '과학',
        'category': '전기',
        'image_url': ''
    },
    {
        'word': '전기 핵심 정리 💡',
        'meaning': '<ul style=\"text-align:left; font-size:18px; line-height:1.8; color:#2d3436; background:#fff9e6; padding:20px 20px 20px 40px; border-radius:15px; border:2px solid #f6d365; margin:0;\"><li><b>전류 (A)</b> = 전기가 흐르는 양</li><li><b>전압 (V)</b> = 전기를 밀어주는 힘</li><li><b>저항 (Ω)</b> = 전기의 흐름을 방해하는 정도</li></ul>',
        'example': '<div style=\"text-align:center; font-size:16px; color:#6c5ce7; font-weight:bold;\">🌟 전압이 커지면 전류가 많이 흐르고,<br>저항이 커지면 전류가 적게 흐릅니다!</div>',
        'subject': '과학',
        'category': '전기',
        'image_url': ''
    },
    {
        'word': '개념 확인 문제 📝',
        'meaning': '<div style=\"font-size:22px; color:#2d3436; font-weight:bold; margin-bottom:15px;\">Q. 전류란 무엇을 의미하나요?</div>',
        'example': '<div style=\"text-align:left; font-size:16px; line-height:1.8; background:#f8f9fa; padding:20px; border-radius:15px; border:2px dashed #b2bec3;\">① 전기를 밀어주는 힘<br>② <b style=\"color:#00b894; font-size:18px;\">전기가 흐르는 양 (정답! 🎉)</b><br>③ 전기의 흐름을 방해하는 정도<br>④ 전기를 저장하는 양</div>',
        'subject': '과학',
        'category': '전기',
        'image_url': ''
    }
]

req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print("Success")
except Exception as e:
    print(f"Error: {e}")
