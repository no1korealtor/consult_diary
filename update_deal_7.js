const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, 'deal-register.html');
let lines = fs.readFileSync(file, 'utf8').split('\n');

for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('<h3 style="margin-top: 0;">새 일정 추가</h3>')) {
        lines[i] = `        <h3 style="margin-top: 0; margin-bottom: 16px;">새 일정 추가</h3>
        <div style="display: flex; background: #f1f5f9; padding: 4px; border-radius: 12px; margin-bottom: 16px;">
            <button id="tabWork" type="button" onclick="switchTab('work')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: #ffffff; color: #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">🏢 업무 일정</button>
            <button id="tabMeet" type="button" onclick="switchTab('meet')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: transparent; color: #64748b; box-shadow: none;">👥 모임 일정</button>
        </div>`;
    }

    if (lines[i].includes('<select id="contractType" onchange="toggleMeetingFields()">')) {
        lines[i] = lines[i].replace('onchange="toggleMeetingFields()"', '');
    }

    if (lines[i].includes('<option value="모임">모임</option>')) {
        lines[i] = lines[i].replace('<option value="모임">모임</option>', '<option value="모임" style="display: none;">모임</option>');
    }

    if (lines[i].includes('function toggleMeetingFields() {')) {
        let replacement = `        let currentTab = 'work';
        function switchTab(tab) {
            currentTab = tab;
            const tabWork = document.getElementById('tabWork');
            const tabMeet = document.getElementById('tabMeet');
            const contractType = document.getElementById('contractType');
            const propertyFields = document.getElementById('propertyFields');
            const meetingFields = document.getElementById('meetingFields');
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
                if (contractType.value === '모임') contractType.value = '입주 정산';
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
                memo.placeholder = '모임 이름 (예: 마포구 협회 정기모임)';
            }
        }`;
        
        // Remove old lines of toggleMeetingFields
        lines[i] = replacement;
        for (let j = i+1; j < lines.length; j++) {
            if (lines[j].includes('document.getElementById(\'memo\').placeholder')) {
                lines[j] = ''; // clear it
                lines[j+1] = ''; // clear closing brace
                break;
            } else {
                lines[j] = ''; // clear it
            }
        }
    }
}

fs.writeFileSync(file, lines.join('\n'));
console.log('done');
