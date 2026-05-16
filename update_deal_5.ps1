$content = Get-Content -Path "deal-register.html" -Raw -Encoding UTF8

# 1. Add Checkbox to meetingFields
$t1 = "            <input type=`"url`" id=`"meetingUrl`" placeholder=`"관련 링크 (URL)`" style=`"margin-bottom: 0; flex: 1;`">
            <input type=`"text`" id=`"meetingUrlName`" placeholder=`"링크 이름 (예: 국세청 홈택스)`" style=`"margin-bottom: 0; flex: 1;`">
        </div>
    </div>"
$r1 = "            <input type=`"url`" id=`"meetingUrl`" placeholder=`"관련 링크 (URL)`" style=`"margin-bottom: 0; flex: 1;`">
            <input type=`"text`" id=`"meetingUrlName`" placeholder=`"링크 이름 (예: 국세청 홈택스)`" style=`"margin-bottom: 0; flex: 1;`">
        </div>
        <div style=`"display: flex; gap: 8px; margin-top: 12px; align-items: center; background: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;`">
            <input type=`"checkbox`" id=`"meetingIsGlobal`" style=`"width: 18px; height: 18px; margin: 0; cursor: pointer;`">
            <label for=`"meetingIsGlobal`" style=`"font-size: 13px; color: #334155; font-weight: 700; cursor: pointer;`">📢 전체 직원에게 공지 (참석 여부 투표 포함)</label>
        </div>
    </div>"
$content = $content.Replace($t1, $r1)

# 2. Add to saveDeal
$t2 = "                if(mAtt) finalMemo += `"[ATT]${mAtt}[/ATT]`";
                if(mUrl) finalMemo += `"[URL]${mUrl}[/URL]`";
            }"
$r2 = "                if(mAtt) finalMemo += `"[ATT]${mAtt}[/ATT]`";
                if(mUrl) finalMemo += `"[URL]${mUrl}[/URL]`";
                const isGlobalMeeting = document.getElementById('meetingIsGlobal').checked;
                if(!isGlobalMeeting) finalMemo += '[PRIVATE]';
            }"
$content = $content.Replace($t2, $r2)

# 3. Filter in loadDeals
$t3 = "            if (data) {
                allDeals = data;
            }"
$r3 = "            if (data) {
                allDeals = data.filter(deal => {
                    const isMine = deal.user_id === window.currentUser.id;
                    const isPrivate = (deal.memo || '').includes('[PRIVATE]');
                    if (isPrivate && !isMine) return false;
                    return true;
                });
            }"
$content = $content.Replace($t3, $r3)

# 4. Parse [PRIVATE] in createDealListItem
$t4 = "            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let isDone = false;"
$r4 = "            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let isPrivate = false;
                if (rawMemo.includes('[PRIVATE]')) {
                    isPrivate = true;
                    isGlobal = false;
                    rawMemo = rawMemo.replace(/\[PRIVATE\]/g, '');
                }
                let isDone = false;"
$content = $content.Replace($t4, $r4)

Set-Content -Path "deal-register.html" -Value $content -Encoding UTF8
Write-Output "Done deal-register"


$detailContent = Get-Content -Path "deal-detail.html" -Raw -Encoding UTF8

$t5 = "            let rawMemo = data.memo || '';
            let isDone = false;"
$r5 = "            let rawMemo = data.memo || '';
            if (rawMemo.includes('[PRIVATE]')) {
                rawMemo = rawMemo.replace(/\[PRIVATE\]/g, '');
            }
            let isDone = false;"
$detailContent = $detailContent.Replace($t5, $r5)

Set-Content -Path "deal-detail.html" -Value $detailContent -Encoding UTF8
Write-Output "Done deal-detail"
