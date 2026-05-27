$file = "market.html"
$content = Get-Content -Path $file -Raw -Encoding UTF8

# 1. Replace client match details with button
$clientRegex = '(?s)<details class="matching-section" open>\s*<summary[^>]*>.*?✨ 매칭된 매물 \(\$\{matches\.length\}건\).*?</summary>\s*\$\{matches\.length > 0 \? `.*?</div>\s*` : `<div[^>]*>조건에 딱 맞는 매물이 아직 없습니다\.</div>`\}\s*</details>'

$clientBtn = '${matches.length > 0 ? `
<button type="button" onclick="showMatchesForClient(''${c.id}'')" style="width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px dashed #3b82f6; background: #eff6ff; color: #2563eb; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" onmouseover="this.style.background=''#dbeafe''" onmouseout="this.style.background=''#eff6ff''">
    🔍 맞춤 매물 찾기 (${matches.length}건 매칭)
</button>
` : `<div style="font-size: 12px; color: #94a3b8; margin-top: 12px; text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;">조건에 딱 맞는 매물이 아직 없습니다.</div>`}'

$content = [regex]::Replace($content, $clientRegex, $clientBtn)

# 2. Replace property match details with button
$propRegex = '(?s)let matchHtml = ''<details class="matching-section".*?return matchHtml;'

$propBtn = 'return ''<button type="button" onclick="showMatchesForProperty(\'''' + p.id + ''\')" style="width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px dashed #10b981; background: #f0fdf4; color: #16a34a; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" onmouseover="this.style.background=\''#dcfce7\''" onmouseout="this.style.background=\''#f0fdf4\''">🤝 매수/임차 희망 손님 ('' + matchedClients.length + ''명) 보기</button>'';'

$content = [regex]::Replace($content, $propRegex, $propBtn)

# 3. Add modal HTML before </body>
$modalHtml = @"
<!-- 매칭 결과 모달 -->
<div id="matchingModal" class="modal">
    <div class="modal-content" style="max-height: 80vh; display: flex; flex-direction: column; width: 90%; max-width: 500px; padding: 20px;">
        <h3 id="matchingModalTitle" style="margin-top:0; margin-bottom:12px; color:#1e293b; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 18px; font-weight: 800;">✨ 매칭 결과</span>
            <button onclick="document.getElementById('matchingModal').style.display='none'" style="background:none; border:none; font-size:24px; cursor:pointer; color:#94a3b8; padding: 0; line-height: 1;">&times;</button>
        </h3>
        <div id="matchingModalBody" style="flex: 1; overflow-y: auto; padding-right: 4px; margin-top: 4px; display: flex; flex-direction: column; gap: 8px;">
            <!-- 매칭 내용 렌더링 -->
        </div>
    </div>
</div>
</body>
"@

$content = $content -replace '</body>', $modalHtml

Set-Content -Path $file -Value $content -Encoding UTF8
