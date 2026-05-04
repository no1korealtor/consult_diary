const fs = require('fs');
const path = require('path');
const glob = require('glob');

const footer = `
    <footer class="site-footer">
        <div class="site-footer-inner">
            <div class="footer-links">
                <a href="#">회사소개</a>
                <a href="#" style="color: #fca5a5;">개인정보처리방침</a>
                <a href="#">이용약관</a>
            </div>
            <div class="footer-info">
                <strong class="footer-strong">신대림공인중개사사무소</strong>
                <span>사업자등록번호: 219-01-50737</span> <span>전화번호: 010-9128-0586</span><br>
                <span>주소: 서울특별시 마포구 모래내로7길 52 (성산동)</span>
            </div>
        </div>
    </footer>
</body>`;

function addFooterToDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            if (file === 'ediary') addFooterToDir(fullPath);
        } else if (fullPath.endsWith('.html')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            if (!content.includes('<footer class="site-footer">')) {
                content = content.replace('</body>', footer);
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log('Updated ' + fullPath);
            }
        }
    }
}

addFooterToDir('.');
