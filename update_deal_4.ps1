$content = Get-Content -Path "deal-register.html" -Raw -Encoding UTF8

$t1 = "            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let linkUrl = null;
                let startDt = null;"
$r1 = "            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let isDone = false;
                if (rawMemo.includes('[DONE]')) {
                    isDone = true;
                    rawMemo = rawMemo.replace(/\[DONE\]/g, '');
                }
                let linkUrl = null;
                let startDt = null;"
$content = $content.Replace($t1, $r1)

$t2 = "                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (dDayText) {"
$r2 = "                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (isDone) {
                    dDayHtml = `<span style=`"background: #f3f4f6; color: #9ca3af; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800; border: 1px solid #e5e7eb;`">완료됨</span>`;
                } else if (dDayText) {"
$content = $content.Replace($t2, $r2)

$t3 = "                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isGlobal) {"
$r3 = "                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isDone) {
                    li.style.opacity = '0.5';
                    li.style.backgroundColor = '#f8fafc';
                }
                if (isGlobal) {"
$content = $content.Replace($t3, $r3)

$t4 = "                    li.onclick = () => location.href = 'deal-detail.html?id=' + deal.id;
                    if (isUrgent) {"
$r4 = "                    li.onclick = () => location.href = 'deal-detail.html?id=' + deal.id;
                    if (isUrgent && !isDone) {"
$content = $content.Replace($t4, $r4)

Set-Content -Path "deal-register.html" -Value $content -Encoding UTF8
Write-Output "Done"
