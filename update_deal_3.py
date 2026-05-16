import sys

file_path = 'd:\\부동산업무\\antigravity\\consult_diary\\deal-register.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = '''            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let linkUrl = null;'''
rep1 = '''            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let isDone = false;
                if (rawMemo.includes('[DONE]')) {
                    isDone = true;
                    rawMemo = rawMemo.replace(/\\[DONE\\]/g, '');
                }
                
                let linkUrl = null;'''
if target1 in content:
    content = content.replace(target1, rep1)

target2 = '''                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (dDayText) {'''
rep2 = '''                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (isDone) {
                    dDayHtml = `<span style="background: #f3f4f6; color: #9ca3af; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800; border: 1px solid #e5e7eb;">완료됨</span>`;
                } else if (dDayText) {'''
if target2 in content:
    content = content.replace(target2, rep2)

target3 = '''                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isGlobal) {'''
rep3 = '''                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isDone) {
                    li.style.opacity = '0.6';
                    li.style.backgroundColor = '#f9fafb';
                }
                if (isGlobal) {'''
if target3 in content:
    content = content.replace(target3, rep3)

target4 = '''                    if (isUrgent) {
                        li.style.borderColor = '#fda4af';'''
rep4 = '''                    if (isUrgent && !isDone) {
                        li.style.borderColor = '#fda4af';'''
if target4 in content:
    content = content.replace(target4, rep4)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
