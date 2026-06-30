import os
import re

files = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]

def patch_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix "지연됨" (Delayed)
    old_delayed = """                if (schedule.is_delayed) {
                    const origD = new Date(schedule.original_schedule_date);"""
    new_delayed = """                const isAnniversaryBadge = schedule.memo && schedule.memo.includes('[ANNIVERSARY]');
                if (schedule.is_delayed && !isAnniversaryBadge) {
                    const origD = new Date(schedule.original_schedule_date);"""
    
    if old_delayed in content:
        content = content.replace(old_delayed, new_delayed)

    # 2. Strip [ANNIVERSARY] from rawMemo
    old_rawmemo = """                    const rawLines = rawMemo.trim().split('\\n');
                    const meetName = rawLines[0] || '이름 없음';"""
    new_rawmemo = """                    let cleanRaw = rawMemo.replace(/\\[ANNIVERSARY\\]/g, '').trim();
                    const rawLines = cleanRaw.split('\\n');
                    const meetName = rawLines[0] || '이름 없음';
                    rawMemo = cleanRaw; // Update rawMemo for the rest of the code"""
    
    if old_rawmemo in content:
        content = content.replace(old_rawmemo, new_rawmemo)

    # 3. Change "개인 일정" to "개인 기념일"
    old_badge = """                    if (isPrivateMeeting) {
                        typeBadgeHtml = `<span style="display: inline-flex; align-items: center; gap: 4px; background: #f3f4f6; color: #4b5563; padding: 5px 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px solid #e5e7eb;">🔒 개인 일정</span>`;"""
    new_badge = """                    if (isPrivateMeeting) {
                        const badgeText = (schedule.memo && schedule.memo.includes('[ANNIVERSARY]')) ? '개인 기념일' : '개인 일정';
                        typeBadgeHtml = `<span style="display: inline-flex; align-items: center; gap: 4px; background: #f3f4f6; color: #4b5563; padding: 5px 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px solid #e5e7eb;">🔒 ${badgeText}</span>`;"""
    
    if old_badge in content:
        content = content.replace(old_badge, new_badge)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

for fp in files:
    patch_file(fp)
