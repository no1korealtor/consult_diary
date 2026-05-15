import re

with open("admin-tips.html", "r", encoding="utf-8") as f:
    content = f.read()

# Add editingTipId variable and editTip function
script_insert = """
        let allTipsData = [];
        let editingTipId = null;

        function editTip(id) {
            const tip = allTipsData.find(t => t.id === id);
            if(!tip) return;
            
            editingTipId = tip.id;
            document.getElementById('category').value = tip.category || '공통';
            document.getElementById('title').value = tip.title || '';
            document.getElementById('summary1').value = tip.summary && tip.summary.length > 0 ? tip.summary[0] : '';
            document.getElementById('summary2').value = tip.summary && tip.summary.length > 1 ? tip.summary[1] : '';
            document.getElementById('summary3').value = tip.summary && tip.summary.length > 2 ? tip.summary[2] : '';
            document.getElementById('effective_date').value = tip.effective_date || '';
            document.getElementById('warnings').value = tip.warnings || '';
            document.getElementById('full_text').value = tip.full_text || '';
            
            const btn = document.querySelector('.btn-primary');
            btn.innerText = '팁 수정하기';
            btn.style.background = '#4f46e5';
            
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function resetForm() {
            editingTipId = null;
            document.getElementById('category').value = '공통';
            document.getElementById('title').value = '';
            document.getElementById('summary1').value = '';
            document.getElementById('summary2').value = '';
            document.getElementById('summary3').value = '';
            document.getElementById('effective_date').value = '';
            document.getElementById('warnings').value = '';
            document.getElementById('full_text').value = '';
            
            const btn = document.querySelector('.btn-primary');
            btn.innerText = '팁 등록하기';
            btn.style.background = '#3b82f6';
        }
"""
content = re.sub(r"async function loadTips\(\) \{", script_insert + "\n        async function loadTips() {", content, count=1)

# Modify loadTips to store allTipsData and add Edit button
loadTips_replace = """
                allTipsData = data || [];
                allTipsData.forEach(tip => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <div style="flex: 1;">
                            <div style="font-size: 11px; color: #6366f1; font-weight: 800; margin-bottom: 4px;">${tip.category}</div>
                            <div style="font-weight: 700; margin-bottom: 4px;">${tip.title}</div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button onclick="editTip(${tip.id})" style="padding: 6px 10px; background: #f1f5f9; color: #475569; border: none; border-radius: 6px; font-weight: 700; cursor: pointer;">수정</button>
                            <button onclick="deleteTip(${tip.id})" style="padding: 6px 10px; background: #fee2e2; color: #ef4444; border: none; border-radius: 6px; font-weight: 700; cursor: pointer;">삭제</button>
                        </div>
                    `;
                    list.appendChild(li);
                });
"""
content = re.sub(r"data\.forEach\(tip => \{.*?list\.appendChild\(li\);\n                \}\);", loadTips_replace, content, flags=re.DOTALL)

# Modify saveTip to use editingTipId and resetForm
saveTip_replace = """
            if (editingTipId) {
                const { error } = await supabaseClient
                    .from('practical_tips')
                    .update({
                        category, title, summary, effective_date: effectiveDate, warnings, full_text: fullText
                    })
                    .eq('id', editingTipId);
                    
                if (error) {
                    alert('수정 실패: ' + error.message);
                    return;
                }
                alert('팁이 성공적으로 수정되었습니다.');
            } else {
                const { error } = await supabaseClient
                    .from('practical_tips')
                    .insert([{
                        category, title, summary, effective_date: effectiveDate, warnings, full_text: fullText, is_active: true
                    }]);
                    
                if (error) {
                    alert('등록 실패: ' + error.message);
                    return;
                }
                alert('팁이 성공적으로 등록되었습니다.');
            }

            resetForm();
            loadTips();
"""
content = re.sub(r"const \{ error \} = await supabaseClient.*?loadTips\(\);", saveTip_replace, content, flags=re.DOTALL)

with open("admin-tips.html", "w", encoding="utf-8") as f:
    f.write(content)