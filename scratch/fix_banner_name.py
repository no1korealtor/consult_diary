import os

files_index = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]

def patch_index(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_code = """                // Extract today's anniversaries
                if (s.schedule_date === todayStr && s.memo && s.memo.includes('[ANNIVERSARY]')) {
                    let raw = s.memo.replace(/\\[.*?\\]/g, '').trim();
                    const name = raw.split('\\n')[0] || '기념일';
                    todayAnniversaries.push(name);
                }"""
                
    new_code = """                // Extract today's anniversaries
                if (s.schedule_date === todayStr && s.memo && s.memo.includes('[ANNIVERSARY]')) {
                    const parsed = typeof parseScheduleMemo === 'function' ? parseScheduleMemo(s.memo, s.schedule_time, window.currentUser?.id) : { cleanMemo: s.memo };
                    let raw = parsed.cleanMemo.replace(/\\[ANNIVERSARY\\]/g, '').replace(/\\[.*?\\]/g, '').trim();
                    
                    // Filter out empty lines
                    const lines = raw.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
                    const name = lines[0] || '기념일';
                    todayAnniversaries.push(name);
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
