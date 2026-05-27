import os

with open('market.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Client Match Block Replacement
client_target = """                <details class="matching-section" open>
                    <summary style="font-size: 13px; font-weight: 800; color: #3b82f6; display: flex; align-items: center; gap: 4px; cursor: pointer; outline: none; margin-bottom: 8px;">
                        ✨ 매칭된 매물 (${matches.length}건)
                    </summary>
                    ${matches.length > 0 ? `
                        <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 6px;">
                            ${matches.map(m => createPropertyCard(m, true, c)).join('')}
                        </div>
                    ` : `<div style="font-size: 12px; color: #94a3b8; margin-top: 8px;">조건에 딱 맞는 매물이 아직 없습니다.</div>`}
                </details>"""

client_replacement = """                ${matches.length > 0 ? `
                <button type="button" onclick="showMatchesForClient('${c.id}')" style="width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px dashed #3b82f6; background: #eff6ff; color: #2563eb; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" onmouseover="this.style.background='#dbeafe'" onmouseout="this.style.background='#eff6ff'">
                    🔍 맞춤 매물 찾기 (${matches.length}건 매칭)
                </button>
                ` : `<div style="font-size: 12px; color: #94a3b8; margin-top: 12px; text-align: center; padding: 10px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;">조건에 딱 맞는 매물이 아직 없습니다.</div>`}"""

content = content.replace(client_target, client_replacement)


# 2. Property Match Block Replacement
prop_target = """                    let matchHtml = '<details class="matching-section" style="margin-top: 12px; border-top: 1px dashed #cbd5e1; padding-top: 12px;" open>' +
                        '<summary style="font-size: 13px; font-weight: 800; color: #10b981; display: flex; align-items: center; gap: 4px; margin-bottom: 8px; cursor: pointer; outline: none;">' +
                            '✨ 매칭 및 보여준 손님 (' + matchedClients.length + '명)' +
                        '</summary>' +
                        '<div style="display: flex; flex-direction: column; gap: 6px;">';
                        
                    matchHtml += matchedClients.map(c => {
                        const viewedList = c.viewed_properties || [];
                        const viewedItem = viewedList.find(v => v.property_id === p.id);
                        const isViewed = !!viewedItem && !viewedItem.is_rejected;
                        const isRejected = !!viewedItem && viewedItem.is_rejected;
                        
                        let cHtml = '<div style="display: flex; justify-content: space-between; align-items: center; background: ' + (isViewed ? '#f1f5f9' : '#fff') + '; border: 1px solid ' + (isViewed ? '#cbd5e1' : '#bae6fd') + '; padding: 8px 10px; border-radius: 8px; font-size: 13px; cursor: pointer; transition: 0.2s; ' + (isRejected ? 'opacity: 0.5; text-decoration: line-through;' : '') + '" onmousedown="this.style.opacity=\\'0.7\\'" onmouseup="this.style.opacity=\\'1\\'" onclick="switchTab(\\'clients\\'); setClientFilter(\\'탐색중\\', null); setTimeout(() => openClientModal(\\'' + c.id + '\\'), 100);">' +
                            '<div>' +
                                '<span style="font-weight: 800; color: #0f172a;">🧑‍💼 ' + formatPhoneNumber(c.client_phone) + '</span>' +
                                '<span style="color: #64748b; margin-left: 4px; font-size: 12px; font-weight: 600;">최대 ' + formatMoney(c.max_budget) + '</span>' +
                            '</div>' +
                            '<div style="display: flex; align-items: center; gap: 8px;" onclick="event.stopPropagation()">';
                        
                        if (isRejected) {
                            cHtml += '<button type="button" onclick="undoRejectProperty(\\'' + c.id + '\\', \\'' + p.id + '\\')" style="font-size: 11px; color: #64748b; font-weight: 700; background: white; border: 1px solid #cbd5e1; padding: 2px 6px; border-radius: 4px; cursor: pointer;">취소</button>';
                            cHtml += '<span style="font-size: 11px; color: #ef4444; font-weight: 800; background: #fee2e2; padding: 2px 6px; border-radius: 4px;">안봄</span>';
                        } else if (isViewed) {
                            cHtml += '<span style="font-size: 11px; color: #10b981; font-weight: 800; background: #dcfce7; padding: 2px 6px; border-radius: 4px;">보여줌</span>';
                        } else {
                            cHtml += '<button type="button" onclick="rejectProperty(\\'' + c.id + '\\', \\'' + p.id + '\\')" style="font-size: 11px; color: #ef4444; font-weight: 700; background: white; border: 1px solid #ef4444; padding: 2px 6px; border-radius: 4px; cursor: pointer;">거절</button>';
                        }

                        cHtml += '</div></div>';
                        return cHtml;
                    }).join('');
                    
                    matchHtml += '</div></details>';
                    return matchHtml;"""

prop_replacement = """                    return '<button type="button" onclick="showMatchesForProperty(\\'' + p.id + '\\')" style="width: 100%; margin-top: 12px; padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 800; border: 1px dashed #10b981; background: #f0fdf4; color: #16a34a; cursor: pointer; transition: 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" onmouseover="this.style.background=\\'#dcfce7\\'" onmouseout="this.style.background=\\'#f0fdf4\\'">🤝 매수/임차 희망 손님 (' + matchedClients.length + '명) 보기</button>';"""

content = content.replace(prop_target, prop_replacement)

# 3. Add JS Functions
js_functions = """    window.showMatchesForClient = function(clientId) {
        const c = clientsData.find(x => x.id === clientId);
        if (!c) return;
        
        const matches = propertiesData.filter(p => isMatch(p, c));
        const title = document.getElementById('matchingModalTitle').querySelector('span');
        title.innerText = '🔍 ' + (formatPhoneNumber(c.client_phone) || '이름없음') + '님 맞춤 매물';
        
        const body = document.getElementById('matchingModalBody');
        if (matches.length > 0) {
            body.innerHTML = matches.map(m => createPropertyCard(m, true, c)).join('');
        } else {
            body.innerHTML = '<div style="text-align: center; color: #94a3b8; margin-top: 20px;">조건에 맞는 매물이 아직 없습니다.</div>';
        }
        
        document.getElementById('matchingModal').style.display = 'flex';
    };

    window.showMatchesForProperty = function(propertyId) {
        const p = propertiesData.find(x => x.id === propertyId);
        if (!p) return;
        
        const matchedClients = clientsData.filter(c => isMatch(p, c));
        
        let titleText = '🤝 ';
        if (p.address) {
            const jibunRegex = /^(.*?)\\s*\\[지번:\\s*(.*?)\\]\\s*(.*)$/;
            const match = p.address.match(jibunRegex);
            titleText += match ? match[2].trim() + ' ' + match[3].trim() : p.address;
        } else {
            titleText += '매수/임차 희망 손님';
        }
        
        const title = document.getElementById('matchingModalTitle').querySelector('span');
        title.innerText = titleText;
        
        const body = document.getElementById('matchingModalBody');
        if (matchedClients.length > 0) {
            let matchHtml = matchedClients.map(c => {
                const viewedList = c.viewed_properties || [];
                const viewedItem = viewedList.find(v => v.property_id === p.id);
                const isViewed = !!viewedItem && !viewedItem.is_rejected;
                const isRejected = !!viewedItem && viewedItem.is_rejected;
                
                let cHtml = '<div style="display: flex; justify-content: space-between; align-items: center; background: ' + (isViewed ? '#f1f5f9' : '#fff') + '; border: 1px solid ' + (isViewed ? '#cbd5e1' : '#bae6fd') + '; padding: 12px; border-radius: 8px; font-size: 13px; cursor: pointer; transition: 0.2s; ' + (isRejected ? 'opacity: 0.5; text-decoration: line-through;' : '') + '" onclick="document.getElementById(\\'matchingModal\\').style.display=\\'none\\'; switchTab(\\'clients\\'); setClientFilter(\\'탐색중\\', null); setTimeout(() => openClientModal(\\'' + c.id + '\\'), 100);">' +
                    '<div style="display: flex; flex-direction: column; gap: 4px;">' +
                        '<span style="font-weight: 800; color: #0f172a; font-size: 14px;">🧑‍💼 ' + formatPhoneNumber(c.client_phone) + '</span>' +
                        '<span style="color: #64748b; font-size: 12px; font-weight: 600;">💰 예산 최대 ' + formatMoney(c.max_budget) + '</span>' +
                    '</div>' +
                    '<div style="display: flex; align-items: center; gap: 8px;" onclick="event.stopPropagation()">';
                
                if (isRejected) {
                    cHtml += '<button type="button" onclick="undoRejectProperty(\\'' + c.id + '\\', \\'' + p.id + '\\')" style="font-size: 12px; color: #64748b; font-weight: 700; background: white; border: 1px solid #cbd5e1; padding: 4px 8px; border-radius: 6px; cursor: pointer;">취소</button>';
                    cHtml += '<span style="font-size: 12px; color: #ef4444; font-weight: 800; background: #fee2e2; padding: 4px 8px; border-radius: 6px;">안봄</span>';
                } else if (isViewed) {
                    cHtml += '<span style="font-size: 12px; color: #10b981; font-weight: 800; background: #dcfce7; padding: 4px 8px; border-radius: 6px;">보여줌</span>';
                } else {
                    cHtml += '<button type="button" onclick="rejectProperty(\\'' + c.id + '\\', \\'' + p.id + '\\')" style="font-size: 12px; color: #ef4444; font-weight: 700; background: white; border: 1px solid #ef4444; padding: 4px 8px; border-radius: 6px; cursor: pointer;">거절</button>';
                }
                cHtml += '</div></div>';
                return cHtml;
            }).join('');
            body.innerHTML = matchHtml;
        } else {
            body.innerHTML = '<div style="text-align: center; color: #94a3b8; margin-top: 20px;">조건에 딱 맞는 손님이 아직 없습니다.</div>';
        }
        
        document.getElementById('matchingModal').style.display = 'flex';
    };

    checkAuthAndLoad();"""

content = content.replace('    checkAuthAndLoad();', js_functions)

# 4. Add Modal HTML
modal_html = """<!-- 매칭 결과 모달 -->
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
</html>"""

content = content.replace('</body>\n</html>', modal_html)

with open('market.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
