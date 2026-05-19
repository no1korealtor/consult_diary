import os
import glob
import re

files_to_update = glob.glob("*.html")

save_deal_old = """            let finalMemo = memo;
            if (contractType === '모임') {
                const mNameElem = document.getElementById('meetingName');
                if (mNameElem && !mNameElem.value.trim()) {
                    status.innerText = '모임 이름을 입력해주세요.';
                    return;
                }
                const mName = mNameElem ? mNameElem.value.trim() : '';

                function getTimeFromSelects(prefix) {
                    const ampm = document.getElementById(prefix + 'AmPm')?.value;
                    const hour = document.getElementById(prefix + 'Hour')?.value;
                    const min = document.getElementById(prefix + 'Minute')?.value;
                    if (!ampm || !hour || !min) return '';
                    let hh = parseInt(hour, 10);
                    if (ampm === 'PM' && hh < 12) hh += 12;
                    if (ampm === 'AM' && hh === 12) hh = 0;
                    return String(hh).padStart(2, '0') + ':' + min;
                }

                finalMemo = mName;
                const mTime = getTimeFromSelects('meetTime');
                const mLocBase = document.getElementById('meetingLocation').value;
                const mLocDetail = document.getElementById('meetingLocationDetail') ? document.getElementById('meetingLocationDetail').value.trim() : '';
                const mLoc = mLocBase + (mLocDetail ? ' ' + mLocDetail : '');
                const mAtt = document.getElementById('meetingAttendance').value;
                const mUrl = document.getElementById('meetingUrl').value;
                const mUrlName = document.getElementById('meetingUrlName').value;
                if(mUrlName && mUrl) {
                    finalMemo += `[URL]${mUrl}|${mUrlName}[/URL]`;
                } else if(mUrl) {
                    finalMemo += `[URL]${mUrl}[/URL]`;
                }

                if(mTime) finalMemo += `[TIME]${mTime}[/TIME]`;
                if(mLoc) finalMemo += `[LOC]${mLoc}[/LOC]`;
                if(mAtt) finalMemo += `[ATT]${mAtt}[/ATT]`;

                if (typeof currentMeetType !== 'undefined') {
                    if (currentMeetType === 'PRIVATE') {
                        finalMemo += '[PRIVATE]';
                    } else if (currentMeetType === 'PROPOSAL') {
                        finalMemo += '[PROPOSAL]';
                        const pDeadDate = document.getElementById('proposalDeadlineDate') ? document.getElementById('proposalDeadlineDate').value : '';
                        const pDeadTime = getTimeFromSelects('propTime');
                        const pDead = (pDeadDate && pDeadTime) ? pDeadDate + 'T' + pDeadTime : '';
                        const pMin = document.getElementById('proposalMinAtt') ? document.getElementById('proposalMinAtt').value : '';
                        if(pDead) finalMemo += `[DEADLINE]${pDead}[/DEADLINE]`;
                        if(pMin) finalMemo += `[MIN_ATT]${pMin}[/MIN_ATT]`;
                    }
                } else {
                    // Fallback just in case
                    finalMemo += '[PRIVATE]';
                }
            } else if (contractType === '잔금') {
                const chkTime = document.getElementById('chkTime')?.checked;
                const chkUtil = document.getElementById('chkUtil')?.checked;
                if (chkTime) {
                    const d = document.getElementById('jangumTimeDate')?.value;
                    const ap = document.getElementById('jangumTimeAmPm')?.value;
                    const h = document.getElementById('jangumTimeHour')?.value;
                    const m = document.getElementById('jangumTimeMinute')?.value;
                    if (d && ap && h && m) {
                        let hh = parseInt(h, 10);
                        if (ap === 'PM' && hh < 12) hh += 12;
                        if (ap === 'AM' && hh === 12) hh = 0;
                        const timeStr = `${d} ${String(hh).padStart(2, '0')}:${m}`;
                        finalMemo += `\\n[TASK:잔금시간] ${timeStr}`;
                    }
                }
                if (chkUtil) {
                    finalMemo += `\\n[TASK:공과금정산] 대상`;
                }
            }
                
            if (memo.trim()) {
                finalMemo += `\\n${memo.trim()}`;
            }

            const payload = {
                schedule_type: contractType,
                schedule_date: balanceDate ? balanceDate : null,
                memo: finalMemo,
                user_id: window.currentUser.id
            };"""

