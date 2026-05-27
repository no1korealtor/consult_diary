$c = Get-Content market.html -Raw -Encoding UTF8
$c = $c.Replace("\\'", "\'")

# Fix duplicate modals by finding the first occurrence of the modal and cutting off the rest, then appending a single modal
$modalStart = $c.IndexOf("<!-- 매칭 결과 모달 -->")
if ($modalStart -gt 0) {
    $c = $c.Substring(0, $modalStart)
    $c += "<!-- 매칭 결과 모달 -->`n"
    $c += "<div id=`"matchingModal`" class=`"modal`">`n"
    $c += "    <div class=`"modal-content`" style=`"max-height: 80vh; display: flex; flex-direction: column; width: 90%; max-width: 500px; padding: 20px;`">`n"
    $c += "        <h3 id=`"matchingModalTitle`" style=`"margin-top:0; margin-bottom:12px; color:#1e293b; display: flex; align-items: center; justify-content: space-between;`">`n"
    $c += "            <span style=`"font-size: 18px; font-weight: 800;`">✨ 매칭 결과</span>`n"
    $c += "            <button onclick=`"document.getElementById('matchingModal').style.display='none'`" style=`"background:none; border:none; font-size:24px; cursor:pointer; color:#94a3b8; padding: 0; line-height: 1;`">&times;</button>`n"
    $c += "        </h3>`n"
    $c += "        <div id=`"matchingModalBody`" style=`"flex: 1; overflow-y: auto; padding-right: 4px; margin-top: 4px; display: flex; flex-direction: column; gap: 8px;`">`n"
    $c += "            <!-- 매칭 내용 렌더링 -->`n"
    $c += "        </div>`n"
    $c += "    </div>`n"
    $c += "</div>`n`n"
    $c += "</body>`n</html>`n"
}

$c | Set-Content market.html -Encoding UTF8
