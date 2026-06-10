const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient('https://clzrbyplzjdrrscctcsl.supabase.co', 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k');

async function insertMoatown() {
    const html = fs.readFileSync('d:\\부동산업무\\antigravity\\consult_diary\\moatown.html', 'utf8');
    
    const startIdx = html.indexOf('<div class="blog-content" id="exportContent">');
    const endIdx = html.indexOf('<div class="public-footer">');
    
    if (startIdx === -1 || endIdx === -1) {
        console.log('Could not extract content');
        return;
    }
    
    let content = html.substring(startIdx, endIdx);
    
    // Remove the wrapping div and tags
    content = content.replace(/<div class="blog-content" id="exportContent">/, '');
    content = content.replace(/<div id="scrapTag">.*?<\/div>/s, '');
    content = content.replace(/<h1>.*?<\/h1>/s, '');
    content = content.replace(/<h2 class="subtitle">.*?<\/h2>/s, '');
    content = content.replace(/<hr>/s, '');
    
    content = content.trim();
    
    const data = {
        title: "모아타운, 도대체 무엇이 궁금한가?",
        category: "기타", // We will use '기타' as that's one of the options, or let's say '재개발/재건축'
        summary: JSON.stringify(["모아타운과 모아주택의 차이", "가로주택정비사업과의 비교", "권리산정기준일과 분양권 요건", "현금청산 기준"]),
        full_text: content,
        is_active: true
    };
    
    const { data: resData, error } = await supabase.from('practical_tips').insert(data).select();
    
    if (error) {
        console.error('Insert error:', error);
    } else {
        console.log('Inserted successfully:', resData);
    }
}

insertMoatown();
