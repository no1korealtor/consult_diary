$lines = Get-Content market.html -Encoding UTF8
$newLines = @()

for ($i=0; $i -lt $lines.Length; $i++) {
    $lineNum = $i + 1
    if ($lineNum -eq 902) {
        $newLines += "                    return '<button type=`"button`" onclick=`"showMatchesForProperty(\''' + p.id + '\')`" style=`"width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px dashed #10b981; background: #f0fdf4; color: #16a34a; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);`" onmouseover=`"this.style.background=\'#dcfce7\'`" onmouseout=`"this.style.background=\'#f0fdf4\'`">🤝 매수/임차 희망 손님 (' + matchedClients.length + '명) 보기</button>';"
    } elseif ($lineNum -gt 902 -and $lineNum -le 936) {
        # Skip original matchHtml building logic
    } elseif ($lineNum -eq 1282) {
        $newLines += "                `${matches.length > 0 ? ``"
        $newLines += "                <button type=`"button`" onclick=`"showMatchesForClient('`${c.id}')`" style=`"width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px dashed #3b82f6; background: #eff6ff; color: #2563eb; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);`" onmouseover=`"this.style.background='#dbeafe'`" onmouseout=`"this.style.background='#eff6ff'`">"
        $newLines += "                    🔍 맞춤 매물 찾기 (`${matches.length}건 매칭)"
        $newLines += "                </button>"
        $newLines += "                `` : ``<div style=`"font-size: 12px; color: #94a3b8; margin-top: 12px; text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;`">조건에 딱 맞는 매물이 아직 없습니다.</div>``}"
    } elseif ($lineNum -gt 1282 -and $lineNum -le 1291) {
        # Skip original client match details
    } elseif ($lineNum -eq 2021) {
        # Replace checkAuthAndLoad(); with full JS functions
        $newLines += "    window.showMatchesForClient = function(clientId) {"
        $newLines += "        const c = clientsData.find(x => x.id === clientId);"
        $newLines += "        if (!c) return;"
        $newLines += "        const matches = propertiesData.filter(p => isMatch(p, c));"
        $newLines += "        const title = document.getElementById('matchingModalTitle').querySelector('span');"
        $newLines += "        title.innerText = '🔍 ' + (formatPhoneNumber(c.client_phone) || '이름없음') + '님 맞춤 매물';"
        $newLines += "        const body = document.getElementById('matchingModalBody');"
        $newLines += "        if (matches.length > 0) {"
        $newLines += "            body.innerHTML = matches.map(m => createPropertyCard(m, true, c)).join('');"
        $newLines += "        } else {"
        $newLines += "            body.innerHTML = '<div style=`"text-align: center; color: #94a3b8; margin-top: 20px;`">조건에 맞는 매물이 아직 없습니다.</div>';"
        $newLines += "        }"
        $newLines += "        document.getElementById('matchingModal').style.display = 'flex';"
        $newLines += "    };"
        $newLines += ""
        $newLines += "    window.showMatchesForProperty = function(propertyId) {"
        $newLines += "        const p = propertiesData.find(x => x.id === propertyId);"
        $newLines += "        if (!p) return;"
        $newLines += "        const matchedClients = clientsData.filter(c => isMatch(p, c));"
        $newLines += "        let titleText = '🤝 ';"
        $newLines += "        if (p.address) {"
        $newLines += "            const jibunRegex = /^(.*?)\s*\[지번:\s*(.*?)\]\s*(.*)`$/;"
        $newLines += "            const match = p.address.match(jibunRegex);"
        $newLines += "            titleText += match ? match[2].trim() + ' ' + match[3].trim() : p.address;"
        $newLines += "        } else {"
        $newLines += "            titleText += '매수/임차 희망 손님';"
        $newLines += "        }"
        $newLines += "        const title = document.getElementById('matchingModalTitle').querySelector('span');"
        $newLines += "        title.innerText = titleText;"
        $newLines += "        const body = document.getElementById('matchingModalBody');"
        $newLines += "        if (matchedClients.length > 0) {"
        $newLines += "            let matchHtml = matchedClients.map(c => {"
        $newLines += "                const viewedList = c.viewed_properties || [];"
        $newLines += "                const viewedItem = viewedList.find(v => v.property_id === p.id);"
        $newLines += "                const isViewed = !!viewedItem && !viewedItem.is_rejected;"
        $newLines += "                const isRejected = !!viewedItem && viewedItem.is_rejected;"
        $newLines += "                let cHtml = '<div style=`"display: flex; justify-content: space-between; align-items: center; background: ' + (isViewed ? '#f1f5f9' : '#fff') + '; border: 1px solid ' + (isViewed ? '#cbd5e1' : '#bae6fd') + '; padding: 12px; border-radius: 8px; font-size: 13px; cursor: pointer; transition: 0.2s; ' + (isRejected ? 'opacity: 0.5; text-decoration: line-through;' : '') + '`" onclick=`"document.getElementById(\''matchingModal\'').style.display=\''none\''; switchTab(\''clients\''); setClientFilter(\''탐색중\'', null); setTimeout(() => openClientModal(\''' + c.id + '\''), 100);`">' +"
        $newLines += "                    '<div style=`"display: flex; flex-direction: column; gap: 4px;`">' +"
        $newLines += "                        '<span style=`"font-weight: 800; color: #0f172a; font-size: 14px;`">🧑‍💼 ' + formatPhoneNumber(c.client_phone) + '</span>' +"
        $newLines += "                        '<span style=`"color: #64748b; font-size: 12px; font-weight: 600;`">💰 예산 최대 ' + formatMoney(c.max_budget) + '</span>' +"
        $newLines += "                    '</div>' +"
        $newLines += "                    '<div style=`"display: flex; align-items: center; gap: 8px;`" onclick=`"event.stopPropagation()`">' ;"
        $newLines += "                if (isRejected) {"
        $newLines += "                    cHtml += '<button type=`"button`" onclick=`"undoRejectProperty(\''' + c.id + '\'', \''' + p.id + '\'')`" style=`"font-size: 12px; color: #64748b; font-weight: 700; background: white; border: 1px solid #cbd5e1; padding: 4px 8px; border-radius: 6px; cursor: pointer;`">취소</button>';"
        $newLines += "                    cHtml += '<span style=`"font-size: 12px; color: #ef4444; font-weight: 800; background: #fee2e2; padding: 4px 8px; border-radius: 6px;`">안봄</span>';"
        $newLines += "                } else if (isViewed) {"
        $newLines += "                    cHtml += '<span style=`"font-size: 12px; color: #10b981; font-weight: 800; background: #dcfce7; padding: 4px 8px; border-radius: 6px;`">보여줌</span>';"
        $newLines += "                } else {"
        $newLines += "                    cHtml += '<button type=`"button`" onclick=`"rejectProperty(\''' + c.id + '\'', \''' + p.id + '\'')`" style=`"font-size: 12px; color: #ef4444; font-weight: 700; background: white; border: 1px solid #ef4444; padding: 4px 8px; border-radius: 6px; cursor: pointer;`">거절</button>';"
        $newLines += "                }"
        $newLines += "                cHtml += '</div></div>';"
        $newLines += "                return cHtml;"
        $newLines += "            }).join('');"
        $newLines += "            body.innerHTML = matchHtml;"
        $newLines += "        } else {"
        $newLines += "            body.innerHTML = '<div style=`"text-align: center; color: #94a3b8; margin-top: 20px;`">조건에 딱 맞는 손님이 아직 없습니다.</div>';"
        $newLines += "        }"
        $newLines += "        document.getElementById('matchingModal').style.display = 'flex';"
        $newLines += "    };"
        $newLines += "    checkAuthAndLoad();"
    } elseif ($lineNum -eq 2023) {
        $newLines += "<!-- 매칭 결과 모달 -->"
        $newLines += "<div id=`"matchingModal`" class=`"modal`">"
        $newLines += "    <div class=`"modal-content`" style=`"max-height: 80vh; display: flex; flex-direction: column; width: 90%; max-width: 500px; padding: 20px;`">"
        $newLines += "        <h3 id=`"matchingModalTitle`" style=`"margin-top:0; margin-bottom:12px; color:#1e293b; display: flex; align-items: center; justify-content: space-between;`">"
        $newLines += "            <span style=`"font-size: 18px; font-weight: 800;`">✨ 매칭 결과</span>"
        $newLines += "            <button onclick=`"document.getElementById('matchingModal').style.display='none'`" style=`"background:none; border:none; font-size:24px; cursor:pointer; color:#94a3b8; padding: 0; line-height: 1;`">&times;</button>"
        $newLines += "        </h3>"
        $newLines += "        <div id=`"matchingModalBody`" style=`"flex: 1; overflow-y: auto; padding-right: 4px; margin-top: 4px; display: flex; flex-direction: column; gap: 8px;`">"
        $newLines += "            <!-- 매칭 내용 렌더링 -->"
        $newLines += "        </div>"
        $newLines += "    </div>"
        $newLines += "</div>"
        $newLines += "</body>"
        $newLines += "</html>"
    } elseif ($lineNum -gt 2023) {
        # skip
    } else {
        $newLines += $lines[$i]
    }
}
$newLines | Set-Content market.html -Encoding UTF8
