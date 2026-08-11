import os
import re

app_footer_replacement = '''    <footer class="app-footer">
        <strong>신대림공인중개사사무소 (제호: 공인중개사소식지)</strong>
        대표/발행·편집인: 조항준 | 등록번호: 서울, 아53763 | 등록일자: 2021년 06월 14일<br>
        사업자등록번호: 219-01-50737 | 전화번호: 02-375-4489 | 주소: 서울특별시 마포구 모래내로7길 52 (성산동)
    </footer>'''

site_footer_replacement = '''    <footer class="site-footer">
        <div class="site-footer-inner">
            <div class="footer-links">
                <a href="#">회사소개</a>
                <a href="#" style="color: #fca5a5;">개인정보처리방침</a>
                <a href="#">이용약관</a>
            </div>
            <div class="footer-info">
                <strong class="footer-strong">신대림공인중개사사무소 (제호: 공인중개사소식지)</strong>
                <span>대표/발행·편집인: 조항준</span> <span>등록번호: 서울, 아53763</span> <span>등록일자: 2021년 06월 14일</span><br>
                <span>사업자등록번호: 219-01-50737</span> <span>전화번호: 02-375-4489</span> <span>주소: 서울특별시 마포구 모래내로7길 52 (성산동)</span>
            </div>
        </div>
    </footer>'''

new_footer_template = '\n' + site_footer_replacement + '\n</body>'

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    
    has_app = '<footer class="app-footer"' in content or "<footer class='app-footer'" in content
    has_site = '<footer class="site-footer"' in content or "<footer class='site-footer'" in content
    
    if has_app and has_site:
        # Remove site-footer entirely
        content = re.sub(r'<footer class=["\']site-footer["\'].*?</footer>', '', content, flags=re.DOTALL)
        # Update app-footer
        content = re.sub(r'<footer class=["\']app-footer["\'].*?</footer>', app_footer_replacement, content, flags=re.DOTALL)
        modified = True
    elif has_app:
        # Update app-footer
        content = re.sub(r'<footer class=["\']app-footer["\'].*?</footer>', app_footer_replacement, content, flags=re.DOTALL)
        modified = True
    elif has_site:
        # Update site-footer
        content = re.sub(r'<footer class=["\']site-footer["\'].*?</footer>', site_footer_replacement, content, flags=re.DOTALL)
        modified = True
    else:
        # Neither exists, insert new site-footer before </body>
        if '</body>' in content:
            content = content.replace('</body>', new_footer_template)
            modified = True
            
    if modified:
        # Clean up any duplicate newlines or spaces before </body>
        content = re.sub(r'\s*\n\s*</body>', '\n</body>', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated: {file_path}')

# Find all HTML files recursively in the project directory
for root, dirs, files in os.walk('.'):
    # Skip git and node_modules
    if '.git' in root or 'node_modules' in root:
        continue
    for file in files:
        if file.endswith('.html'):
            file_path = os.path.join(root, file)
            update_file(file_path)
