import re

def update_file(filename, is_admin):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    if is_admin:
        # 1. Add UI
        content = content.replace(
            '<input type="url" id="urlInput" placeholder="관련 URL (예, https://...)">',
            '<input type="url" id="urlInput" placeholder="관련 URL (예, https://...)" style="margin-bottom:8px;">\n        <input type="text" id="urlNameInput" placeholder="링크 이름 (선택, 예: 국세청 홈택스)">'
        )
        # 2. Add variables
        content = content.replace(
            "const urlInput = document.getElementById('urlInput').value;",
            "const urlInput = document.getElementById('urlInput').value;\n            const urlNameInput = document.getElementById('urlNameInput').value;"
        )
        # 3. Store logic
        content = content.replace(
            "if (urlInput) finalMemo = [URL][/URL] + finalMemo;",
            "if (urlInput) finalMemo = [URL][/URL] + finalMemo;"
        )
        # 4. Clear input
        content = content.replace(
            "document.getElementById('urlInput').value = '';",
            "document.getElementById('urlInput').value = '';\n            document.getElementById('urlNameInput').value = '';"
        )
    else:
        # deal-register.html UI
        content = content.replace(
            '<input type="url" id="meetingUrl" placeholder="관련 링크 (URL)" style="margin-bottom: 0;">',
            '<input type="url" id="meetingUrl" placeholder="관련 링크 (URL)" style="margin-bottom: 8px;">\n          <input type="text" id="meetingUrlName" placeholder="링크 이름 (선택, 예: 국세청 홈택스)" style="margin-bottom: 0;">'
        )
        # 2. Store logic
        content = content.replace(
            "const mUrl = document.getElementById('meetingUrl').value;",
            "const mUrl = document.getElementById('meetingUrl').value;\n                  const mUrlName = document.getElementById('meetingUrlName').value;"
        )
        content = content.replace(
            "if(mUrl) finalMemo += [URL][/URL];",
            "if(mUrl) finalMemo += [URL][/URL];"
        )

    # 5. Parse logic (Both)
    parse_target = """                if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\[URL\](.*?)\[\/URL\]/);
                    if (m) { linkUrl = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                }"""
    parse_replacement = """                let linkName = '🔗 관련 링크 열기';
                if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\[URL\](.*?)\[\/URL\]/);
                    if (m) { 
                        let urlData = m[1];
                        if (urlData.includes('|')) {
                            const parts = urlData.split('|');
                            linkUrl = parts[0];
                            linkName = '🔗 ' + parts[1];
                        } else {
                            linkUrl = urlData;
                        }
                        rawMemo = rawMemo.replace(m[0], ''); 
                    }
                }"""
    content = content.replace(parse_target, parse_replacement)

    # 6. Render logic (Both)
    render_target1 = """                if (linkUrl) {
                    memoHtml += <div onclick="window.open('', '_blank'); event.stopPropagation();" style="margin-top: 8px; font-size: 12px; color: #3b82f6; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; padding: 6px 10px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe;">🔗 관련 링크 열기</div>;
                }"""
    render_replacement1 = """                if (linkUrl) {
                    memoHtml += <div onclick="window.open('', '_blank'); event.stopPropagation();" style="margin-top: 8px; font-size: 12px; color: #3b82f6; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; padding: 6px 10px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe;"></div>;
                }"""
                
    render_target2 = """                if (linkUrl) {
                    memoHtml += <div onclick="window.open('', '_blank'); event.stopPropagation();" style="margin-top: 6px; font-size: 13px; color: #3b82f6; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 8px; background: #eff6ff; border-radius: 6px;">🔗 관련 링크 열기</div>;
                }"""
    render_replacement2 = """                if (linkUrl) {
                    memoHtml += <div onclick="window.open('', '_blank'); event.stopPropagation();" style="margin-top: 6px; font-size: 13px; color: #3b82f6; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 8px; background: #eff6ff; border-radius: 6px;"></div>;
                }"""
                
    content = content.replace(render_target1, render_replacement1)
    content = content.replace(render_target2, render_replacement2)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

update_file('admin-global-deals.html', True)
update_file('deal-register.html', False)

print("Done")