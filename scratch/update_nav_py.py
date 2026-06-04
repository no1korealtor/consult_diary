import os
import re

files = [
    "manual.html",
    "deal-register.html",
    "contacts.html",
    "admin-tips.html",
    "profile-edit.html",
    "market.html",
    "harmonica.html",
    "study.html",
    "login.html",
    "scrap.html"
]

nav_template = """<nav class="{nav_class}">
    <a href="deal-register.html" class="nav-item">
        <span class="nav-icon">🏠</span>
        <span>일정</span>
    </a>
    <a href="market.html" class="nav-item" id="navMarket" style="display: none;">
        <span class="nav-icon">📋</span>
        <span>장부</span>
    </a>
    <a href="contacts.html" class="nav-item">
        <span class="nav-icon">👥</span>
        <span>연락처</span>
    </a>
    <a href="manual.html" class="nav-item">
        <span class="nav-icon">🗂️</span>
        <span>자료실</span>
    </a>
    <a href="profile-edit.html" class="nav-item">
        <span class="nav-icon">👤</span>
        <span>내정보</span>
    </a>
</nav>"""

for filename in files:
    if not os.path.exists(filename):
        continue
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if '<nav class="bottom-nav">' in content or '<nav class="bottom-nav dark-mode">' in content:
        nav_class = "bottom-nav dark-mode" if '<nav class="bottom-nav dark-mode">' in content else "bottom-nav"
        
        replacement = nav_template.format(nav_class=nav_class)
        
        # Add active class for the current file
        replacement = replacement.replace(f'"{filename}" class="nav-item"', f'"{filename}" class="nav-item active"')
        # Special case: scrap.html and manual.html share the same tab logic, but we make manual.html active
        if filename == "scrap.html":
             replacement = replacement.replace(f'"manual.html" class="nav-item"', f'"manual.html" class="nav-item active"')
        
        new_content = re.sub(r'<nav class="bottom-nav[^>]*>.*?</nav>', replacement, content, flags=re.DOTALL)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
