with open('deal-register.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = "const isMeetingTag = mTime || mLoc || mAtt;"
replacement = """const isMeetingTag = mTime || mLoc || mAtt;
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
                    if (isGlobal && myAtt) mAtt = myAtt;"""

content = content.replace("const isMeetingTag = mTime || mLoc || mAtt;\n                if (deal.contract_type === '모임' || (isGlobal && isMeetingTag)) {", replacement)

target2 = "let attBadge = '';"
replacement2 = """if (isGlobal) {
                        details += <div style="display: flex; gap: 8px; margin-top: 12px; background: #f8fafc; padding: 12px; border-radius: 12px; border: 1px solid #e2e8f0;" onclick="event.stopPropagation()">
                            <button type="button" onclick="setAttendance('', '참석')" style="flex: 1; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; transition: 0.2s; border: 1px solid ; background: ; color: ; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">👍 참석 ()</button>
                            <button type="button" onclick="setAttendance('', '불참')" style="flex: 1; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; transition: 0.2s; border: 1px solid ; background: ; color: ; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">✋ 불참 ()</button>
                        </div>;
                    }
                    let attBadge = '';"""

content = content.replace("let attBadge = '';", replacement2)

with open('deal-register.html', 'w', encoding='utf-8') as f:
    f.write(content)