import os
import re

files_detail = [
    r'd:\부동산업무\antigravity\consult_diary\deal-detail.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\deal-detail.html'
]

def patch_detail(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add ID to kakao map button
    old_kakao = '<button type="button" class="btn-kakao" onclick="openKakaoMap()"'
    new_kakao = '<button type="button" id="btnKakao" class="btn-kakao" onclick="openKakaoMap()"'
    if old_kakao in content and 'id="btnKakao"' not in content:
        content = content.replace(old_kakao, new_kakao)

    # 2. Strip [ANNIVERSARY] from rawMemo
    old_rawmemo = """            const parsed = parseScheduleMemo(data.memo, data.schedule_time, currentUserId);
            let rawMemo = parsed.cleanMemo;"""
    new_rawmemo = """            const parsed = parseScheduleMemo(data.memo, data.schedule_time, currentUserId);
            let rawMemo = parsed.cleanMemo;
            
            let isAnniversary = rawMemo.includes('[ANNIVERSARY]') || (data.memo && data.memo.includes('[ANNIVERSARY]'));
            if (isAnniversary) {
                rawMemo = rawMemo.replace(/\\[ANNIVERSARY\\]\\n?/g, '').replace(/\\[ANNIVERSARY\\]/g, '').trim();
            }"""
    if old_rawmemo in content:
        content = content.replace(old_rawmemo, new_rawmemo)
        
    # 3. Change title '개인 일정' to '개인 기념일' if it's an anniversary
    old_title = "if (isPrivateMeeting) meetTitle = '개인 일정';"
    new_title = "if (isPrivateMeeting) meetTitle = isAnniversary ? '개인 기념일' : '개인 일정';"
    if old_title in content:
        content = content.replace(old_title, new_title)

    # 4. Hide Hold button and Kakao map button for anniversaries
    old_btn_hide = """            const isAnniversary = data.memo && data.memo.includes('[ANNIVERSARY]');
            const btnComplete = document.getElementById('btnComplete');
            if (isAnniversary) {
                btnComplete.style.display = 'none';
            } else if (isDone) {"""
    
    new_btn_hide = """            const isAnniCheck = data.memo && data.memo.includes('[ANNIVERSARY]');
            const btnComplete = document.getElementById('btnComplete');
            const btnHold = document.getElementById('btnHold');
            const btnKakao = document.getElementById('btnKakao');
            if (isAnniCheck) {
                if (btnComplete) btnComplete.style.display = 'none';
                if (btnHold) btnHold.style.display = 'none';
                if (btnKakao) btnKakao.style.display = 'none';
                
                // Hide the flex container for Complete/Hold buttons if both are hidden
                if (btnComplete) {
                    const actionRow = btnComplete.parentElement;
                    if (actionRow && actionRow.style.display !== 'none') {
                        actionRow.style.display = 'none';
                    }
                }
            } else if (isDone) {"""
            
    if old_btn_hide in content:
        content = content.replace(old_btn_hide, new_btn_hide)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

for fp in files_detail:
    patch_detail(fp)
