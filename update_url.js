const fs = require('fs');

function updateFile(filename, isAdmin) {
    let content = fs.readFileSync(filename, 'utf-8');

    if (isAdmin) {
        content = content.replace(
            '<input type="url" id="urlInput" placeholder="관련 URL (예, https://...)">',
            '<input type="url" id="urlInput" placeholder="관련 URL (예, https://...)" style="margin-bottom:8px;">\n        <input type="text" id="urlNameInput" placeholder="링크 이름 (선택, 예: 국세청 홈택스)">'
        );
        content = content.replace(
            "const urlInput = document.getElementById('urlInput').value;",
            "const urlInput = document.getElementById('urlInput').value;\n            const urlNameInput = document.getElementById('urlNameInput').value;"
        );
        content = content.replace(
            "if (urlInput) finalMemo = [URL][/URL] + finalMemo;",
            "if (urlInput) finalMemo = [URL][/URL] + finalMemo;"
        );
        content = content.replace(
            "document.getElementById('urlInput').value = '';",
            "document.getElementById('urlInput').value = '';\n            document.getElementById('urlNameInput').value = '';"
        );
    } else {
        content = content.replace(
            '<input type="url" id="meetingUrl" placeholder="관련 링크 (URL)" style="margin-bottom: 0;">',
            '<input type="url" id="meetingUrl" placeholder="관련 링크 (URL)" style="margin-bottom: 8px;">\n          <input type="text" id="meetingUrlName" placeholder="링크 이름 (선택, 예: 국세청 홈택스)" style="margin-bottom: 0;">'
        );
        content = content.replace(
            "const mUrl = document.getElementById('meetingUrl').value;",
            "const mUrl = document.getElementById('meetingUrl').value;\n                  const mUrlName = document.getElementById('meetingUrlName').value;"
        );
        content = content.replace(
            "if(mUrl) finalMemo += [URL][/URL];",
            "if(mUrl) finalMemo += [URL][/URL];"
        );
    }

    // Replace parsing logic (both)
    const parseTarget =                 if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\\[URL\\](.*?)\\[\\/URL\\]/);
                    if (m) { linkUrl = m[1]; rawMemo = rawMemo.replace(m[0], ''); }
                };
    
    const parseReplacement =                 let linkName = '🔗 관련 링크 열기';
                if (rawMemo.includes('[URL]')) {
                    const m = rawMemo.match(/\\[URL\\](.*?)\\[\\/URL\\]/);
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
                };
    
    // JS .replace with string only replaces first occurrence, which is what we want
    // But since line endings might differ (CRLF vs LF), we should normalize to regex or just replace whitespace variations
    content = content.replace(/if\s*\(rawMemo\.includes\('\[URL\]'\)\)\s*\{\s*const m = rawMemo\.match\(\/\\\[URL\\\]\(\.\*\?\)\\\[\\\/URL\\\]\/\);\s*if\s*\(m\)\s*\{\s*linkUrl\s*=\s*m\[1\];\s*rawMemo\s*=\s*rawMemo\.replace\(m\[0\],\s*''\);\s*\}\s*\}/g, parseReplacement);

    const renderTarget1 = /if\s*\(linkUrl\)\s*\{\s*memoHtml\s*\+=\s*<div onclick="window\.open\('\$\{linkUrl\}',\s*'_blank'\);\s*event\.stopPropagation\(\);"\s*style="margin-top:\s*8px;\s*font-size:\s*12px;\s*color:\s*#3b82f6;\s*font-weight:\s*700;\s*display:\s*inline-flex;\s*align-items:\s*center;\s*gap:\s*4px;\s*cursor:\s*pointer;\s*padding:\s*6px\s*10px;\s*background:\s*#eff6ff;\s*border-radius:\s*6px;\s*border:\s*1px\s*solid\s*#bfdbfe;">🔗 관련 링크 열기<\/div>;\s*\}/g;
    const renderReplacement1 = if (linkUrl) {
                    memoHtml += \<div onclick="window.open('\', '_blank'); event.stopPropagation();" style="margin-top: 8px; font-size: 12px; color: #3b82f6; font-weight: 700; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; padding: 6px 10px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe;">\</div>\;
                };
    content = content.replace(renderTarget1, renderReplacement1);

    const renderTarget2 = /if\s*\(linkUrl\)\s*\{\s*memoHtml\s*\+=\s*<div onclick="window\.open\('\$\{linkUrl\}',\s*'_blank'\);\s*event\.stopPropagation\(\);"\s*style="margin-top:\s*6px;\s*font-size:\s*13px;\s*color:\s*#3b82f6;\s*font-weight:\s*600;\s*display:\s*inline-flex;\s*align-items:\s*center;\s*gap:\s*4px;\s*cursor:\s*pointer;\s*padding:\s*4px\s*8px;\s*background:\s*#eff6ff;\s*border-radius:\s*6px;">🔗 관련 링크 열기<\/div>;\s*\}/g;
    const renderReplacement2 = if (linkUrl) {
                    memoHtml += \<div onclick="window.open('\', '_blank'); event.stopPropagation();" style="margin-top: 6px; font-size: 13px; color: #3b82f6; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 8px; background: #eff6ff; border-radius: 6px;">\</div>\;
                };
    content = content.replace(renderTarget2, renderReplacement2);

    fs.writeFileSync(filename, content, 'utf-8');
}

updateFile('admin-global-deals.html', true);
updateFile('deal-register.html', false);