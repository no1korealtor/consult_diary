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
        'word': '물질의 상태 🧊💧☁️',
        'meaning': '<div style=\"font-size:24px; color:#6c5ce7; font-weight:bold;\">물질은 3가지 상태로 존재해요!</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">고체, 액체, 기체로 나뉘며, 이 세 가지 상태는 모양과 부피가 서로 달라요.</div>',
        'example': '<div style=\"display:flex; justify-content:space-around; background:#f0f5ff; padding:15px; border-radius:15px; border:2px solid #a1c4fd; text-align:center;\"><div><span style=\"font-size:30px;\">🧊</span><br><b style=\"color:#0984e3;\">고체</b></div><div><span style=\"font-size:30px;\">💧</span><br><b style=\"color:#00b894;\">액체</b></div><div><span style=\"font-size:30px;\">☁️</span><br><b style=\"color:#fdcb6e;\">기체</b></div></div>',
        'subject': '과학',
        'category': '물질의 상태',
        'image_url': ''
    },
    {
        'word': '고체 (Solid) 🧊',
        'meaning': '<div style=\"font-size:24px; color:#0984e3; font-weight:bold;\">모양이 일정하고 부피도 일정한 물질</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">예) 얼음, 돌, 책, 철 등</div>',
        'example': '<div style=\"text-align:left; background:#eafbf0; padding:15px; border-radius:15px; border:2px solid #84fab0;\">📌 <b>핵심 정리</b><br>고체 ➡️ 모양 ⭕, 부피 ⭕<br><br>📝 <b>확인 문제</b><br>다음 중 고체를 모두 고르세요.<br>① 얼음 ② 물 ③ 돌 ④ 수증기<br><br><span style=\"color:#00b894; font-weight:bold;\">정답: ① 얼음, ③ 돌</span></div>',
        'subject': '과학',
        'category': '물질의 상태',
        'image_url': ''
    },
    {
        'word': '액체 (Liquid) 💧',
        'meaning': '<div style=\"font-size:24px; color:#00b894; font-weight:bold;\">모양은 변하지만 부피는 일정한 물질</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">예) 물, 우유, 주스 등 (담는 그릇에 따라 모양이 변해요!)</div>',
        'example': '<div style=\"text-align:left; background:#fff0f5; padding:15px; border-radius:15px; border:2px solid #ff9a9e;\">📌 <b>핵심 정리</b><br>액체 ➡️ 모양 ❌, 부피 ⭕<br><br>📝 <b>확인 문제</b><br>컵의 물을 병에 옮기면 어떻게 될까요?<br>① 모양이 변한다 ② 부피가 변한다<br><br><span style=\"color:#ff758c; font-weight:bold;\">정답: ① 모양이 변한다</span></div>',
        'subject': '과학',
        'category': '물질의 상태',
        'image_url': ''
    },
    {
        'word': '기체 (Gas) ☁️',
        'meaning': '<div style=\"font-size:24px; color:#fdcb6e; font-weight:bold;\">모양도 변하고 부피도 변하는 물질</div><div style=\"font-size:16px; margin-top:10px; color:#636e72;\">예) 공기, 수증기, 풍선 속 공기 등 (공간을 가득 채워요!)</div>',
        'example': '<div style=\"text-align:left; background:#fff9e6; padding:15px; border-radius:15px; border:2px solid #ffeaa7;\">📌 <b>핵심 정리</b><br>기체 ➡️ 모양 ❌, 부피 ❌<br><br>📝 <b>확인 문제</b><br>풍선을 크게 불면 변하는 것은?<br>① 모양 ② 부피 ③ 둘 다<br><br><span style=\"color:#e17055; font-weight:bold;\">정답: ③ 둘 다</span></div>',
        'subject': '과학',
        'category': '물질의 상태',
        'image_url': ''
    },
    {
        'word': '상태변화 용어 🔄',
        'meaning': '<div style=\"font-size:22px; color:#d63031; font-weight:bold;\">물질은 상태가 변할 때 특별한 이름이 있어요!</div>',
        'example': '<ul style=\"text-align:left; font-size:16px; line-height:1.8; background:#f8f9fa; padding:20px 20px 20px 40px; border-radius:15px; border:2px dashed #b2bec3; margin:0;\"><li>🧊 얼음 ➡️ 💧 물 : <b style=\"color:#d63031;\">융해 (녹는다)</b></li><li>💧 물 ➡️ ☁️ 수증기 : <b style=\"color:#e17055;\">기화 (끓는다/증발한다)</b></li><li>☁️ 수증기 ➡️ 💧 물 : <b style=\"color:#0984e3;\">액화 (물방울이 된다)</b></li><li>💧 물 ➡️ 🧊 얼음 : <b style=\"color:#6c5ce7;\">응고 (언다)</b></li></ul>',
        'subject': '과학',
        'category': '상태변화',
        'image_url': ''
    },
    {
        'word': '마무리 퀴즈 🎯',
        'meaning': '<div style=\"font-size:20px; color:#2d3436; font-weight:bold; margin-bottom:15px;\">배운 내용을 확인해 볼까요?</div>',
        'example': '<div style=\"text-align:left; font-size:15px; line-height:1.8; background:#e8f4f8; padding:15px; border-radius:15px; border:2px solid #74b9ff;\">① 얼음이 녹아 물이 되는 현상은?<br>👉 <b style=\"color:#d63031;\">융해</b><br><br>② 수증기가 물방울이 되는 현상은?<br>👉 <b style=\"color:#0984e3;\">액화</b><br><br>③ 고체는 모양이 (<b>일정</b>)하고 부피가 (<b>일정</b>)하다.<br>④ 액체는 모양이 (<b>변함</b>)하지만 부피는 (<b>일정</b>)하다.<br>⑤ 기체는 모양도 (<b>변함</b>)하고 부피도 (<b>변함</b>)한다.</div>',
        'subject': '과학',
        'category': '상태변화',
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