save_deal_new = """            let finalMemo = memo.trim();
            let pTime = null, pLocBase = null, pLocDetail = null, pAtt = null, pUrl = null, pUrlName = null;
            let isProposal = false, pDead = null, pMin = null;
            
            if (contractType === '모임') {
                const mNameElem = document.getElementById('meetingName');
                if (mNameElem && !mNameElem.value.trim()) {
                    status.innerText = '모임 이름을 입력해주세요.';
                    return;
                }
                const mName = mNameElem ? mNameElem.value.trim() : '';

                function getTimeFromSelects(prefix) {
                    const ampm = document.getElementById(prefix + 'AmPm')?.value;
                    const hour = document.getElementById(prefix + 'Hour')?.value;
                    const min = document.getElementById(prefix + 'Minute')?.value;
                    if (!ampm || !hour || !min) return '';
                    let hh = parseInt(hour, 10);
                    if (ampm === 'PM' && hh < 12) hh += 12;
                    if (ampm === 'AM' && hh === 12) hh = 0;
                    return String(hh).padStart(2, '0') + ':' + min;
                }

                if (mName) finalMemo = mName + (finalMemo ? '\\n' + finalMemo : '');
                
                pTime = getTimeFromSelects('meetTime') || null;
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
            } else if (contractType === '잔금') {
                const chkTime = document.getElementById('chkTime')?.checked;
                const chkUtil = document.getElementById('chkUtil')?.checked;
                if (chkTime) {
                    const d = document.getElementById('jangumTimeDate')?.value;
                    const ap = document.getElementById('jangumTimeAmPm')?.value;
                    const h = document.getElementById('jangumTimeHour')?.value;
                    const m = document.getElementById('jangumTimeMinute')?.value;
                    if (d && ap && h && m) {
                        let hh = parseInt(h, 10);
                        if (ap === 'PM' && hh < 12) hh += 12;
                        if (ap === 'AM' && hh === 12) hh = 0;
                        const timeStr = `${d} ${String(hh).padStart(2, '0')}:${m}`;
                        finalMemo += `\\n[TASK:잔금시간] ${timeStr}`;
                    }
                }
                if (chkUtil) {
                    finalMemo += `\\n[TASK:공과금정산] 대상`;
                }
            }

            const payload = {
                schedule_type: contractType,
                schedule_date: balanceDate ? balanceDate : null,
                schedule_time: pTime,
                location: pLocBase,
                location_detail: pLocDetail,
                url: pUrl,
                url_name: pUrlName,
                is_proposal: isProposal,
                proposal_deadline: pDead,
                min_attendance: pMin,
                memo: finalMemo,
                user_id: window.currentUser.id
            };"""

create_old = """                let linkName = '관련 링크';
                if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\[URL\](.*?)\[\/URL\]/);
                    if (m) { 
                        let urlData = m[1];
                        if (urlData.includes('|')) {
                            const parts = urlData.split('|');
                            linkUrl = parts[0];
                            linkName = parts[1];
                        } else {
                            linkUrl = urlData;
                        }
                        rawMemo = rawMemo.replace(m[0], ''); 
                    }
                }
                if (rawMemo.includes('[START]')) {
                    const m = rawMemo.match(/\[START\](.*?)\[\/START\]/);
                    if (m) { startDt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                
                let mTime = null, mLoc = null, mAtt = null;
                let myAtt = null;
                if (rawMemo.includes('[TIME]')) {
                    const m = rawMemo.match(/\[TIME\](.*?)\[\/TIME\]/);
                    if (m) { mTime = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[LOC]')) {
                    const m = rawMemo.match(/\[LOC\](.*?)\[\/LOC\]/);
                    if (m) { mLoc = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[ATT]')) {
                    const m = rawMemo.match(/\[ATT\](.*?)\[\/ATT\]/);
                    if (m) { mAtt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }

                let mDeadline = null, mMinAtt = null;
                if (rawMemo.includes('[DEADLINE]')) {
                    const m = rawMemo.match(/\[DEADLINE\](.*?)\[\/DEADLINE\]/);
                    if (m) { mDeadline = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[MIN_ATT]')) {
                    const m = rawMemo.match(/\[MIN_ATT\](.*?)\[\/MIN_ATT\]/);
                    if (m) { mMinAtt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                
                let tJangumTime = null;
                let tUtil = false;
                if (rawMemo.includes('[TASK:잔금시간]')) {
                    const m = rawMemo.match(/\[TASK:잔금시간\]\\s*(.*?)(?=\\n|$)/);
                    if (m) { tJangumTime = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[TASK:공과금정산]')) {
                    const m = rawMemo.match(/\[TASK:공과금정산\]\\s*(.*?)(?=\\n|$)/);
                    if (m) { tUtil = true; rawMemo = rawMemo.replace(m[0], ''); }
                }
                
                const isPrivateMeeting = rawMemo.includes('[PRIVATE]');
                if (isPrivateMeeting) {
                    rawMemo = rawMemo.replace('[PRIVATE]', '');
                }
                const isProposal = rawMemo.includes('[PROPOSAL]');
                if (isProposal) {
                    rawMemo = rawMemo.replace('[PROPOSAL]', '');
                }
                
                const isMine = schedule.user_id === window.currentUser.id;"""

