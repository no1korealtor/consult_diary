$csvPath = "d:\부동산업무\강의관련모음\모아타운\서울특별시 소규모주택정비법령 질의회신 사례집  (1).csv"
$htmlPath = "d:\부동산업무\강의관련모음\모아타운\소규모주택정비법령_질의회신_사례집_편람.html"

# Read the entire text (handling BOM if present)
$content = [IO.File]::ReadAllText($csvPath, [Text.Encoding]::UTF8)

# Convert to Base64 to safely embed in JS
$bytes = [Text.Encoding]::UTF8.GetBytes($content)
$encoded = [Convert]::ToBase64String($bytes)

$html = @"
<!DOCTYPE html>
<html lang='ko'>
<head>
<meta charset='UTF-8'>
<title>서울특별시 소규모주택정비법령 질의회신 사례집 편람</title>
<style>
body { font-family: 'Malgun Gothic', sans-serif; padding: 20px; line-height: 1.6; background-color: #f4f7f6; color: #333; margin: 0; }
.container { max-width: 1000px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
h1 { text-align: center; color: #2c3e50; font-size: 2em; margin-bottom: 40px; }
.category { margin-top: 50px; border-bottom: 3px solid #3498db; padding-bottom: 10px; color: #2980b9; font-size: 1.5em; }
.sub-category { margin-top: 30px; color: #34495e; font-size: 1.2em; border-left: 4px solid #95a5a6; padding-left: 10px; }
.item { background: #fff; border: 1px solid #e0e6ed; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: transform 0.2s; }
.item:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.item-title { font-weight: bold; color: #e74c3c; margin-bottom: 8px; font-size: 1.15em; }
.item-meta { font-size: 0.85em; color: #7f8c8d; margin-bottom: 15px; border-bottom: 1px dashed #eee; padding-bottom: 10px; }
.item-summary { font-weight: 600; margin-bottom: 15px; color: #2c3e50; }
.item-reply { background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; border-radius: 4px; white-space: pre-wrap; font-size: 0.95em; line-height: 1.7; color: #444; }
.search-box { width: 100%; padding: 15px; font-size: 1.1em; border: 2px solid #ddd; border-radius: 8px; margin-bottom: 30px; box-sizing: border-box; }
.search-box:focus { outline: none; border-color: #3498db; }
.hidden { display: none !important; }
</style>
</head>
<body>
<div class='container'>
    <h1>📖 서울특별시 소규모주택정비법령 질의회신 사례집 편람</h1>
    
    <input type="text" id="searchInput" class="search-box" placeholder="검색어를 입력하세요 (제목, 요지, 회신내용 등)..." onkeyup="filterItems()">
    
    <div id='content'>데이터를 불러오는 중입니다...</div>
</div>

<script>
    const base64Data = "$encoded";
    
    function b64DecodeUnicode(str) {
        return decodeURIComponent(atob(str).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
    }
    
    try {
        const rawCsv = b64DecodeUnicode(base64Data);
        
        const records = [];
        let inQuote = false;
        let currentRecord = '';
        for(let i=0; i<rawCsv.length; i++) {
            const char = rawCsv[i];
            if (char === '"') {
                if (inQuote && i+1 < rawCsv.length && rawCsv[i+1] === '"') {
                    currentRecord += '"';
                    i++; 
                } else {
                    inQuote = !inQuote;
                    if (!inQuote) {
                        records.push(currentRecord);
                        currentRecord = '';
                    }
                }
            } else {
                if (inQuote) currentRecord += char;
            }
        }
        
        let htmlOut = '';
        let currentLarge = '';
        let currentMedium = '';
        
        let isFirst = true;
        for (let record of records) {
            const lines = record.split('\\n');
            if (lines.length < 7) continue;
            if (isFirst && lines[0].trim() === '대분류') {
                isFirst = false;
                continue;
            }
            isFirst = false;
            
            const largeCat = lines[0].trim();
            const mediumCat = lines[1].trim();
            const page = lines[2].trim();
            const docNum = lines[3].trim();
            const title = lines[4].trim();
            const summary = lines[5].trim();
            const reply = lines.slice(6).join('\\n').trim();
            
            if (largeCat !== currentLarge) {
                currentLarge = largeCat;
                htmlOut += '<h2 class="category search-target">' + currentLarge + '</h2>';
                currentMedium = '';
            }
            if (mediumCat !== currentMedium) {
                currentMedium = mediumCat;
                htmlOut += '<h3 class="sub-category search-target">' + currentMedium + '</h3>';
            }
            
            htmlOut += '<div class="item search-target">';
            htmlOut += '<div class="item-title">' + title + '</div>';
            htmlOut += '<div class="item-meta">문서번호: ' + docNum + ' | 페이지: ' + page + '</div>';
            htmlOut += '<div class="item-summary">' + summary + '</div>';
            htmlOut += '<div class="item-reply">' + reply + '</div>';
            htmlOut += '</div>';
        }
        document.getElementById('content').innerHTML = htmlOut || '데이터가 없습니다.';
    } catch(e) {
        document.getElementById('content').innerHTML = '오류 발생: ' + e;
    }

    function filterItems() {
        const input = document.getElementById('searchInput').value.toLowerCase();
        const targets = document.querySelectorAll('.search-target');
        
        let currentCat = null;
        let currentSub = null;
        
        // Simple search: just hide items that don't match. 
        // Categories will always show if any child matches.
        
        targets.forEach(el => {
            if (el.classList.contains('category') || el.classList.contains('sub-category')) {
                // Show by default, we can refine logic later
                el.style.display = '';
            } else if (el.classList.contains('item')) {
                const text = el.innerText.toLowerCase();
                if (text.includes(input)) {
                    el.style.display = '';
                } else {
                    el.style.display = 'none';
                }
            }
        });
    }
</script>
</body>
</html>
"@

[IO.File]::WriteAllText($htmlPath, $html, [Text.Encoding]::UTF8)
Write-Host "Done"
