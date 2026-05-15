import re

with open("deal-register.html", "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"if \(deal\.contract_type === '모임' \|\| \(isGlobal && isMeetingTag\)\) \{.*?\} else if \(isGlobal\) \{"
replacement = """if (deal.contract_type === '모임' || (isGlobal && isMeetingTag)) {
                    const timeStr = mTime ? `${mTime}` : '';
                    let locStr = '';
                    if (mLoc) {
                        locStr = `<span onclick="window.open('https://map.kakao.com/link/search/${encodeURIComponent(mLoc)}', '_blank'); event.stopPropagation();" style="color: #475569; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 2px;">📍 ${mLoc}</span>`;
                    }
                    
                    let details = '';
                    if (timeStr || locStr) {
                        details = `<div style="font-size: 13px; margin-top: 8px; display: inline-flex; gap: 8px; align-items: center; background: #f8fafc; padding: 6px 12px; border-radius: 8px; border: 1px solid #f1f5f9;">`;
                        if (timeStr) details += `<span style="color: #1e293b; font-weight: 800;">🕒 ${timeStr}</span>`;
                        if (timeStr && locStr) details += `<span style="color: #cbd5e1;">|</span>`;
                        if (locStr) details += `${locStr}`;
                        details += `</div>`;
                    }

                    let myAtt = null;
                    let attCount = 0;
                    let noCount = 0;
                    if (deal.deal_attendances) {
                        const attendances = deal.deal_attendances;
                        const myRec = attendances.find(a => a.user_id === window.currentUser.id);
                        if (myRec) myAtt = myRec.status;
                        attCount = attendances.filter(a => a.status === '참석').length;
                        noCount = attendances.filter(a => a.status === '불참').length;
                    }

                    if (isGlobal && myAtt) mAtt = myAtt;
                    
                    if (isGlobal) {
                        details += `
                        <div style="display: flex; gap: 10px; margin-top: 16px;" onclick="event.stopPropagation()">
                            <button type="button" onclick="setAttendance('${deal.id}', '참석')" style="flex: 1; padding: 14px; border-radius: 16px; font-weight: 800; font-size: 15px; cursor: pointer; transition: 0.2s; border: none; background: ${myAtt === '참석' ? '#4f46e5' : '#f1f5f9'}; color: ${myAtt === '참석' ? 'white' : '#64748b'};">👍 참석 ${attCount > 0 ? `<span style="opacity: 0.8; font-weight: 600; font-size: 13px; margin-left: 2px;">${attCount}</span>` : ''}</button>
                            <button type="button" onclick="setAttendance('${deal.id}', '불참')" style="flex: 1; padding: 14px; border-radius: 16px; font-weight: 800; font-size: 15px; cursor: pointer; transition: 0.2s; border: none; background: ${myAtt === '불참' ? '#e2e8f0' : '#f8fafc'}; color: ${myAtt === '불참' ? '#475569' : '#94a3b8'};">✋ 불참 ${noCount > 0 ? `<span style="opacity: 0.8; font-weight: 600; font-size: 13px; margin-left: 2px;">${noCount}</span>` : ''}</button>
                        </div>
                        `;
                    }

                    let attBadge = '';
                    if(mAtt === '참석') attBadge = `<span style="color:#4f46e5; font-size:13px; font-weight:800; margin-left: 6px;">[참석]</span>`;
                    else if(mAtt === '불참') attBadge = `<span style="color:#64748b; font-size:13px; font-weight:800; margin-left: 6px;">[불참]</span>`;
                    else if(mAtt === '미정') attBadge = `<span style="color:#94a3b8; font-size:13px; font-weight:800; margin-left: 6px;">[미정]</span>`;

                    const meetName = rawMemo.trim() || '이름 없음';
                    locationHtml = `<div style="color: #0f172a; font-size: 18px; font-weight: 900; line-height: 1.4; margin-bottom: 2px; letter-spacing: -0.5px;">${meetName}${attBadge}</div>${details}`;
                    typeBadgeHtml = `<span style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800;">공지</span>`;
                    rawMemo = ''; // Hide memo
                } else if (isGlobal) {"""
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("deal-register.html", "w", encoding="utf-8") as f:
    f.write(content)