create_new = """                let linkUrl = schedule.url || null;
                let linkName = schedule.url_name || '관련 링크';
                if (!linkUrl && rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\[URL\](.*?)\[\/URL\]/);
                    if (m) { 
                        let urlData = m[1];
                        if (urlData.includes('|')) {
                            const parts = urlData.split('|');
                            linkUrl = parts[0];
                            linkName = parts[1];
                        } else {
                            linkUrl = urlData;
                        }
                        rawMemo = rawMemo.replace(m[0], ''); 
                    }
                }
                if (rawMemo.includes('[START]')) {
                    const m = rawMemo.match(/\[START\](.*?)\[\/START\]/);
                    if (m) { startDt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                
                let mTime = schedule.schedule_time ? schedule.schedule_time.substring(0, 5) : null;
                let mLoc = schedule.location || null;
                if (schedule.location_detail) mLoc += ' ' + schedule.location_detail;
                let mAtt = null;
                let myAtt = null;

                if (!mTime && rawMemo.includes('[TIME]')) {
                    const m = rawMemo.match(/\[TIME\](.*?)\[\/TIME\]/);
                    if (m) { mTime = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (!mLoc && rawMemo.includes('[LOC]')) {
                    const m = rawMemo.match(/\[LOC\](.*?)\[\/LOC\]/);
                    if (m) { mLoc = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[ATT]')) {
                    const m = rawMemo.match(/\[ATT\](.*?)\[\/ATT\]/);
                    if (m) { mAtt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }

                let mDeadline = schedule.proposal_deadline || null;
                let mMinAtt = schedule.min_attendance || null;
                if (!mDeadline && rawMemo.includes('[DEADLINE]')) {
                    const m = rawMemo.match(/\[DEADLINE\](.*?)\[\/DEADLINE\]/);
                    if (m) { mDeadline = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (!mMinAtt && rawMemo.includes('[MIN_ATT]')) {
                    const m = rawMemo.match(/\[MIN_ATT\](.*?)\[\/MIN_ATT\]/);
                    if (m) { mMinAtt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                
                let tJangumTime = null;
                let tUtil = false;
                if (rawMemo.includes('[TASK:잔금시간]')) {
                    const m = rawMemo.match(/\[TASK:잔금시간\]\\s*(.*?)(?=\\n|$)/);
                    if (m) { tJangumTime = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[TASK:공과금정산]')) {
                    const m = rawMemo.match(/\[TASK:공과금정산\]\\s*(.*?)(?=\\n|$)/);
                    if (m) { tUtil = true; rawMemo = rawMemo.replace(m[0], ''); }
                }
                
                const isPrivateMeeting = rawMemo.includes('[PRIVATE]');
                if (isPrivateMeeting) {
                    rawMemo = rawMemo.replace('[PRIVATE]', '');
                }
                const isProposal = schedule.is_proposal || rawMemo.includes('[PROPOSAL]');
                if (rawMemo.includes('[PROPOSAL]')) {
                    rawMemo = rawMemo.replace('[PROPOSAL]', '');
                }
                
                const isMine = schedule.user_id === window.currentUser.id;"""

for filepath in files_to_update:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    if save_deal_old in new_content:
        new_content = new_content.replace(save_deal_old, save_deal_new)
        print(f"Updated save_deal logic in {filepath}")
    
    if create_old in new_content:
        new_content = new_content.replace(create_old, create_new)
        print(f"Updated parsing logic in {filepath}")
        
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Done Refactoring")
