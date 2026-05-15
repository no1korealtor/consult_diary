import os

file_path = 'deal-register.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                if (dDayText) {
                    let badgeBg = '#f3f4f6', badgeColor = '#9ca3af';
                    if (dDayText === 'D-Day') { 
                        badgeBg = '#fee2e2'; badgeColor = '#ef4444'; 
                    } else if (dDayText.startsWith('D-')) { 
                        const daysLeft = parseInt(dDayText.substring(2));
                        if (daysLeft <= 7) {
                            badgeBg = '#dbeafe'; badgeColor = '#2563eb'; 
                        }
                    }
                    dDayHtml = `<span style="background: ${badgeBg}; color: ${badgeColor}; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800;">${dDayText}</span>`;
                }

                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isGlobal) {
                    li.classList.add('global');
                    li.style.cursor = 'default';
                } else {
                    li.style.cursor = 'pointer';
                    li.onclick = () => location.href = 'deal-detail.html?id=' + deal.id;
                }"""

replacement = """                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (dDayText) {
                    let badgeBg = '#f3f4f6', badgeColor = '#9ca3af';
                    if (dDayText === 'D-Day') { 
                        badgeBg = '#fee2e2'; badgeColor = '#ef4444'; 
                        isUrgent = true;
                    } else if (dDayText.startsWith('D-')) { 
                        const daysLeft = parseInt(dDayText.substring(2));
                        if (daysLeft <= 3) {
                            badgeBg = '#ffedd5'; badgeColor = '#ea580c'; 
                            isUrgent = true;
                        } else if (daysLeft <= 7) {
                            badgeBg = '#dbeafe'; badgeColor = '#2563eb'; 
                        }
                    }
                    dDayHtml = `<span style="background: ${badgeBg}; color: ${badgeColor}; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800;">${dDayText}</span>`;
                }

                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isGlobal) {
                    li.classList.add('global');
                    li.style.cursor = 'default';
                } else {
                    li.style.cursor = 'pointer';
                    li.onclick = () => location.href = 'deal-detail.html?id=' + deal.id;
                    if (isUrgent) {
                        li.style.borderColor = '#fda4af';
                        li.style.backgroundColor = '#fff1f2';
                        li.style.boxShadow = '0 4px 12px rgba(244, 63, 94, 0.1)';
                    }
                }"""

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Success")
else:
    print("Target not found")
