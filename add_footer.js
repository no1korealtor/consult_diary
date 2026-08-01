const fs = require('fs');
const path = require('path');

const appFooterReplacement = `    <footer class="app-footer">
        <strong>신대림공인중개사사무소 (제호: 공인중개사소식지)</strong>
        대표/발행·편집인: 조항준 | 등록번호: 서울, 아53763 | 등록일자: 2021년 06월 14일<br>
        사업자등록번호: 219-01-50737 | 전화번호: 010-9128-0586 | 주소: 서울특별시 마포구 모래내로7길 52 (성산동)
    </footer>`;

const siteFooterReplacement = `    <footer class="site-footer">
        <div class="site-footer-inner">
            <div class="footer-links">
                <a href="#">회사소개</a>
                <a href="#" style="color: #fca5a5;">개인정보처리방침</a>
                <a href="#">이용약관</a>
            </div>
            <div class="footer-info">
                <strong class="footer-strong">신대림공인중개사사무소 (제호: 공인중개사소식지)</strong>
                <span>대표/발행·편집인: 조항준</span> <span>등록번호: 서울, 아53763</span> <span>등록일자: 2021년 06월 14일</span><br>
                <span>사업자등록번호: 219-01-50737</span> <span>전화번호: 010-9128-0586</span> <span>주소: 서울특별시 마포구 모래내로7길 52 (성산동)</span>
            </div>
        </div>
    </footer>`;

const newFooterTemplate = `\n${siteFooterReplacement}\n</body>`;

function updateFile(filePath) {
    let content = fs.readFileSync(filePath, 'utf8');
    let modified = false;

    const hasApp = content.includes('<footer class="app-footer"') || content.includes("<footer class='app-footer'");
    const hasSite = content.includes('<footer class="site-footer"') || content.includes("<footer class='site-footer'");

    if (hasApp && hasSite) {
        // Remove site-footer entirely
        content = content.replace(/<footer class=["']site-footer["']>[\s\S]*?<\/footer>/g, '');
        // Update app-footer
        content = content.replace(/<footer class=["']app-footer["']>[\s\S]*?<\/footer>/g, appFooterReplacement);
        modified = true;
    } else if (hasApp) {
        // Update app-footer
        content = content.replace(/<footer class=["']app-footer["']>[\s\S]*?<\/footer>/g, appFooterReplacement);
        modified = true;
    } else if (hasSite) {
        // Update site-footer
        content = content.replace(/<footer class=["']site-footer["']>[\s\S]*?<\/footer>/g, siteFooterReplacement);
        modified = true;
    } else {
        // Neither exists, insert new site-footer before </body>
        if (content.includes('</body>')) {
            content = content.replace('</body>', newFooterTemplate);
            modified = true;
        }
    }

    if (modified) {
        content = content.replace(/\s*\n\s*<\/body>/, '\n</body>');
        fs.writeFileSync(filePath, content, 'utf8');
        console.log('Updated: ' + filePath);
    }
}

function processDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            if (file !== '.git' && file !== 'node_modules') {
                processDir(fullPath);
            }
        } else if (fullPath.endsWith('.html')) {
            updateFile(fullPath);
        }
    }
}

processDir('.');
