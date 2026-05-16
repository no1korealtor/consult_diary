import re

with open("deal-register.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update tipBanner to have explicit buttons
banner_pattern = r'<div id="tipBanner" style="display: none; background: linear-gradient\(135deg, #1e293b, #0f172a\);.*?</div>\s*</div>\s*</div>'
new_banner = """<div id="tipBanner" style="display: none; background: linear-gradient(135deg, #1e293b, #0f172a); color: white; border-radius: 16px; padding: 20px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <div onclick="openTipSheet()" style="cursor: pointer;">
        <div style="font-size: 12px; color: #94a3b8; font-weight: 700; margin-bottom: 8px; display: flex; align-items: center; gap: 6px;">
            <span>💡 새로운 실무 팁</span>
            <span id="tipBannerCategory" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 2px 6px; border-radius: 4px; font-size: 10px;">일반</span>
        </div>
        <div id="tipBannerTitle" style="font-size: 16px; font-weight: 800; color: #f8fafc; word-break: keep-all; line-height: 1.4;">-</div>
    </div>
    <div style="display: flex; gap: 8px; margin-top: 16px;">
        <button type="button" onclick="saveCurrentTip(event)" style="flex: 1; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 14px; cursor: pointer; border: none; background: #3b82f6; color: white; box-shadow: 0 2px 4px rgba(59,130,246,0.3);">⭐ 보관하기</button>
        <button type="button" onclick="hideCurrentTip(event)" style="flex: 1; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 14px; cursor: pointer; border: none; background: rgba(255,255,255,0.1); color: #cbd5e1;">✕ 이제 안보기</button>
    </div>
</div>"""
content = re.sub(banner_pattern, new_banner, content, flags=re.DOTALL)

# 2. Update renderTips to add buttons
render_pattern = r'function renderTips\(\) \{.*?container\.innerHTML = \'\';.*?practicalTips\.forEach\(tip => \{.*?<div id="fullText_\$\{tip\.id\}".*?</div>.*?`;\s*container\.appendChild\(card\);\s*\}\);\s*\}'
new_render = """function renderTips() {
    const container = document.getElementById('tipContainer');
    container.innerHTML = '';
    
    practicalTips.forEach(tip => {
        const card = document.createElement('div');
        card.style.cssText = "background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);";
        
        const sumArr = Array.isArray(tip.summary) ? tip.summary : (typeof tip.summary === "string" ? JSON.parse(tip.summary || "[]") : []); 
        const sumHtml = sumArr.map(s => `<li style="margin-bottom:8px; color:#334155; line-height:1.4; display:flex; gap:8px;"><span style="color:#3b82f6;">✓</span><span>${s}</span></li>`).join('');
        
        card.innerHTML = `
            <h3 style="margin: 0 0 16px; font-size: 16px; font-weight: 800; color: #111827;">${tip.title}</h3>
            <ul style="list-style: none; padding: 0; margin: 0 0 16px; font-size: 14px; font-weight: 700;">
                ${sumHtml}
            </ul>
            <div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;">
                <span style="background: #e0e7ff; color: #4338ca; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 800;">📅 ${tip.effective_date}</span>
                <span style="background: #fee2e2; color: #dc2626; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 800;">⚠️ ${tip.warnings}</span>
            </div>
            <div id="fullText_${tip.id}" style="display: none; margin-top: 16px; padding-top: 16px; border-top: 1px solid #cbd5e1; font-size: 14px; color: #475569; line-height: 1.6; word-break: keep-all;">
                ${tip.full_text}
            </div>
            <button onclick="toggleFullText(${tip.id}, this)" style="width: 100%; padding: 12px; background: white; border: 1px solid #e2e8f0; color: #475569; border-radius: 10px; font-weight: 700; font-size: 14px; cursor: pointer; display: flex; justify-content: center; align-items: center; gap: 6px; margin-bottom: 16px;">
                📄 원문 전체보기
            </button>
            <div style="display: flex; gap: 8px; margin-top: 16px; border-top: 1px dashed #cbd5e1; padding-top: 16px;">
                <button type="button" onclick="saveCurrentTip(event)" style="flex: 1; padding: 12px; border-radius: 10px; font-weight: 800; font-size: 14px; cursor: pointer; border: none; background: #3b82f6; color: white; box-shadow: 0 2px 4px rgba(59,130,246,0.2);">⭐ 보관하기</button>
                <button type="button" onclick="hideCurrentTip(event)" style="flex: 1; padding: 12px; border-radius: 10px; font-weight: 800; font-size: 14px; cursor: pointer; border: none; background: #e2e8f0; color: #475569;">✕ 그만보기</button>
            </div>
        `;
        container.appendChild(card);
    });
}"""
content = re.sub(render_pattern, new_render, content, flags=re.DOTALL)

with open("deal-register.html", "w", encoding="utf-8") as f:
    f.write(content)