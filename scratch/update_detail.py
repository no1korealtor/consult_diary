import re
import os

files_to_update = [
    r'd:\부동산업무\antigravity\consult_diary\deal-detail.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\deal-detail.html'
]

def update_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # deal-detail.html replaces
    content = content.replace("let meetTitle = '모임(기념일)';", "let meetTitle = data.memo && data.memo.includes('[ANNIVERSARY]') ? '기념일' : '모임';")
    content = content.replace("else if (isCanceled) meetTitle = '❌ 취소된 모임(기념일)';", "else if (isCanceled) meetTitle = '❌ 취소된 ' + meetTitle;")
    content = content.replace("else meetTitle = '✅ 확정 모임(기념일)';", "else meetTitle = '✅ 확정 ' + meetTitle;")
    content = content.replace("const meetName = rawLines[0] || '모임(기념일)';", "const meetName = rawLines[0] || (data.memo && data.memo.includes('[ANNIVERSARY]') ? '기념일' : '모임');")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

for fp in files_to_update:
    update_file(fp)
