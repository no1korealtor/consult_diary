import re

with open("deal-register.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the locationHtml generation for meeting
pattern = r"\} else if \(isGlobal && isMeetingTag\) \{.*?else if \(isGlobal\) \{"
replacement = """} else if (isGlobal && isMeetingTag) {
                    const timeStr = mTime ? `${mTime}` : '';
                    let locStr = '';
                    if (mLoc) {
                        if (mLoc.includes('http')) locStr = `<a href="${mLoc}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 700;" onclick="event.stopPropagation()">🔗 링크 열기</a>`;
                        else locStr = `<span style="color: #64748b; font-weight: 600;">📍 ${mLoc}</span>`;
                    }
                    
                    let details = '';
                    if (timeStr || locStr) {
                        details = `<div style="font-size: 13px; margin-top: 6px; display: flex; gap: 6px; align-items: center; background: #f8fafc; padding: 6px 10px; border-radius: 8px; border: 1px solid #f1f5f9; width: fit-content;">`;
                        if (timeStr) details += `<span style="color: #1e293b; font-weight: 700;">🕒 ${timeStr}</span>`;
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

                    if (isGlobal && myAtt) mAtt = myAtt; // 내 상태로 덮어쓰기
                    
                    if (isGlobal) {
                        details += `
                        <div style="display: flex; gap: 8px; margin-top: 14px;" onclick="event.stopPropagation()">
                            <button type="button" onclick="setAttendance('${deal.id}', '참석')" style="flex: 1; padding: 12px; border-radius: 12px; font-weight: 800; font-size: 14px; cursor: pointer; transition: 0.2s; border: none; background: ${myAtt === '참석' ? '#4f46e5' : '#f1f5f9'}; color: ${myAtt === '참석' ? 'white' : '#64748b'};">👍 참석 ${attCount > 0 ? `<span style="opacity: 0.8; font-weight: 600; font-size: 12px; margin-left: 2px;">${attCount}</span>` : ''}</button>
                            <button type="button" onclick="setAttendance('${deal.id}', '불참')" style="flex: 1; padding: 12px; border-radius: 12px; font-weight: 800; font-size: 14px; cursor: pointer; transition: 0.2s; border: none; background: ${myAtt === '불참' ? '#e2e8f0' : '#f8fafc'}; color: ${myAtt === '불참' ? '#475569' : '#94a3b8'};">✋ 불참 ${noCount > 0 ? `<span style="opacity: 0.8; font-weight: 600; font-size: 12px; margin-left: 2px;">${noCount}</span>` : ''}</button>
                        </div>
                        `;
                    }

                    let attBadge = '';
                    if(mAtt === '참석') attBadge = `<span style="color:#4f46e5; font-size:12px; font-weight:800; margin-left: 4px;">[참석]</span>`;
                    else if(mAtt === '불참') attBadge = `<span style="color:#64748b; font-size:12px; font-weight:800; margin-left: 4px;">[불참]</span>`;
                    else if(mAtt === '미정') attBadge = `<span style="color:#94a3b8; font-size:12px; font-weight:800; margin-left: 4px;">[미정]</span>`;

                    const meetName = rawMemo.trim() || '이름 없음';
                    locationHtml = `<div style="color: #0f172a; font-size: 17px; font-weight: 800; line-height: 1.4; margin-bottom: 4px; letter-spacing: -0.5px;">${meetName}${attBadge}</div>${details}`;
                    typeBadgeHtml = `<span style="background: rgba(139, 92, 246, 0.1); color: #8b5cf6; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 800;">공지</span>`;
                    rawMemo = ''; // Hide memo
                } else if (isGlobal) {"""
content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Fix the date box
date_pattern = r"<div style=\"flex-shrink: 0; width: 64px; display: flex; flex-direction: column; align-items: \ncenter; justify-content: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 0;\">"
date_repl = "<div style=\"flex-shrink: 0; width: 56px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding-top: 4px;\">"
content = content.replace(date_pattern, date_repl)
content = content.replace("<div style=\"flex-shrink: 0; width: 64px; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 0;\">", date_repl)

# Fix link URL box
link_pattern = r"memoHtml \+\= `<div onclick=\"window\.open\('\$\{linkUrl\}', '_blank'\); event\.stopPropagation\(\);\" style=\"\nmargin-top: 8px; font-size: 12px; color: #3b82f6; font-weight: 700; display: inline-flex; align-items: center; gap: 4px\n; cursor: pointer; padding: 6px 10px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe;\">\$\{linkName\}<\n/div>`;"
link_repl = "memoHtml += `<div onclick=\"window.open('${linkUrl}', '_blank'); event.stopPropagation();\" style=\"margin-top: 12px; font-size: 13px; color: #475569; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; cursor: pointer; padding: 8px 12px; background: #f1f5f9; border-radius: 8px; transition: 0.2s;\">🔗 ${linkName}</div>`;"
content = re.sub(link_pattern, link_repl, content, flags=re.DOTALL)

with open("deal-register.html", "w", encoding="utf-8") as f:
    f.write(content)