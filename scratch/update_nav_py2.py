import os

files = [
    "admin-center.html", "admin-tips.html", "contacts.html", 
    "deal-register.html", "login.html", "manual.html", 
    "market.html", "profile-edit.html"
]

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = content.replace('<a href="tips-handbook.html"', '<a href="manual.html"')
        content = content.replace('<span class="nav-icon">📚</span>\n        <span>편람</span>', '<span class="nav-icon">📖</span>\n        <span>매뉴얼</span>')
        content = content.replace('<span class="nav-icon">📖</span>\n            <span>편람</span>', '<span class="nav-icon">📖</span>\n            <span>매뉴얼</span>')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Done")
