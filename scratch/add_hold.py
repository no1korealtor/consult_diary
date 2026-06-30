import re
import os

files_detail = [
    r'd:\부동산업무\antigravity\consult_diary\deal-detail.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\deal-detail.html'
]

files_index = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]

def patch_detail(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add button
    old_btn = """        <button type="button" id="btnComplete" class="btn-secondary" onclick="toggleComplete()" style="margin-bottom: 12px; border-radius: 14px; background-color: #dcfce7; border: 1px solid #bbf7d0; color: #16a34a; font-weight: 700;">
            ✅ 일정 완료
        </button>"""
    new_btn = """        <div style="display: flex; gap: 12px; margin-bottom: 12px;">
            <button type="button" id="btnComplete" class="btn-secondary" onclick="toggleComplete()" style="flex: 1; margin-bottom: 0; border-radius: 14px; background-color: #dcfce7; border: 1px solid #bbf7d0; color: #16a34a; font-weight: 700;">
                ✅ 일정 완료
            </button>
            <button type="button" id="btnHold" class="btn-secondary" onclick="toggleHold()" style="flex: 1; margin-bottom: 0; border-radius: 14px; background-color: #fef3c7; border: 1px solid #fde68a; color: #d97706; font-weight: 700;">
                ⏸️ 일정 보류
            </button>
        </div>"""
    if old_btn in content:
        content = content.replace(old_btn, new_btn)

    # 2. Add window.currentDealIsHold check
    old_isdone = """            let isDone = parsed.isDone;
            window.currentDealIsDone = isDone;"""
    new_isdone = """            let isDone = parsed.isDone;
            window.currentDealIsDone = isDone;
            
            let isHold = rawMemo.includes('[HOLD]');
            if (isHold) {
                rawMemo = rawMemo.replace(/\\[HOLD\\]\\n?/g, '');
            }
            window.currentDealIsHold = isHold;"""
    if old_isdone in content:
        content = content.replace(old_isdone, new_isdone)

    # 3. Add btnHold style logic
    old_btn_style = """            if (isDone) {
                btnComplete.innerHTML = '🔄 완료 취소';
                btnComplete.style.backgroundColor = '#f3f4f6';
                btnComplete.style.color = '#4b5563';
                btnComplete.style.borderColor = '#e5e7eb';
            } else {
                btnComplete.innerHTML = '✅ 일정 완료';
                btnComplete.style.backgroundColor = '#dcfce7';
                btnComplete.style.color = '#16a34a';
                btnComplete.style.borderColor = '#bbf7d0';
            }"""
    new_btn_style = old_btn_style + """
            const btnHold = document.getElementById('btnHold');
            if (btnHold) {
                if (isHold) {
                    btnHold.innerHTML = '▶️ 보류 해제';
                    btnHold.style.backgroundColor = '#f3f4f6';
                    btnHold.style.color = '#4b5563';
                    btnHold.style.borderColor = '#e5e7eb';
                } else {
                    btnHold.innerHTML = '⏸️ 일정 보류';
                    btnHold.style.backgroundColor = '#fef3c7';
                    btnHold.style.color = '#d97706';
                    btnHold.style.borderColor = '#fde68a';
                }
            }"""
    if old_btn_style in content:
        content = content.replace(old_btn_style, new_btn_style)

    # 4. Add toggleHold function
    old_toggle = "async function toggleComplete() {"
    new_toggle = """async function toggleHold() {
            const ok = confirm(window.currentDealIsHold ? '보류 상태를 해제하시겠습니까?' : '이 일정을 보류(후순위) 상태로 변경하시겠습니까?');
            if (!ok) return;

            const { data, error: fetchErr } = await supabaseClient.from('schedules').select('memo').eq('id', scheduleId).single();
            if (fetchErr) { alert(fetchErr.message); return; }

            let newMemo = data.memo || '';
            if (window.currentDealIsHold) {
                newMemo = newMemo.replace(/\\[HOLD\\]\\n?/g, '').trim();
            } else {
                newMemo = '[HOLD]\\n' + newMemo;
            }

            const { error } = await supabaseClient.from('schedules').update({ memo: newMemo }).eq('id', scheduleId);
            if (error) { alert(error.message); return; }

            alert(window.currentDealIsHold ? '보류가 해제되었습니다.' : '일정이 보류 상태로 변경되었습니다.');
            location.reload();
        }

        async function toggleComplete() {"""
    if old_toggle in content:
        content = content.replace(old_toggle, new_toggle)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

def patch_index(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Add isHold to sortByDate logic
    old_sort = """            const sortByDate = (a, b) => {
                const isNoticeA = isNotice(a);
                const isNoticeB = isNotice(b);
                
                if (isNoticeA && !isNoticeB) return -1;
                if (!isNoticeA && isNoticeB) return 1;"""
    new_sort = """            const sortByDate = (a, b) => {
                const isNoticeA = isNotice(a);
                const isNoticeB = isNotice(b);
                
                if (isNoticeA && !isNoticeB) return -1;
                if (!isNoticeA && isNoticeB) return 1;

                const isHoldA = (a.memo || '').includes('[HOLD]');
                const isHoldB = (b.memo || '').includes('[HOLD]');
                if (isHoldA && !isHoldB) return 1;
                if (!isHoldA && isHoldB) return -1;"""
    if old_sort in content:
        content = content.replace(old_sort, new_sort)

    # Add isHold to monthStr logic
    old_month = """                let monthStr = '미정';
                let dateStr = '-';
                let dayStr = '';

                if (schedule.schedule_date) {"""
    new_month = """                let monthStr = '미정';
                let dateStr = '-';
                let dayStr = '';

                if (schedule.memo && schedule.memo.includes('[HOLD]')) {
                    monthStr = '보류';
                } else if (schedule.schedule_date) {"""
    if old_month in content:
        content = content.replace(old_month, new_month)
        
    # Add styling for '보류' group
    old_color = """                let dateBoxBg = monthStr === '미정' ? '#fee2e2' : '#f8fafc';
                let dateBoxBorder = monthStr === '미정' ? '#fca5a5' : '#e2e8f0';
                let dateTextColor = monthStr === '미정' ? '#ef4444' : '#1e293b';"""
    new_color = """                let dateBoxBg = monthStr === '미정' ? '#fee2e2' : (monthStr === '보류' ? '#fef3c7' : '#f8fafc');
                let dateBoxBorder = monthStr === '미정' ? '#fca5a5' : (monthStr === '보류' ? '#fde68a' : '#e2e8f0');
                let dateTextColor = monthStr === '미정' ? '#ef4444' : (monthStr === '보류' ? '#d97706' : '#1e293b');"""
    if old_color in content:
        content = content.replace(old_color, new_color)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

for fp in files_detail:
    patch_detail(fp)

for fp in files_index:
    patch_index(fp)
