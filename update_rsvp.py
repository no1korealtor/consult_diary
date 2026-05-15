import re

with open('deal-register.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add window.setAttendance before getDDay
content = content.replace(
    'function getDDay(dateString) {',
    '''window.setAttendance = async function(dealId, status) {
            const { error } = await supabaseClient
                .from('deal_attendances')
                .upsert({ deal_id: dealId, user_id: window.currentUser.id, status: status }, { onConflict: 'deal_id,user_id' });
            if (error) {
                alert('투표 저장에 실패했습니다: ' + error.message);
                return;
            }
            loadDeals();
        };

        function getDDay(dateString) {'''
)

# Update the rendering logic
target = '''                const isMeetingTag = mTime || mLoc || mAtt;
                if (deal.contract_type === '모임' || (isGlobal && isMeetingTag)) {
                    const timeStr = mTime ? ${mTime} : '';
                    let locStr = '';
                    if (mLoc) {
                        locStr = <span onclick="window.open('https://map.kakao.com/link/search/', '_blank'); event.stopPropagation();" style="color: #2563eb; cursor: pointer; text-decoration: underline;"></span>;
                    }
                    
                    let details = [timeStr, locStr].filter(Boolean).join(' · ');
                    if(details) details = <div style="font-size:13px; color:#6b7280; margin-top:4px;"></div>;
                    
                    let attBadge = '';
                    if(mAtt === '참석') attBadge = <span style="color:#16a34a; font-size:12px; font-weight:800;">[참석]</span>;
                    else if(mAtt === '미정') attBadge = <span style="color:#d97706; font-size:12px; font-weight:800;">[미정]</span>;
                    else if(mAtt === '불참') attBadge = <span style="color:#dc2626; font-size:12px; font-weight:800;">[불참]</span>;

                    const meetName = rawMemo.trim() || '모임 일정';
                    locationHtml = <div style="color: #111827; font-size: 16px; font-weight: 800; line-height: 1.4; margin-bottom: 2px;"> </div>;
                    typeBadgeHtml = <span style="background: #fdf4ff; color: #c026d3; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800;"></span>;
                    rawMemo = ''; // Hide memo
                } else if (isGlobal) {'''

replacement = '''                const isMeetingTag = mTime || mLoc || mAtt;
                if (deal.contract_type === '모임' || (isGlobal && isMeetingTag)) {
                    
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

                    if (isGlobal && myAtt) {
                        mAtt = myAtt; // 내 상태로 뱃지 덮어쓰기
                    }

                    const timeStr = mTime ? ${mTime} : '';
                    let locStr = '';
                    if (mLoc) {
                        locStr = <span onclick="window.open('https://map.kakao.com/link/search/', '_blank'); event.stopPropagation();" style="color: #2563eb; cursor: pointer; text-decoration: underline;"></span>;
                    }
                    
                    let details = [timeStr, locStr].filter(Boolean).join(' · ');
                    if(details) details = <div style="font-size:13px; color:#6b7280; margin-top:4px;"></div>;
                    
                    if (isGlobal) {
                        details += 
                        <div style="display: flex; gap: 8px; margin-top: 12px; background: #f8fafc; padding: 12px; border-radius: 12px; border: 1px solid #e2e8f0;" onclick="event.stopPropagation()">
                            <button type="button" onclick="setAttendance('', '참석')" style="flex: 1; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; transition: 0.2s; border: 1px solid ; background: ; color: ; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">👍 참석 ()</button>
                            <button type="button" onclick="setAttendance('', '불참')" style="flex: 1; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; transition: 0.2s; border: 1px solid ; background: ; color: ; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">✋ 불참 ()</button>
                        </div>
                        ;
                    }

                    let attBadge = '';
                    if(mAtt === '참석') attBadge = <span style="color:#16a34a; font-size:12px; font-weight:800;">[참석]</span>;
                    else if(mAtt === '미정') attBadge = <span style="color:#d97706; font-size:12px; font-weight:800;">[미정]</span>;
                    else if(mAtt === '불참') attBadge = <span style="color:#dc2626; font-size:12px; font-weight:800;">[불참]</span>;

                    const meetName = rawMemo.trim() || '모임 일정';
                    locationHtml = <div style="color: #111827; font-size: 16px; font-weight: 800; line-height: 1.4; margin-bottom: 2px;"> </div>;
                    typeBadgeHtml = <span style="background: #fdf4ff; color: #c026d3; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800;"></span>;
                    rawMemo = ''; // Hide memo
                } else if (isGlobal) {'''

# Windows uses CRLF, python might have loaded as LF. 
# Re-normalize to match.
target_norm = target.replace('\r\n', '\n')
content_norm = content.replace('\r\n', '\n')

content_norm = content_norm.replace(target_norm, replacement)

with open('deal-register.html', 'w', encoding='utf-8') as f:
    f.write(content_norm)