import os

files_index = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]

files_detail = [
    r'd:\부동산업무\antigravity\consult_diary\deal-detail.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\deal-detail.html'
]

def patch_index(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_code = """                let toggleDoneBtnHtml = '';
                if (isMine || (window.currentUser && window.currentUser.role === 'admin')) {"""
    new_code = """                let toggleDoneBtnHtml = '';
                const isAnniversary = schedule.memo && schedule.memo.includes('[ANNIVERSARY]');
                if (!isAnniversary && (isMine || (window.currentUser && window.currentUser.role === 'admin'))) {"""

    if old_code in content:
        content = content.replace(old_code, new_code)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")

def patch_detail(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the btnComplete logic and hide it if anniversary
    old_btn_logic = """            const btnComplete = document.getElementById('btnComplete');
            if (isDone) {"""
    new_btn_logic = """            const isAnniversary = data.memo && data.memo.includes('[ANNIVERSARY]');
            const btnComplete = document.getElementById('btnComplete');
            if (isAnniversary) {
                btnComplete.style.display = 'none';
            } else if (isDone) {"""

    if old_btn_logic in content:
        content = content.replace(old_btn_logic, new_btn_logic)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filepath}")

for fp in files_index:
    patch_index(fp)

for fp in files_detail:
    patch_detail(fp)
