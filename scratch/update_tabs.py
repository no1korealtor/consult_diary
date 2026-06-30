import re

files_to_update = [
    r'd:\부동산업무\antigravity\consult_diary\deal-register.html',
    r'd:\부동산업무\antigravity\consult_diary\smart_schedule\index.html'
]

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update tabs HTML
    old_tabs = """<button id="tabWork" type="button" onclick="switchTab('work')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: #ffffff; color: #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">🏢 업무 일정</button>
            <button id="tabMeet" type="button" onclick="switchTab('meet')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: transparent; color: #64748b; box-shadow: none;">👥 모임(기념일)</button>"""
    new_tabs = """<button id="tabWork" type="button" onclick="switchTab('work')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: #ffffff; color: #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">🏢 업무 일정</button>
            <button id="tabMeet" type="button" onclick="switchTab('meet')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: transparent; color: #64748b; box-shadow: none;">👥 모임</button>
            <button id="tabAnni" type="button" onclick="switchTab('anni')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: transparent; color: #64748b; box-shadow: none;">🎉 기념일</button>"""
    
    content = content.replace(old_tabs, new_tabs)

    # 2. Update meeting name placeholder
    content = content.replace('📌 모임/기념일 이름 (예: 정기모임, 생일 등)', '📌 모임 이름 (예: 정기모임, 회식 등)')

    # 3. Replace switchTab logic
    old_switch_tab = """        let currentTab = 'work';
        function switchTab(tab) {
            currentTab = tab;
            const tabWork = document.getElementById('tabWork');
            const tabMeet = document.getElementById('tabMeet');
            const contractType = document.getElementById('contractType');
            const propertyFields = document.getElementById('propertyFields');
            const meetingFields = document.getElementById('meetingFields');
            const meetSubTabs = document.getElementById('meetSubTabs');
            const meetingName = document.getElementById('meetingName');
            const timeCol = document.getElementById('timeCol');
            const memo = document.getElementById('memo');

            if (tab === 'work') {
                tabWork.style.background = '#ffffff';
                tabWork.style.color = '#3b82f6';
                tabWork.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
                tabMeet.style.background = 'transparent';
                tabMeet.style.color = '#64748b';
                tabMeet.style.boxShadow = 'none';

                contractType.style.display = 'block';
                propertyFields.style.display = 'block';
                meetingFields.style.display = 'none';
                if (meetSubTabs) meetSubTabs.style.display = 'none';
                if (meetingName) meetingName.style.display = 'none';
                const chkRep = document.getElementById('repeatOptionsContainer');
                if (chkRep) chkRep.style.display = 'none';
                if (contractType.value === '모임') contractType.value = '정산';
                memo.placeholder = '메모';
            } else {
                tabMeet.style.background = '#ffffff';
                tabMeet.style.color = '#8b5cf6';
                tabMeet.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
                tabWork.style.background = 'transparent';
                tabWork.style.color = '#64748b';
                tabWork.style.boxShadow = 'none';

                contractType.style.display = 'none';
                contractType.value = '모임';
                propertyFields.style.display = 'none';
                meetingFields.style.display = 'block';
                if (meetSubTabs) meetSubTabs.style.display = 'flex';
                if (meetingName) meetingName.style.display = 'block';
                const chkRep = document.getElementById('repeatOptionsContainer');
                if (chkRep) chkRep.style.display = 'block';
                memo.placeholder = '추가 메모 (선택사항)';
            }
        }"""
    
    new_switch_tab = """        let currentTab = 'work';
        function switchTab(tab) {
            currentTab = tab;
            const tabWork = document.getElementById('tabWork');
            const tabMeet = document.getElementById('tabMeet');
            const tabAnni = document.getElementById('tabAnni');
            const contractType = document.getElementById('contractType');
            const propertyFields = document.getElementById('propertyFields');
            const meetingFields = document.getElementById('meetingFields');
            const meetSubTabs = document.getElementById('meetSubTabs');
            const meetingName = document.getElementById('meetingName');
            const timeCol = document.getElementById('timeCol');
            const memo = document.getElementById('memo');
            const chkRep = document.getElementById('repeatOptionsContainer');

            [tabWork, tabMeet, tabAnni].forEach(t => {
                if (t) {
                    t.style.background = 'transparent';
                    t.style.color = '#64748b';
                    t.style.boxShadow = 'none';
                }
            });

            if (tab === 'work') {
                tabWork.style.background = '#ffffff';
                tabWork.style.color = '#3b82f6';
                tabWork.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';

                contractType.style.display = 'block';
                propertyFields.style.display = 'block';
                meetingFields.style.display = 'none';
                if (meetSubTabs) meetSubTabs.style.display = 'none';
                if (meetingName) meetingName.style.display = 'none';
                if (chkRep) chkRep.style.display = 'none';
                if (timeCol) timeCol.style.display = 'block';
                if (contractType.value === '모임') contractType.value = '정산';
                memo.placeholder = '메모';
            } else if (tab === 'meet') {
                tabMeet.style.background = '#ffffff';
                tabMeet.style.color = '#8b5cf6';
                tabMeet.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';

                contractType.style.display = 'none';
                contractType.value = '모임';
                propertyFields.style.display = 'none';
                meetingFields.style.display = 'block';
                if (meetSubTabs) meetSubTabs.style.display = 'flex';
                if (meetingName) {
                    meetingName.style.display = 'block';
                    meetingName.placeholder = '📌 모임 이름 (예: 정기모임, 회식 등)';
                }
                if (chkRep) chkRep.style.display = 'block';
                if (timeCol) timeCol.style.display = 'block';
                memo.placeholder = '추가 메모 (선택사항)';
            } else if (tab === 'anni') {
                if (tabAnni) {
                    tabAnni.style.background = '#ffffff';
                    tabAnni.style.color = '#f59e0b';
                    tabAnni.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
                }

                contractType.style.display = 'none';
                contractType.value = '모임'; // 백엔드 로직 호환을 위해 모임으로 유지
                propertyFields.style.display = 'none';
                meetingFields.style.display = 'none'; // 장소 등 숨김
                if (meetSubTabs) meetSubTabs.style.display = 'none';
                if (meetingName) {
                    meetingName.style.display = 'block';
                    meetingName.placeholder = '🎉 기념일 이름 (예: 생일, 결혼기념일 등)';
                }
                if (chkRep) chkRep.style.display = 'block';
                if (timeCol) timeCol.style.display = 'none'; // 시간 숨김
                memo.placeholder = '기념일 관련 메모';
            }
        }"""
    
    if old_switch_tab in content:
        content = content.replace(old_switch_tab, new_switch_tab)
    else:
        print("Warning: old_switch_tab not found in", filepath)

    # 4. Replace saveDeal logic
    old_save_deal_meeting = """            if (contractType === '모임') {
                const mNameElem = document.getElementById('meetingName');
                if (mNameElem && !mNameElem.value.trim()) {
                    status.innerText = '모임 이름을 입력해주세요.';
                    return;
                }
                const mName = mNameElem ? mNameElem.value.trim() : '';

                if (mName) finalMemo = mName + (finalMemo ? '\\n' + finalMemo : '');
                pLocBase = document.getElementById('meetingLocation').value || null;
                pLocDetail = document.getElementById('meetingLocationDetail') ? document.getElementById('meetingLocationDetail').value.trim() : null;
                pAtt = document.getElementById('meetingAttendance') ? document.getElementById('meetingAttendance').value : null;
                pUrl = document.getElementById('meetingUrl') ? document.getElementById('meetingUrl').value : null;
                pUrlName = document.getElementById('meetingUrlName') ? document.getElementById('meetingUrlName').value : null;

                if (typeof currentMeetType !== 'undefined') {
                    if (currentMeetType === 'PRIVATE') {
                        finalMemo += '\\n[PRIVATE]';
                    } else if (currentMeetType === 'PROPOSAL') {
                        isProposal = true;
                        const pDeadDate = document.getElementById('proposalDeadlineDate') ? document.getElementById('proposalDeadlineDate').value : '';
                        const pDeadTime = getTimeFromSelects('propTime');
                        pDead = (pDeadDate && pDeadTime) ? pDeadDate + 'T' + pDeadTime + ':00' : null;
                        pMin = document.getElementById('proposalMinAtt') ? parseInt(document.getElementById('proposalMinAtt').value) : null;
                    }
                } else {
                    finalMemo += '\\n[PRIVATE]';
                }
            }"""

    new_save_deal_meeting = """            if (contractType === '모임') {
                const isAnni = (typeof currentTab !== 'undefined' && currentTab === 'anni');
                const mNameElem = document.getElementById('meetingName');
                if (mNameElem && !mNameElem.value.trim()) {
                    status.innerText = (isAnni ? '기념일' : '모임') + ' 이름을 입력해주세요.';
                    return;
                }
                const mName = mNameElem ? mNameElem.value.trim() : '';

                if (mName) finalMemo = mName + (finalMemo ? '\\n' + finalMemo : '');
                
                if (!isAnni) {
                    pLocBase = document.getElementById('meetingLocation').value || null;
                    pLocDetail = document.getElementById('meetingLocationDetail') ? document.getElementById('meetingLocationDetail').value.trim() : null;
                    pAtt = document.getElementById('meetingAttendance') ? document.getElementById('meetingAttendance').value : null;
                    pUrl = document.getElementById('meetingUrl') ? document.getElementById('meetingUrl').value : null;
                    pUrlName = document.getElementById('meetingUrlName') ? document.getElementById('meetingUrlName').value : null;
                } else {
                    finalMemo += '\\n[ANNIVERSARY]';
                    pTime = null;
                }

                if (typeof currentMeetType !== 'undefined') {
                    if (currentMeetType === 'PRIVATE') {
                        finalMemo += '\\n[PRIVATE]';
                    } else if (currentMeetType === 'PROPOSAL' && !isAnni) {
                        isProposal = true;
                        const pDeadDate = document.getElementById('proposalDeadlineDate') ? document.getElementById('proposalDeadlineDate').value : '';
                        const pDeadTime = getTimeFromSelects('propTime');
                        pDead = (pDeadDate && pDeadTime) ? pDeadDate + 'T' + pDeadTime + ':00' : null;
                        pMin = document.getElementById('proposalMinAtt') ? parseInt(document.getElementById('proposalMinAtt').value) : null;
                    }
                } else {
                    finalMemo += '\\n[PRIVATE]';
                }
            }"""
    
    if old_save_deal_meeting in content:
        content = content.replace(old_save_deal_meeting, new_save_deal_meeting)
    else:
        print("Warning: old_save_deal_meeting not found in", filepath)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

for fp in files_to_update:
    update_file(fp)
