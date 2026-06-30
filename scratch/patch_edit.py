import re
import os

files_to_edit = [
    r'd:\부동산업무\antigravity\consult_diary\deal-edit.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\deal-edit.html'
]

def patch_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update contractType select to include onchange and new options
    old_select = """<select id="contractType" style="margin-bottom: 12px;">
            <option value="정산">정산</option>
            <option value="임대차 잔금">임대차 잔금</option>
            <option value="매매 잔금">매매 잔금</option>
            <option value="잔금" style="display:none;">잔금 (구버전)</option>
            <option value="임대차계약">임대차계약</option>
            <option value="매매계약">매매계약</option>
            <option value="계약해제">계약해제</option>
            <option value="집보여주기">집보여주기</option>
            <option value="기타">기타</option>
        </select>"""
    new_select = """<select id="contractType" style="margin-bottom: 12px;" onchange="handleContractTypeChange()">
            <option value="정산">정산</option>
            <option value="임대차 잔금">임대차 잔금</option>
            <option value="매매 잔금">매매 잔금</option>
            <option value="잔금" style="display:none;">잔금 (구버전)</option>
            <option value="임대차계약">임대차계약</option>
            <option value="매매계약">매매계약</option>
            <option value="계약해제">계약해제</option>
            <option value="집보여주기">집보여주기</option>
            <option value="기타">기타</option>
            <option value="모임">👥 모임</option>
            <option value="기념일">🎉 기념일</option>
        </select>"""
    if old_select in content:
        content = content.replace(old_select, new_select)
    else:
        # try a generic replace if whitespace differs
        content = re.sub(r'<select id="contractType" style="margin-bottom: 12px;">[\s\S]*?</select>', new_select, content)

    # 2. Add id="mTimeWrapper" to time wrapper
    content = content.replace('<div style="flex: 1;">\n                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">\n                    <label style="font-size: 12px; color: #6b7280; font-weight: 600;">시간 지정 (선택)</label>',
                              '<div style="flex: 1;" id="mTimeWrapper">\n                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">\n                    <label style="font-size: 12px; color: #6b7280; font-weight: 600;">시간 지정 (선택)</label>')

    # 3. Add [ANNIVERSARY] to exactTags
    content = content.replace("const exactTags = ['[DONE]', '[PRIVATE]', '[PROPOSAL]', '[PENDING_ADMIN]'];",
                              "const exactTags = ['[DONE]', '[PRIVATE]', '[PROPOSAL]', '[PENDING_ADMIN]', '[ANNIVERSARY]'];")

    # 4. Modify loadDeal logic for '모임' to show contractType and handle Anniversary
    old_load_meet = """            if (data.schedule_type === '모임' || (!data.buildings && !data.properties)) {
                document.getElementById('propertyFields').style.display = 'none';
                document.getElementById('contractType').style.display = 'none';
                if(document.getElementById('clientSelectContainer')) document.getElementById('clientSelectContainer').style.display = 'none';
                document.getElementById('balanceDateLabel').style.display = 'block';
                document.querySelector('.notice').innerText = "💡 장소, 링크 및 메모를 수정할 수 있습니다.";
                document.getElementById('meetingEditFields').style.display = 'block';
                document.getElementById('repeatOptionsContainer').style.display = 'block';"""
    new_load_meet = """            if (data.schedule_type === '모임' || (!data.buildings && !data.properties)) {
                document.getElementById('propertyFields').style.display = 'none';
                document.getElementById('contractType').style.display = 'block';
                const isAnni = window.preservedTags.includes('[ANNIVERSARY]');
                document.getElementById('contractType').value = isAnni ? '기념일' : '모임';
                if(document.getElementById('clientSelectContainer')) document.getElementById('clientSelectContainer').style.display = 'none';
                document.getElementById('balanceDateLabel').style.display = 'block';
                document.querySelector('.notice').innerText = isAnni ? "💡 기념일 이름과 날짜, 메모를 수정할 수 있습니다." : "💡 장소, 링크 및 메모를 수정할 수 있습니다.";
                document.getElementById('meetingEditFields').style.display = isAnni ? 'none' : 'block';
                document.getElementById('mTimeWrapper').style.display = isAnni ? 'none' : 'block';
                document.getElementById('repeatOptionsContainer').style.display = 'block';"""
    if old_load_meet in content:
        content = content.replace(old_load_meet, new_load_meet)

    # 5. Add handleContractTypeChange function
    handle_func = """
        function handleContractTypeChange() {
            const val = document.getElementById('contractType').value;
            const propFields = document.getElementById('propertyFields');
            const meetFields = document.getElementById('meetingEditFields');
            const timeWrapper = document.getElementById('mTimeWrapper');
            const clientRow = document.getElementById('clientSelectContainer');
            const notice = document.querySelector('.notice');
            const repOpt = document.getElementById('repeatOptionsContainer');

            if (val === '모임' || val === '기념일') {
                propFields.style.display = 'none';
                if(clientRow) clientRow.style.display = 'none';
                repOpt.style.display = 'block';
                
                if (val === '모임') {
                    meetFields.style.display = 'block';
                    if (timeWrapper) timeWrapper.style.display = 'block';
                    if (notice) notice.innerText = "💡 장소, 링크 및 메모를 수정할 수 있습니다.";
                } else {
                    meetFields.style.display = 'none';
                    if (timeWrapper) timeWrapper.style.display = 'none';
                    if (notice) notice.innerText = "💡 기념일 이름과 날짜, 메모를 수정할 수 있습니다.";
                }
            } else {
                propFields.style.display = 'block';
                if(clientRow) clientRow.style.display = 'block';
                meetFields.style.display = 'none';
                repOpt.style.display = 'none';
                if (timeWrapper) timeWrapper.style.display = 'block';
                if (notice) notice.innerText = "💡 건물/매물이나 호수를 선택하여 변경할 수 있습니다.";
            }
        }
    """
    if "function execDaumPostcodeMeeting()" in content and "handleContractTypeChange" not in content:
        content = content.replace("function execDaumPostcodeMeeting() {", handle_func + "\n        function execDaumPostcodeMeeting() {")

    # 6. Update save logic
    old_save_tags = """            let finalTags = window.preservedTags || '';
            const todayStr = new Date().toLocaleDateString('en-CA');
            if (balanceDate && balanceDate >= todayStr) {
                finalTags = finalTags.replace(/\\[DONE\\]/g, '').replace(/\\[DONE:[^\\]]+\\]/g, '');
            }
            payload.memo = finalTags + memo;"""
    new_save_tags = """            let finalTags = window.preservedTags || '';
            const todayStr = new Date().toLocaleDateString('en-CA');
            if (balanceDate && balanceDate >= todayStr) {
                finalTags = finalTags.replace(/\\[DONE\\]/g, '').replace(/\\[DONE:[^\\]]+\\]/g, '');
            }
            
            // Handle Anniversary tag based on contractType
            if (contractType === '기념일') {
                if (!finalTags.includes('[ANNIVERSARY]')) finalTags += '[ANNIVERSARY]';
                contractType = '모임'; // Save as '모임' for backend compat
            } else if (contractType === '모임') {
                finalTags = finalTags.replace('\\[ANNIVERSARY\\]', '');
            }
            
            payload.memo = finalTags + memo;"""
    
    old_const_contract = "const contractType = document.getElementById('contractType').style.display !== 'none' ? document.getElementById('contractType').value : undefined;"
    new_let_contract = "let contractType = document.getElementById('contractType').style.display !== 'none' ? document.getElementById('contractType').value : undefined;"
    content = content.replace(old_const_contract, new_let_contract)

    if old_save_tags in content:
        content = content.replace(old_save_tags, new_save_tags)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filepath}")

for fp in files_to_edit:
    patch_file(fp)
