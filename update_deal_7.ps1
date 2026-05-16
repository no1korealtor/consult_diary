$file = "deal-register.html"
$lines = Get-Content $file -Encoding UTF8

for ($i = 0; $i -lt $lines.Length; $i++) {
    if ($lines[$i] -match '<h3 style="margin-top: 0;">새 일정 추가</h3>') {
        $lines[$i] = '        <h3 style="margin-top: 0; margin-bottom: 16px;">새 일정 추가</h3>
        <div style="display: flex; background: #f1f5f9; padding: 4px; border-radius: 12px; margin-bottom: 16px;">
            <button id="tabWork" type="button" onclick="switchTab(''work'')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: #ffffff; color: #3b82f6; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">🏢 업무 일정</button>
            <button id="tabMeet" type="button" onclick="switchTab(''meet'')" style="flex: 1; margin: 0; padding: 10px; border-radius: 10px; font-size: 15px; font-weight: 800; border: none; cursor: pointer; transition: 0.2s; background: transparent; color: #64748b; box-shadow: none;">👥 모임 일정</button>
        </div>'
    }

    if ($lines[$i] -match '<select id="contractType" onchange="toggleMeetingFields()">') {
        $lines[$i] = '    <select id="contractType">'
    }

    if ($lines[$i] -match '<option value="모임">모임</option>') {
        $lines[$i] = '        <option value="모임" style="display: none;">모임</option>'
    }

    if ($lines[$i] -match '<textarea id="memo" placeholder="메모 \(모임일 경우 모임명 입력\)"></textarea>') {
        $lines[$i] = '    <textarea id="memo" placeholder="메모"></textarea>'
    }

    if ($lines[$i] -match 'function toggleMeetingFields\(\) \{') {
        $replacement = "        let currentTab = 'work';
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
        }"
        
        $lines[$i] = $replacement
        for ($j = $i + 1; $j -lt $lines.Length; $j++) {
            if ($lines[$j] -match "document.getElementById\('memo'\).placeholder") {
                $lines[$j] = ""
                $lines[$j+1] = ""
                break
            } else {
                $lines[$j] = ""
            }
        }
    }
}

Set-Content -Path $file -Value $lines -Encoding UTF8
Write-Output "Done"
