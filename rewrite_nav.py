import os
import re
import glob

html_files = glob.glob('*.html') + glob.glob('smart_schedule/*.html')

nav_template = """<nav class="{navClass}">
    <a href="deal-register.html" class="nav-item{active_deal}">
        <span class="nav-icon">🏠</span>
        <span>일정</span>
    </a>
    <a href="market.html" class="nav-item{active_market}">
        <span class="nav-icon">📋</span>
        <span>장부</span>
    </a>
    <a href="contacts.html" class="nav-item{active_contacts}">
        <span class="nav-icon">👥</span>
        <span>연락처</span>
    </a>
    <a href="tips-handbook.html" class="nav-item{active_tips}">
        <span class="nav-icon">🗂️</span>
        <span>자료실</span>
    </a>
    <a href="profile-edit.html" class="nav-item{active_profile}">
        <span class="nav-icon">👤</span>
        <span>내정보</span>
    </a>
</nav>"""

for file_path in html_files:
    if not os.path.exists(file_path): continue
    
    # Read keeping utf-8 if possible, else cp949
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp949') as f:
            content = f.read()
            
    is_dark = '<nav class="bottom-nav dark-mode"' in content
    navClass = "bottom-nav dark-mode" if is_dark else "bottom-nav"
    
    basename = os.path.basename(file_path)
    active_deal = ' active' if basename == 'deal-register.html' else ''
    active_market = ' active' if basename == 'market.html' else ''
    active_contacts = ' active' if basename == 'contacts.html' else ''
    active_tips = ' active' if basename in ('tips-handbook.html', 'manual.html', 'scrap.html') else ''
    active_profile = ' active' if basename == 'profile-edit.html' else ''
    
    new_nav = nav_template.format(navClass=navClass, active_deal=active_deal, active_market=active_market, active_contacts=active_contacts, active_tips=active_tips, active_profile=active_profile)
    
    new_content = re.sub(r'<nav class="bottom-nav[^>]*>.*?</nav>', new_nav, content, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
