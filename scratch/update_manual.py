import os

files_to_update = [
    r'd:\부동산업무\antigravity\consult_diary\manual.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\manual.html'
]

def update_file(filepath):
    if not os.path.exists(filepath):
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # manual.html replaces
    content = content.replace(
        '<span style="color:#8b5cf6;font-weight:bold;">👥 모임(기념일)</span>',
        '<span style="color:#8b5cf6;font-weight:bold;">👥 모임</span>과 <span style="color:#f59e0b;font-weight:bold;">🎉 기념일</span>'
    )
    content = content.replace(
        '<h3>👥 모임(기념일) (개인 약속, 기념일 및 회식)</h3>',
        '<h3>👥 모임 / 🎉 기념일 (개인 약속, 생일, 회식 등)</h3>'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

for fp in files_to_update:
    update_file(fp)
