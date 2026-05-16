const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, 'deal-register.html');
let content = fs.readFileSync(filePath, 'utf8');

const target1 = `            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let linkUrl = null;`;
const rep1 = `            const createDealListItem = (deal, isGlobal) => {
                let rawMemo = deal.memo || '';
                let isDone = false;
                if (rawMemo.includes('[DONE]')) {
                    isDone = true;
                    rawMemo = rawMemo.replace(/\\[DONE\\]/g, '');
                }
                
                let linkUrl = null;`;

if (content.includes(target1)) content = content.replace(target1, rep1);
else console.log('target1 not found');

const target2 = `                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (dDayText) {`;
const rep2 = `                const dDayText = getDDay(deal.balance_date);
                let dDayHtml = '';
                let isUrgent = false;
                if (isDone) {
                    dDayHtml = \`<span style="background: #f3f4f6; color: #9ca3af; padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: 800; border: 1px solid #e5e7eb;">완료됨</span>\`;
                } else if (dDayText) {`;

if (content.includes(target2)) content = content.replace(target2, rep2);
else console.log('target2 not found');

const target3 = `                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isGlobal) {`;
const rep3 = `                const li = document.createElement('li');
                li.className = 'deal-item';
                if (isDone) {
                    li.style.opacity = '0.6';
                    li.style.backgroundColor = '#f9fafb';
                }
                if (isGlobal) {`;

if (content.includes(target3)) content = content.replace(target3, rep3);
else console.log('target3 not found');

const target4 = `                    if (isUrgent) {
                        li.style.borderColor = '#fda4af';`;
const rep4 = `                    if (isUrgent && !isDone) {
                        li.style.borderColor = '#fda4af';`;

if (content.includes(target4)) content = content.replace(target4, rep4);
else console.log('target4 not found');

fs.writeFileSync(filePath, content, 'utf8');
console.log('Done JS!');
