import re

with open("admin-tips.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update CSS
css_pattern = r"<style>.*?</style>"
new_css = """<style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css');

        body {
            font-family: 'Pretendard Variable', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
            background-color: #f3f4f6;
            margin: 0;
            padding: 24px 16px;
            max-width: 480px;
            margin-left: auto;
            margin-right: auto;
        }

        h2 {
            font-size: 22px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 24px;
        }

        .form-group {
            background: #ffffff;
            padding: 24px;
            border-radius: 24px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.03);
            margin-bottom: 32px;
        }

        label {
            display: block;
            font-size: 13px;
            font-weight: 700;
            color: #64748b;
            margin-bottom: 8px;
            margin-top: 16px;
        }

        input[type="text"], select, textarea {
            width: 100%;
            padding: 14px 16px;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 600;
            font-family: inherit;
            box-sizing: border-box;
            background: #f1f5f9;
            color: #1e293b;
            transition: all 0.2s;
        }

        input[type="text"]:focus, select:focus, textarea:focus {
            outline: none;
            background: #e2e8f0;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }

        textarea {
            height: 100px;
            resize: vertical;
        }

        .btn-primary {
            width: 100%;
            padding: 16px;
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 16px;
            font-weight: 800;
            cursor: pointer;
            margin-top: 24px;
            transition: 0.2s;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
        }

        .btn-primary:active {
            transform: scale(0.98);
        }

        .tip-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .tip-item {
            background: white;
            padding: 20px;
            border-radius: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.02);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

    </style>"""
content = re.sub(css_pattern, new_css, content, flags=re.DOTALL)

# 2. Add resetVisibility Function
script_insert = """
        async function resetVisibility(tipId) {
            if(!confirm('이 팁을 다시 모든 사용자의 메인 화면 배너에 띄우시겠습니까? (알림 재공지)')) return;
            
            const { error } = await supabaseClient
                .from('user_tip_status')
                .update({ is_hidden: false })
                .eq('tip_id', tipId);
                
            if(error) {
                alert('재공지 처리 실패: ' + error.message);
                return;
            }
            alert('성공적으로 재공지되었습니다! 이제 사용자들이 접속하면 배너가 다시 뜹니다.');
        }

        let allTipsData = [];
"""
content = re.sub(r"let allTipsData = \[\];", script_insert, content, count=1)

# 3. Update tip-item HTML inside loadTips to show the three buttons beautifully
item_pattern = r"li\.innerHTML = `.*?`;"
item_replacement = """li.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <span style="font-size: 11px; font-weight: 800; color: #4338ca; background: #e0e7ff; padding: 4px 8px; border-radius: 6px; margin-bottom: 8px; display: inline-block;">${tip.category}</span>
                            <div style="font-size: 16px; font-weight: 800; color: #0f172a; line-height: 1.4;">${tip.title}</div>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; margin-top: 8px;">
                        <button onclick="resetVisibility(${tip.id})" style="flex: 1; background: #eff6ff; color: #2563eb; border: none; padding: 10px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 13px;">📢 재공지</button>
                        <button onclick="editTip(${tip.id})" style="flex: 1; background: #f1f5f9; color: #475569; border: none; padding: 10px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 13px;">✏️ 수정</button>
                        <button onclick="deleteTip(${tip.id})" style="flex: 1; background: #fef2f2; color: #dc2626; border: none; padding: 10px; border-radius: 8px; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 13px;">🗑️ 삭제</button>
                    </div>
                `;"""
content = re.sub(item_pattern, item_replacement, content, flags=re.DOTALL)

with open("admin-tips.html", "w", encoding="utf-8") as f:
    f.write(content)