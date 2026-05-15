const fs = require('fs');

const filePath = 'deal-register.html';
let content = fs.readFileSync(filePath, 'utf-8');

const target1 = `            if (!buildingId) {
                status.innerText = '건물을 선택해주세요.';
                return;
            }
            if (!roomId) {
                status.innerText = '호수를 선택해주세요.';
                return;
            }

            status.innerText = '저장 중...';
            
            const payload = {
                contract_type: contractType,
                balance_date: balanceDate ? balanceDate : null,
                memo: memo,
                user_id: window.currentUser.id
            };
            
            if (buildingId) payload.building_id = buildingId;
            if (roomId) payload.room_id = roomId;`;

const replacement1 = `            if (contractType !== '모임' && !buildingId) {
                status.innerText = '건물을 선택해주세요.';
                return;
            }
            if (contractType !== '모임' && !roomId) {
                status.innerText = '호수를 선택해주세요.';
                return;
            }

            status.innerText = '저장 중...';
            
            let finalMemo = memo;
            if (contractType === '모임') {
                const mTime = document.getElementById('meetingTime').value;
                const mLoc = document.getElementById('meetingLocation').value;
                const mAtt = document.getElementById('meetingAttendance').value;
                const mUrl = document.getElementById('meetingUrl').value;
                if(mTime) finalMemo += \`[TIME]\${mTime}[/TIME]\`;
                if(mLoc) finalMemo += \`[LOC]\${mLoc}[/LOC]\`;
                if(mAtt) finalMemo += \`[ATT]\${mAtt}[/ATT]\`;
                if(mUrl) finalMemo += \`[URL]\${mUrl}[/URL]\`;
            }

            const payload = {
                contract_type: contractType,
                balance_date: balanceDate ? balanceDate : null,
                memo: finalMemo,
                user_id: window.currentUser.id
            };
            
            if (contractType !== '모임' && buildingId) payload.building_id = buildingId;
            if (contractType !== '모임' && roomId) payload.room_id = roomId;`;

if (content.includes(target1)) {
    content = content.replace(target1, replacement1);
} else {
    console.log("Target 1 not found");
}

const target2 = `        async function saveDeal() {`;
const replacement2 = `        function toggleMeetingFields() {
            const isMeeting = document.getElementById('contractType').value === '모임';
            const mFields = document.getElementById('meetingFields');
            const pFields = document.getElementById('propertyFields');
            if(mFields) mFields.style.display = isMeeting ? 'block' : 'none';
            if(pFields) pFields.style.display = isMeeting ? 'none' : 'block';
            document.getElementById('memo').placeholder = isMeeting ? '모임 이름 (예: 마포구 협회 정기모임)' : '메모';
        }

        async function saveDeal() {`;

if (content.includes(target2)) {
    content = content.replace(target2, replacement2);
} else {
    console.log("Target 2 not found");
}

const target3 = `                let rawMemo = deal.memo || '';
                let linkUrl = null;
                let startDt = null;
                
                if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\\[URL\\](.*?)\\[\\/URL\\]/);
                    if (m) { linkUrl = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[START]')) {
                    const m = rawMemo.match(/\\[START\\](.*?)\\[\\/START\\]/);
                    if (m) { startDt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }`;

const replacement3 = `                let rawMemo = deal.memo || '';
                let linkUrl = null;
                let startDt = null;
                let mTime = null, mLoc = null, mAtt = null;
                
                if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\\[URL\\](.*?)\\[\\/URL\\]/);
                    if (m) { linkUrl = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[START]')) {
                    const m = rawMemo.match(/\\[START\\](.*?)\\[\\/START\\]/);
                    if (m) { startDt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[TIME]')) {
                    const m = rawMemo.match(/\\[TIME\\](.*?)\\[\\/TIME\\]/);
                    if (m) { mTime = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[LOC]')) {
                    const m = rawMemo.match(/\\[LOC\\](.*?)\\[\\/LOC\\]/);
                    if (m) { mLoc = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }
                if (rawMemo.includes('[ATT]')) {
                    const m = rawMemo.match(/\\[ATT\\](.*?)\\[\\/ATT\\]/);
                    if (m) { mAtt = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }`;

if (content.includes(target3)) {
    content = content.replace(target3, replacement3);
} else {
    console.log("Target 3 not found");
}

const target4 = `                let locationHtml = '';
                let typeBadgeHtml = '';
                
                if (isGlobal) {`;

const replacement4 = `                let locationHtml = '';
                let typeBadgeHtml = '';
                
                if (deal.contract_type === '모임') {
                    const timeStr = mTime ? \`\${mTime}\` : '';
                    let locStr = '';
                    if (mLoc) {
                        locStr = \`<span onclick="window.open('https://map.kakao.com/link/search/\${encodeURIComponent(mLoc)}', '_blank'); event.stopPropagation();" style="color: #2563eb; cursor: pointer; text-decoration: underline;">\${mLoc}</span>\`;
                    }
                    
                    let details = [timeStr, locStr].filter(Boolean).join(' · ');
                    if(details) details = \`<div style="font-size:13px; color:#6b7280; margin-top:2px;">\${details}</div>\`;
                    
                    let attBadge = '';
                    if(mAtt === '참석') attBadge = \`<span style="color:#16a34a; font-size:12px; font-weight:800;">[참석]</span>\`;
                    else if(mAtt === '미정') attBadge = \`<span style="color:#d97706; font-size:12px; font-weight:800;">[미정]</span>\`;
                    else if(mAtt === '불참') attBadge = \`<span style="color:#dc2626; font-size:12px; font-weight:800;">[불참]</span>\`;

                    const meetName = rawMemo.trim() || '모임 일정';
                    
                    locationHtml = \`<div style="color: #111827; font-size: 16px; font-weight: 800; line-height: 1.4; margin-bottom: 2px;">\${meetName} \${attBadge}</div>\${details}\`;
                    
                    typeBadgeHtml = \`<span style="background: #fdf4ff; color: #c026d3; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800;">모임</span>\`;
                    rawMemo = ''; // Hide memo since it is used as the title
                } else if (isGlobal) {`;

if (content.includes(target4)) {
    content = content.replace(target4, replacement4);
} else {
    console.log("Target 4 not found");
}

fs.writeFileSync(filePath, content, 'utf-8');
console.log("Updated HTML!");
