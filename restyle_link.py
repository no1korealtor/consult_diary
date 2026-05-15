import re

with open("deal-register.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the link name default
content = content.replace("let linkName = '🔗 관련 링크 열기';", "let linkName = '관련 링크';")
content = content.replace("linkName = '🔗 ' + parts[1];", "linkName = parts[1];")

# Replace memoHtml link styling
old_link = """if (linkUrl) {
                    memoHtml += `<div onclick="window.open('${linkUrl}', '_blank'); event.stopPropagation();" style="
margin-top: 8px; font-size: 12px; color: #3b82f6; font-weight: 700; display: inline-flex; align-items: center; gap: 4px
; cursor: pointer; padding: 6px 10px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe;">${linkName}<
/div>`;
                }"""
old_link = re.sub(r'\n', '', old_link)
# Just use regex to find linkUrl block
content = re.sub(
    r"if \(linkUrl\) \{.*?memoHtml \+\= `<div onclick=\"window\.open\('\$\{linkUrl\}'.*?</div>`;\n\s*\}",
    r"""if (linkUrl) {
                    memoHtml += `<div onclick="window.open('${linkUrl}', '_blank'); event.stopPropagation();" style="margin-top: 12px; font-size: 13px; color: #475569; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; cursor: pointer; padding: 8px 12px; background: #f1f5f9; border-radius: 8px; transition: 0.2s;">🔗 ${linkName}</div>`;
                }""",
    content,
    flags=re.DOTALL
)

with open("deal-register.html", "w", encoding="utf-8") as f:
    f.write(content)