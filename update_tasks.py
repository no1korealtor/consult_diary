import re

def modify_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the query
    content = content.replace(
        'schedule_attendances ( user_id, status )',
        'schedule_attendances ( user_id, status ),\n                    schedule_tasks ( id, task_content, is_completed, created_at )'
    )

    # 2. Add Checklist HTML logic just after memoHtml rendering
    checklist_logic = """
                let checklistHtml = '';
                if (!isGlobal && (isMine || (window.currentUser && window.currentUser.role === 'admin'))) {
                    let tasks = schedule.schedule_tasks || [];
                    tasks.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
                    
                    checklistHtml += `<div style="margin-top: 12px; padding-top: 12px; border-top: 1px dashed #cbd5e1;" onclick="event.stopPropagation()">`;
                    checklistHtml += `<div style="font-size: 13px; font-weight: 800; color: #475569; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">`;
                    checklistHtml += `<span>✅ 세부 할 일 (${tasks.filter(t => t.is_completed).length}/${tasks.length})</span>`;
                    checklistHtml += `<button type="button" onclick="addTask('${schedule.id}')" style="background: none; border: none; font-size: 12px; font-weight: 700; color: #3b82f6; cursor: pointer; padding: 4px;">+ 할 일 추가</button>`;
                    checklistHtml += `</div>`;
                    
                    if (tasks.length > 0) {
                        checklistHtml += `<div style="display: flex; flex-direction: column; gap: 4px;">`;
                        tasks.forEach(t => {
                            checklistHtml += `
                            <div style="display: flex; align-items: flex-start; justify-content: space-between; padding: 6px 8px; background: ${t.is_completed ? '#f8fafc' : '#fff'}; border: 1px solid ${t.is_completed ? '#e2e8f0' : '#cbd5e1'}; border-radius: 8px;">
                                <label style="display: flex; align-items: flex-start; gap: 8px; font-size: 13px; color: ${t.is_completed ? '#94a3b8' : '#334155'}; cursor: pointer; flex: 1; text-decoration: ${t.is_completed ? 'line-through' : 'none'}; word-break: break-all; font-weight: ${t.is_completed ? '500' : '600'};">
                                    <input type="checkbox" ${t.is_completed ? 'checked' : ''} onchange="toggleTask('${t.id}', this.checked)" style="margin-top: 2px; accent-color: #3b82f6; width: 14px; height: 14px; cursor: pointer;">
                                    ${t.task_content}
                                </label>
                                <button type="button" onclick="deleteTask('${t.id}')" style="background: none; border: none; font-size: 12px; color: #ef4444; cursor: pointer; padding: 0 4px; font-weight: bold; opacity: 0.6;" title="삭제">✕</button>
                            </div>
                            `;
                        });
                        checklistHtml += `</div>`;
                    }
                    checklistHtml += `</div>`;
                }

                li.style.position = 'relative';"""
    
    content = content.replace("                li.style.position = 'relative';", checklist_logic)
    
    # 3. Add checklistHtml to li.innerHTML rendering
    content = content.replace(
        '${memoHtml}\n                        </div>',
        '${memoHtml}\n                            ${checklistHtml}\n                        </div>'
    )

    # 4. Add the task JS functions right after loadschedules ends (around line 1400)
    # Finding the end of loadschedules block
    task_functions = """
        window.addTask = async function(scheduleId) {
            const content = prompt("추가할 할 일을 입력하세요:\\n(예: 잔금 확인, 수도요금 정산, 열쇠 교부 등)");
            if (!content || !content.trim()) return;

            const { error } = await supabaseClient
                .from('schedule_tasks')
                .insert({ schedule_id: scheduleId, task_content: content.trim() });
                
            if (error) {
                alert("할 일 추가 중 오류 발생: " + error.message);
                return;
            }
            loadschedules();
        };

        window.toggleTask = async function(taskId, isCompleted) {
            const { error } = await supabaseClient
                .from('schedule_tasks')
                .update({ is_completed: isCompleted })
                .eq('id', taskId);
                
            if (error) {
                alert("상태 변경 중 오류 발생: " + error.message);
            }
            loadschedules();
        };

        window.deleteTask = async function(taskId) {
            if (!confirm("이 할 일을 삭제하시겠습니까?")) return;
            const { error } = await supabaseClient
                .from('schedule_tasks')
                .delete()
                .eq('id', taskId);
                
            if (error) {
                alert("삭제 중 오류 발생: " + error.message);
            }
            loadschedules();
        };
"""
    
    content = content.replace("        window.addEventListener('pageshow'", task_functions + "\n        window.addEventListener('pageshow'")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

modify_file('deal-register.html')
