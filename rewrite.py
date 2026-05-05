import codecs
import re

with codecs.open('public-consult.html', 'r', 'utf-8') as f:
    html = f.read()

# 1. Update topActionButtons
html = re.sub(r'<div id="topActionButtons">.*?</div>', '<div id="topActionButtons">\n                    <a href="index.html?pro=true" class="btn" style="padding: 0.5rem 1rem; width: auto; background: var(--accent-color);">전문가 로그인</a>\n                </div>', html, flags=re.DOTALL)

# 2. Remove 기타 option from categorySelect
html = html.replace('<option value="기타">기타</option>', '')

# 3. Remove subCategoryArea and detailSelectArea
html = re.sub(r'<!-- Step 1-2 \(Sub Category\) -->.*?</div>\s*<!-- Step 1-3 \(Detail & Penalty\) -->.*?</div>', '', html, flags=re.DOTALL)

# 4. Remove searchForm and resultArea
html = re.sub(r'<!-- Step 3 -->.*?<div id="resultArea"[^>]*>.*?</div>\s*</div>', '</div>', html, flags=re.DOTALL)

# 5. Simplify JS script entirely
html = re.sub(r'<script type="module">.*?</script>', '''<script type="module">
        import { supabase } from './supabase-client.js';

        window.toggleTimeline = (element) => {
            element.classList.toggle('expanded');
        };

        const categorySelect = document.getElementById('categorySelect');
        const processFlowArea = document.getElementById('processFlowArea');
        const processFlowBox = document.getElementById('processFlowBox');
        
        categorySelect.addEventListener('change', (e) => {
            const val = e.target.value;
            if (!val) {
                processFlowArea.style.display = 'none';
                return;
            }
            updateProcessFlow(val);
        });

        const STAGE_CONFIG = {
            '과태료': [
                { 
                    name: '소명', basis: '질서위반행위규제법', 
                    desc: '공인중개사에 대한 행정청의 과태료 부과는 한국부동산원의 모니터닝 결과 통보에 의한 행정청의 조사 또는 민원에 의해 시작되고 통상 이 과정을 소명요구단계라 말합니다.', 
                    tip: '?? Tip: 소명 기한은 통상 10일 이상. 객관적 자료가 필수입니다.',
                    lawTitle: '제22조(질서위반행위의 조사)',
                    lawText: `① 행정청은 질서위반행위가 발생하였다는 합리적 의심이 있어 그에 대한 조사가 필요하다고 인정할 때에는 대통령령으로 정하는 바에 따라 다음 각 호의 조치를 할 수 있다.<br>&nbsp;&nbsp;1. 당사자 또는 참고인의 출석 요구 및 진술의 청취<br>&nbsp;&nbsp;2. 당사자에 대한 보고 명령 또는 자료 제출의 명령<br><br>② 행정청은 질서위반행위가 발생하였다는 합리적 의심이 있어 그에 대한 조사가 필요하다고 인정할 때에는 그 소속 직원으로 하여금 당사자의 사무소 또는 영업소에 출입하여 장부ㆍ서류 또는 그 밖의 물건을 검사하게 할 수 있다.<br><br>③ 제2항에 따른 검사를 하고자 하는 행정청 소속 직원은 당사자에게 검사 개시 7일 전까지 검사 대상 및 검사 이유, 그 밖에 대통령령으로 정하는 사항을 통지하여야 한다. 다만, 긴급을 요하거나 사전통지의 경우 증거인멸 등으로 검사목적을 달성할 수 없다고 인정되는 때에는 그러하지 아니하다.<br><br>④ 제2항에 따라 검사를 하는 직원은 그 권한을 표시하는 증표를 지니고 이를 관계인에게 내보여야 한다.<br><br>⑤ 제1항 및 제2항에 따른 조치 또는 검사는 그 목적 달성에 필요한 최소한에 그쳐야 한다.`
                },
                { 
                    name: '사전통지', basis: '질서위반행위규제법', 
                    desc: '행정청이 당사자에게 미리 알리고 의견을 제출할 기회를 줍니다.', 
                    tip: '?? 안내: 자진 납부 시 최대 20% 과태료 감경 가능.',
                    lawTitle: '시행령 제3조(사전통지 및 의견제출 등)',
                    lawText: `① 법 제16조제1항에 따라 행정청이 과태료 부과에 관하여 미리 통지하는 경우에는 다음 각 호의 사항을 모두 적은 서면으로 하여야 한다.<br>&nbsp;&nbsp;1. 당사자의 성명과 주소<br>&nbsp;&nbsp;<u>2. 과태료 부과의 원인이 되는 사실, 과태료 금액 및 적용 법령</u><br>&nbsp;&nbsp;3. 과태료를 부과하는 행정청의 명칭과 주소<br>&nbsp;&nbsp;4. 당사자가 의견을 제출할 수 있다는 사실과 그 제출기한<br>&nbsp;&nbsp;5. 법 제18조에 따라 자진 납부하는 경우 과태료를 감경받을 수 있다는 사실<br>&nbsp;&nbsp;<u>5의2. 감경된 과태료 납부 시 과태료 부과·징수절차가 종료되어 의견 제출 및 이의제기를 할 수 없다는 사실</u><br>&nbsp;&nbsp;6. 제2조의2에 따라 과태료를 감경받을 수 있다는 사실<br>&nbsp;&nbsp;7. 그 밖에 과태료 부과에 관하여 필요한 사항<br><br>② 당사자는 의견제출 기한 이내에 서면이나 말로 의견을 제출(진술)할 수 있고, 증거자료 등을 제출할 수 있다.<br><br>③ 행정청은 당사자가 말로 의견을 진술한 경우에는 진술자와 그 의견의 요지를 기록해 두어야 한다.`
                },
                { 
                    name: '과태료 부과', basis: '질서위반행위규제법', 
                    desc: '정식으로 과태료 납부 고지서가 발송됩니다.', tip: '' 
                },
                { 
                    name: '이의제기', basis: '질서위반행위규제법', 
                    desc: '과태료 부과 처분에 불복하여 이의를 제기합니다.', 
                    tip: '?? 주의: 부과 통지 받은 날부터 60일 이내 서면 제출. 이의 제기 시 과태료 처분 효력 상실.',
                    lawTitle: '제20조(이의제기)',
                    lawText: `① 행정청의 과태료 부과에 불복하는 당사자는 제17조제1항에 따른 과태료 부과 통지를 받은 날부터 60일 이내에 해당 행정청에 서면으로 이의제기를 할 수 있다.<br><br>② 제1항에 따른 이의제기가 있는 경우에는 행정청의 과태료 부과처분은 그 효력을 상실한다.<br><br>③ 당사자는 행정청으로부터 제21조제3항에 따른 통지를 받기 전까지는 행정청에 대하여 서면으로 이의제기를 철회할 수 있다.`
                },
                { 
                    name: '법원통보', basis: '질서위반행위규제법', 
                    desc: '행정청은 이의제기를 받은 날부터 14일 이내에 법원에 통보합니다.', 
                    tip: '?? 실무 Tip: 실무상 사실상 전수 약식재판으로 진행됩니다.',
                    lawTitle: '제21조(법원에의 통보)',
                    lawText: `① 제20조제1항에 따른 이의제기를 받은 행정청은 이의제기를 받은 날부터 14일 이내에 이에 대한 의견 및 증빙서류를 첨부하여 관할 법원에 통보하여야 한다. 다만, 다음 각 호의 어느 하나에 해당하는 경우에는 그러하지 아니하다.<br>&nbsp;&nbsp;1. 당사자가 이의제기를 철회한 경우<br>&nbsp;&nbsp;2. 당사자의 이의제기에 이유가 있어 과태료를 부과할 필요가 없는 것으로 인정되는 경우<br><br>② 행정청은 사실상 또는 법률상 같은 원인으로 말미암아 다수인에게 과태료를 부과할 필요가 있는 경우에는 다수인 가운데 1인에 대한 관할권이 있는 법원에 제1항에 따른 이의제기 사실을 통보할 수 있다.<br><br>③ 행정청이 제1항 및 제2항에 따라 관할 법원에 통보를 하거나 통보하지 아니하는 경우에는 그 사실을 즉시 당사자에게 통지하여야 한다.`
                },
                { 
                    name: '재판', basis: '질서위반행위규제법', 
                    desc: '약식재판 또는 정식재판이 진행됩니다.', 
                    tip: '? 기한: 결정 통지 받은 날부터 7일 이내 즉시항고.' 
                }
            ],
            '행정처분': [
                { name: '조사단계', basis: '행정절차법', desc: '위반 사실에 대한 현장 조사 및 관련 자료 수집 단계입니다.', tip: '?? Tip: 조사 과정에서 작성되는 확인서나 문답서의 내용이 향후 처분의 핵심 근거가 되므로 신중히 답변해야 합니다.' },
                { 
                    name: '사전통지', basis: '행정절차법', 
                    desc: '처분을 내리기 전 당사자에게 미리 알리고, 의견이나 소명을 듣는 절차.', 
                    tip: '?? 주의: 이 단계에서 적극적으로 유리한 증거와 의견서를 제출하여 처분 수위를 낮추는 것이 가장 효과적입니다.',
                    lawTitle: '제21조(처분의 사전 통지)',
                    lawText: `① 행정청은 당사자에게 의무를 부과하거나 권익을 제한하는 처분을 하는 경우에는 미리 다음 각 호의 사항을 당사자등에게 통지하여야 한다.<br>&nbsp;&nbsp;1. 처분의 제목<br>&nbsp;&nbsp;2. 당사자의 성명 또는 명칭과 주소<br>&nbsp;&nbsp;3. 처분하려는 원인이 되는 사실과 처분의 내용 및 법적 근거<br>&nbsp;&nbsp;4. 제3호에 대하여 의견을 제출할 수 있다는 뜻과 의견을 제출하지 아니하는 경우의 처리방법<br>&nbsp;&nbsp;5. 의견제출기관의 명칭과 주소<br>&nbsp;&nbsp;6. 의견제출기한<br>&nbsp;&nbsp;7. 그 밖에 필요한 사항<br><br>② 행정청은 청문을 하려면 청문이 시작되는 날부터 10일 전까지 제1항 각 호의 사항을 당사자등에게 통지하여야 한다. 이 경우 제1항제4호부터 제6호까지의 사항은 청문 주재자의 소속ㆍ직위 및 성명, 청문의 일시 및 장소, 청문에 응하지 아니하는 경우의 처리방법 등 청문에 필요한 사항으로 갈음한다.<br><br>③ 제1항제6호에 따른 기한은 의견제출에 필요한 기간을 10일 이상으로 고려하여 정하여야 한다. &lt;개정 2019. 12. 10.&gt;<br><br>④ 다음 각 호의 어느 하나에 해당하는 경우에는 제1항에 따른 통지를 하지 아니할 수 있다.<br>&nbsp;&nbsp;1. 공공의 안전 또는 복리를 위하여 긴급히 처분을 할 필요가 있는 경우<br>&nbsp;&nbsp;2. 법령등에서 요구된 자격이 없거나 없어지게 되면 반드시 일정한 처분을 하여야 하는 경우에 그 자격이 없거나 없어지게 된 사실이 법원의 재판 등에 의하여 객관적으로 증명된 경우<br>&nbsp;&nbsp;3. 해당 처분의 성질상 의견청취가 현저히 곤란하거나 명백히 불필요하다고 인정될 만한 상당한 이유가 있는 경우<br><br>⑤ 처분의 전제가 되는 사실이 법원의 재판 등에 의하여 객관적으로 증명된 경우 등 제4항에 따른 사전 통지를 하지 아니할 수 있는 구체적인 사항은 대통령령으로 정한다. &lt;신설 2014. 1. 28.&gt;<br><br>⑥ 제4항에 따라 사전 통지를 하지 아니하는 경우 행정청은 처분을 할 때 당사자등에게 통지를 하지 아니한 사유를 알려야 한다. 다만, 신속한 처분이 필요한 경우에는 처분 후 그 사유를 알릴 수 있다. &lt;신설 2014. 12. 30.&gt;<br><br>⑦ 제6항에 따라 당사자등에게 알리는 경우에는 제24조를 준용한다. &lt;신설 2014. 12. 30.&gt;<br><br>[전문개정 2012. 10. 22.]`
                },
                { name: '처분', basis: '행정절차법', desc: '행정처분의 효력이 발생합니다.', tip: '행정심판이나 행정소송의 청구가 가능하며 효력정지를 집행정지시키기 위해서는 1주정도의 시간이 소요된다.' },
                { name: '불복절차', basis: '행정절차법', desc: '행정심판위원회에 심판을 청구하거나 관할 법원에 소송을 제기합니다.', tip: '? 기한: 처분이 있음을 안 날부터 90일, 있은 날부터 180일(소송은 1년) 이내.\n??? 전략: 반드시 집행정지 신청을 병행하세요.' }
            ]
        };

        function renderAccordionInfo(category) {
            const stages = STAGE_CONFIG[category];
            let html = '<div class="timeline-container">';
            
            let currentPhase = '';

            stages.forEach((s, i) => {
                let phaseType = (i >= 3) ? 'appeal' : 'admin';
                let newPhase = (i >= 3) ? '?? 불복 절차' : '?? 행정 절차';
                
                if (currentPhase !== newPhase) {
                    if (currentPhase !== '') {
                        html += `</div>`; 
                    }
                    currentPhase = newPhase;
                    
                    let headerClass = (phaseType === 'appeal') ? 'phase-appeal' : 'phase-admin';
                    let wrapperClass = (phaseType === 'appeal') ? 'wrapper-appeal' : 'wrapper-admin';
                    let title = newPhase + (phaseType === 'admin' && s.basis ? ` (근거법: ${s.basis})` : '');
                    
                    html += `<div class="phase-header ${headerClass}">${title}</div>`;
                    html += `<div class="timeline-wrapper ${wrapperClass}">`;
                }
                
                let itemClass = (phaseType === 'appeal') ? 'phase-appeal-item' : '';
                let activeClass = (i === 0) ? 'expanded active' : '';
                
                html += `
                    <div class="timeline-item ${itemClass} ${activeClass}" onclick="toggleTimeline(this)">
                        <div class="timeline-dot"></div>
                        <div class="timeline-card">
                            <div class="timeline-card-header">
                                <span>${i + 1}. ${s.name}</span>
                                <span class="toggle-icon">▼</span>
                            </div>
                            <div class="timeline-content">
                                <p>${s.desc}</p>
                                ${s.tip ? `<div class="tip-box" style="margin-bottom: 0.8rem; white-space: pre-wrap;">${s.tip}</div>` : ''}
                                ${s.lawText ? `<div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px; font-size: 0.8rem; border-left: 3px solid ${(phaseType === 'appeal') ? '#fca5a5' : '#60a5fa'}; margin-top: 0.5rem;"><strong style="color: ${(phaseType === 'appeal') ? '#fca5a5' : '#60a5fa'};">?? ${s.lawTitle || '관련 법령'}</strong><br><br><span style="color: #cbd5e1; line-height: 1.6;">${s.lawText}</span></div>` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            if (currentPhase !== '') {
                html += `</div>`; 
            }
            html += `</div>`;
            
            processFlowBox.innerHTML = html;
        }

        function updateProcessFlow(val) {
            renderAccordionInfo(val);
            processFlowArea.style.display = 'none';
            processFlowArea.offsetHeight; 
            processFlowArea.style.display = 'block';
        }
    </script>''', html, flags=re.DOTALL)

with codecs.open('public-consult.html', 'w', 'utf-8') as f:
    f.write(html)
