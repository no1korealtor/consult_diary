import os

files_index = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]
manual_file = r'd:\부동산업무\antigravity\consult_diary\manual.html'

def patch_index(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_notice = """<span style="color: #3b82f6; margin-right: 4px;">[6/17 개선]</span> 이전 날짜의 미완료 일정이 오늘 일정으로 자동 이관되어 표시되도록 개선"""
    new_notice = """<span style="color: #3b82f6; margin-right: 4px;">[6/30 개선]</span> 기념일 전용 UI가 분리되었으며, 후순위 업무 관리를 위한 '일정 보류' 기능이 추가되었습니다."""
    
    if old_notice in content:
        content = content.replace(old_notice, new_notice)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched notice in {filepath}")

def patch_manual(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_tip_1 = "<li><span class=\"highlight\">NEW</span> <strong>오늘의 실무 팁 배너</strong>:"
    new_tip_1 = """<li><span class="highlight">NEW</span> <strong>일정 보류 기능</strong>: 당장 취소할 수는 없지만 한동안 미뤄둬야 하는 일(예: 나중에 할 하자보수 등)은 일정 상세화면에서 '⏸️ 일정 보류'를 누르세요. 메인 화면 맨 아래쪽 '보류된 일정' 영역으로 묶여서 눈에 덜 띄게 깔끔하게 관리됩니다.</li>\n                <li><span class="highlight">NEW</span> <strong>오늘의 실무 팁 배너</strong>:"""
    if old_tip_1 in content:
        content = content.replace(old_tip_1, new_tip_1)
        
    old_tip_2 = """<li><strong>💡 모임 제안</strong>: 사무실 식구들에게 모임을 제안하고 <strong>참석/불참 투표</strong>를 받을 수 있습니다."""
    new_tip_2 = """<li><span class="highlight">NEW</span> <strong>🎉 기념일</strong>: 매년 반복되는 생일, 축일, 결혼기념일 등을 전용으로 관리할 수 있습니다. 장소와 시간 입력이 사라져 깔끔하며, 당일에는 '오늘의 업무' 화면 최상단에 <strong>축하 배너</strong>가 나타납니다! (기존의 모임이나 업무도 일정 수정에서 '기념일'로 바꿀 수 있습니다)</li>\n                <li><strong>💡 모임 제안</strong>: 사무실 식구들에게 모임을 제안하고 <strong>참석/불참 투표</strong>를 받을 수 있습니다."""
    if old_tip_2 in content:
        content = content.replace(old_tip_2, new_tip_2)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

for fp in files_index:
    patch_index(fp)

patch_manual(manual_file)
