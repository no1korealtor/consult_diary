import re

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. createPropertyCard signature update
    content = content.replace(
        'function createPropertyCard(p, isMatched = false, client = null) {',
        'function createPropertyCard(p, isMatched = false, client = null, matchedClients = []) {'
    )

    # 2. Add matchedClients HTML block at the end of createPropertyCard
    target_return = "return '';\n            })()\}"
    replacement_return = """return '';
            })()}
            ${(() => {
                if (!isMatched && matchedClients && matchedClients.length > 0) {
                    return `
                    <div class="matching-section" style="margin-top: 12px; border-top: 1px dashed #cbd5e1; padding-top: 12px;">
                        <div style="font-size: 13px; font-weight: 800; color: #10b981; display: flex; align-items: center; gap: 4px; margin-bottom: 8px;">
                            ✨ 조건이 맞는 손님 (${matchedClients.length}명)
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            ${matchedClients.map(c => {
                                const viewedList = c.viewed_properties || [];
                                const viewedItem = viewedList.find(v => v.property_id === p.id);
                                const isViewed = !!viewedItem;
                                
                                return `
                                <div style="display: flex; justify-content: space-between; align-items: center; background: ${isViewed ? '#f1f5f9' : '#fff'}; border: 1px solid ${isViewed ? '#cbd5e1' : '#bae6fd'}; padding: 8px 10px; border-radius: 8px; font-size: 13px; cursor: pointer; transition: 0.2s;" onmousedown="this.style.opacity='0.7'" onmouseup="this.style.opacity='1'" onclick="switchTab('clients'); setClientFilter('탐색중', null); setTimeout(() => openClientModal('${c.id}'), 100);">
                                    <div>
                                        <span style="font-weight: 800; color: #0f172a;">🧑‍💼 ${formatPhoneNumber(c.client_phone)}</span>
                                        <span style="color: #64748b; margin-left: 4px; font-size: 12px; font-weight: 600;">최대 ${formatMoney(c.max_budget)}</span>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 8px;" onclick="event.stopPropagation()">
                                        ${isViewed ? `<span style="font-size: 11px; color: #10b981; font-weight: 800; background: #dcfce7; padding: 2px 6px; border-radius: 4px;">✅ 보여줌</span>` : ''}
                                        <button onclick="copyClientToKakao('${c.id}', this)" style="background: #fee500; color: #371d1e; border: none; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 11px; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">💬 카톡</button>
                                    </div>
                                </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                    `;
                }
                return '';
            })()}"""
    
    content = content.replace(target_return, replacement_return)

    # 3. Add isMatch function before renderProperties
    is_match_func = """    function isMatch(p, c) {
        if (p.status !== '거래가능') return false;
        if (c.status !== '탐색중') return false;
        
        if (!p.deal_types || !Array.isArray(p.deal_types)) return false;
        if (!c.target_types || !Array.isArray(c.target_types)) return false;
        
        const typeMatch = p.deal_types.some(pt => c.target_types.includes(pt));
        if (!typeMatch) return false;
        
        let isBudgetOk = false;
        const pSale = p.sale_price || 0;
        const pDep = p.deposit || 0;
        const pRent = p.monthly_rent || 0;
        
        const cBudget = c.max_budget || 9999999;
        const flexRent = c.max_monthly ? c.max_monthly + 10 : 9999999;
        
        if (c.target_types.includes('매매') && p.deal_types.includes('매매')) {
            if (pSale > 0 && pSale <= cBudget) isBudgetOk = true;
        }
        if (c.target_types.includes('전세') && p.deal_types.includes('전세')) {
            if (pDep > 0 && pRent === 0 && pDep <= cBudget) isBudgetOk = true;
        }
        if (c.target_types.includes('월세') && p.deal_types.includes('월세')) {
            if (pDep <= cBudget && pRent > 0 && pRent <= flexRent) isBudgetOk = true;
        }
        
        if (!isBudgetOk) return false;

        // 방 개수가 안 적혀있으면 통과, 적혀있더라도 실무 호환성을 위해 1개 차이(-1)까지는 매칭 허용
        if (c.min_room_count && p.room_count && p.room_count < c.min_room_count - 1) return false;
        if (c.need_pet && !p.pet_allowed) return false;
        if (c.need_parking && !p.parking_allowed) return false;
        if (c.need_loan && !p.loan_allowed) return false;
        if (c.need_lh_sh && !p.lh_sh_allowed) return false;
        if (c.need_exclude_basement && p.is_basement) return false;
        
        if (p.occupancy_type === '입주불가(세안고)' && c.occupancy_type !== '무관') return false;
        
        return true;
    }

    function renderProperties() {"""
    content = content.replace('    function renderProperties() {', is_match_func)

    # 4. Use isMatch inside renderClients
    client_match_logic = """            // Find matches
            const matches = propertiesData.filter(p => isMatch(p, c));"""
    
    # We replace the entire old filter logic in renderClients
    old_filter_pattern = re.compile(r'// Find matches\s*const matches = propertiesData\.filter\(p => \{.*?(?=\s*// 상태 뱃지 동적 생성)', re.DOTALL)
    content = old_filter_pattern.sub(client_match_logic + '\n\n', content)

    # 5. Provide matchedClients array to createPropertyCard in renderProperties
    render_prop_logic = """        filteredData.forEach(p => {
            const matchedClients = (p.status === '거래가능') ? clientsData.filter(c => isMatch(p, c)) : [];
            html += createPropertyCard(p, false, null, matchedClients);
        });"""
    content = content.replace("""        filteredData.forEach(p => {
            html += createPropertyCard(p, false);
        });""", render_prop_logic)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('market.html')
