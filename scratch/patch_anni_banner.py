import os

files_index = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]

def patch_index(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_code = """            // 통합 일정 렌더링
            const todayTaskBoard = document.getElementById('todayTaskBoard');
            if (todayTaskBoard) todayTaskBoard.innerHTML = '';
            
            let todayTaskSchedule = null;
            allDeals = allDeals.filter(s => {
                const todayStr = new Date().toLocaleDateString('en-CA');
                if (s.schedule_type === '모임' && s.memo && s.memo.startsWith('오늘의 업무\\n[PRIVATE]') && s.schedule_date === todayStr && !s.is_delayed) {
                    todayTaskSchedule = s;
                    return false;
                }
                return true;
            });

            if (todayTaskSchedule && todayTaskBoard) {
                const li = createDealListItem(todayTaskSchedule, true);
                todayTaskBoard.innerHTML = '<ul style="list-style: none; padding: 0; margin: 0;"></ul>';
                todayTaskBoard.querySelector('ul').appendChild(li);
            }"""
            
    new_code = """            // 통합 일정 렌더링
            const todayTaskBoard = document.getElementById('todayTaskBoard');
            if (todayTaskBoard) todayTaskBoard.innerHTML = '';
            
            let todayTaskSchedule = null;
            let todayAnniversaries = [];
            const todayStr = new Date().toLocaleDateString('en-CA');
            
            allDeals = allDeals.filter(s => {
                if (s.schedule_type === '모임' && s.memo && s.memo.startsWith('오늘의 업무\\n[PRIVATE]') && s.schedule_date === todayStr && !s.is_delayed) {
                    todayTaskSchedule = s;
                    return false;
                }
                
                // Extract today's anniversaries
                if (s.schedule_date === todayStr && s.memo && s.memo.includes('[ANNIVERSARY]')) {
                    let raw = s.memo.replace(/\\[.*?\\]/g, '').trim();
                    const name = raw.split('\\n')[0] || '기념일';
                    todayAnniversaries.push(name);
                }
                return true;
            });

            if ((todayTaskSchedule || todayAnniversaries.length > 0) && todayTaskBoard) {
                let html = '';
                if (todayAnniversaries.length > 0) {
                    const anniText = todayAnniversaries.map(a => `🎉 오늘은 ${a}입니다!`).join(' / ');
                    html += `<div style="background: #fef3c7; border: 1px solid #fde68a; color: #d97706; padding: 12px; border-radius: 12px; margin-bottom: 12px; font-weight: 800; font-size: 15px; text-align: center; box-shadow: 0 2px 8px rgba(217, 119, 6, 0.1); display: flex; align-items: center; justify-content: center; gap: 8px;"><span>${anniText}</span></div>`;
                }
                
                html += '<ul style="list-style: none; padding: 0; margin: 0;"></ul>';
                todayTaskBoard.innerHTML = html;
                
                if (todayTaskSchedule) {
                    const li = createDealListItem(todayTaskSchedule, true);
                    todayTaskBoard.querySelector('ul').appendChild(li);
                }
            }"""

    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")
    else:
        print(f"Could not find old code in {filepath}")

for fp in files_index:
    patch_index(fp)
