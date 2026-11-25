const supabaseUrl = 'https://clzrbyplzjdrrscctcsl.supabase.co'
        const supabaseKey = 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k'

        const supabaseClient = window.supabase.createClient(
            supabaseUrl,
            supabaseKey
        )

        let words = []
        let currentWord = null

        function cleanWord(str) {
            return str ? str.replace(/_\d+$/, '') : '';
        }
        let meaningVisible = false
        let isTestMode = false

        // Multiple choice state & helpers
        let currentMc = null;
        let mcWrongClicked = false;

        function parseMultipleChoice(example) {
            if (!example) return null;
            
            // Check if there are choices like A. B. C. D. or A) B) C) D)
            if (!/([A-E]|[1-5])[\.\)]/i.test(example)) return null;

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = example;
            
            let htmlContent = tempDiv.innerHTML
                .replace(/<br\s*\/?>/gi, '\n')
                .replace(/<\/p>/gi, '\n')
                .replace(/<p[^>]*>/gi, '');
                
            tempDiv.innerHTML = htmlContent;
            let plainText = tempDiv.textContent || tempDiv.innerText || '';
            
            let lines = plainText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
            
            let question = '';
            let options = [];
            let correctIndex = -1;
            
            for (let i = 0; i < lines.length; i++) {
                let line = lines[i];
                let match = line.match(/^([A-E]|[1-5])[\.\)]\s*(.*)$/i);
                if (match) {
                    let label = match[1];
                    let text = match[2];
                    let isCorrect = false;
                    
                    if (text.includes('(정답') || text.includes('정답!') || text.includes('정답')) {
                        isCorrect = true;
                        text = text.replace(/\(정답.*?\)/g, '').replace(/정답.*/g, '').trim();
                        text = text.replace(/[\(\)\!\s]+$/, '').trim();
                    }
                    
                    options.push({
                        label: label.toUpperCase(),
                        text: text,
                        isCorrect: isCorrect
                    });
                    
                    if (isCorrect) {
                        correctIndex = options.length - 1;
                    }
                } else {
                    if (question) {
                        question += '<br>' + line;
                    } else {
                        question = line;
                    }
                }
            }
            
            if (options.length > 0) {
                // If correct option is not explicitly marked with "(정답)", check if option matches currentWord.word
                if (correctIndex === -1 && typeof currentWord !== 'undefined' && currentWord) {
                    const cleanTarget = cleanWord(currentWord.word).toLowerCase();
                    for (let i = 0; i < options.length; i++) {
                        if (options[i].text.toLowerCase() === cleanTarget) {
                            options[i].isCorrect = true;
                            correctIndex = i;
                            break;
                        }
                    }
                }
                
                return {
                    question: question,
                    options: options,
                    correctIndex: correctIndex
                };
            }
            
            return null;
        }

        function renderMultipleChoice(example) {
            const mc = parseMultipleChoice(example);
            if (!mc) {
                return example || '';
            }
            
            currentMc = mc;
            mcWrongClicked = false;
            
            return `
                <div class="mc-container">
                    <div class="mc-question">${mc.question}</div>
                    <div class="mc-options">
                        ${mc.options.map((opt, idx) => `
                            <button class="mc-option-btn" id="mc-opt-${idx}" onclick="selectMcOption(${idx})">
                                <span class="mc-label">${opt.label}</span>
                                <span class="mc-text">${opt.text}</span>
                            </button>
                        `).join('')}
                    </div>
                    <div class="mc-feedback hidden" id="mc-feedback"></div>
                </div>
            `;
        }

        async function selectMcOption(idx) {
            if (!currentMc || isSubmitting) return;
            
            const feedbackEl = document.getElementById('mc-feedback');
            const clickedBtn = document.getElementById(`mc-opt-${idx}`);
            const option = currentMc.options[idx];
            
            if (option.isCorrect) {
                isSubmitting = true;
                
                // Mark correct option
                clickedBtn.classList.add('mc-correct');
                feedbackEl.innerHTML = "정답이에요! 🎉";
                feedbackEl.className = "mc-feedback success";
                feedbackEl.classList.remove('hidden');
                
                // Disable all options
                currentMc.options.forEach((_, i) => {
                    const btn = document.getElementById(`mc-opt-${i}`);
                    if (btn) btn.disabled = true;
                });
                
                // If they got it right on the first try, increase combo
                if (!mcWrongClicked) {
                    comboCount++;
                } else {
                    comboCount = 0;
                }
                
                dailyProgress++;
                saveStats();
                
                // Trigger confetti
                confetti({
                    particleCount: 150,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#ffc3a0', '#ffafbd', '#84fab0', '#8fd3f4', '#f6d365']
                });
                
                // Speak the word automatically
                speakWord(currentWord.word);
                
                // Automatically show the meaning in DOM
                const meaningEl = document.querySelector('.meaning');
                if (meaningEl) {
                    meaningEl.classList.remove('hidden');
                }
                meaningVisible = true;

                // Reveal the hidden word if it was a multiple choice question
                const secretWordEl = document.getElementById('secret-word-display');
                if (secretWordEl) {
                    secretWordEl.innerText = cleanWord(currentWord.word);
                    secretWordEl.style = '';
                }
                const secretSpeakerEl = document.getElementById('secret-speaker-icon');
                if (secretSpeakerEl) {
                    secretSpeakerEl.classList.remove('hidden');
                }
                
                await updateMemorizedState();
                await insertStudyLog(currentWord.subject || '영어', cleanWord(currentWord.word), '객관식 퀴즈 정답 완료');
                
                setTimeout(() => {
                    const memorizedWord = currentWord;
                    words = words.filter(w => w.id !== currentWord.id);
                    memorizedWords.push(memorizedWord);
                    
                    isSubmitting = false;
                    mcWrongClicked = false;
                    meaningVisible = false;
                    
                    setupSubjects();
                    loadMyHistory();
                }, 1800);
                
            } else {
                // Mark incorrect option
                clickedBtn.classList.add('mc-incorrect');
                clickedBtn.disabled = true;
                
                mcWrongClicked = true;
                comboCount = 0;
                saveStats();
                
                feedbackEl.innerHTML = "앗, 틀렸어요! 다른 답을 골라보세요! 😉";
                feedbackEl.className = "mc-feedback fail";
                feedbackEl.classList.remove('hidden');
            }
        }
        let isIrregularTestMode = false
        
        let wordsBySubject = {}
        let subjects = []
        let currentSubjectIndex = 0

        let memorizedWords = []
        let isQuizMode = false
        let quizOptions = []
        let quizTargetWord = null
        let userNickname = ''
        let geminiApiKey = ''
        
        let isMathAiMode = false;
        let mathAiResult = null;
        let isMathLoading = false;
        let isSubmitting = false;

        // Reward System State
        let comboCount = 0;
        const dailyGoal = 5;
        let dailyProgress = 0;

        function initStats() {
            const todayStr = new Date().toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'short' });
            userNickname = localStorage.getItem('study_currentUser') || '';
            
            // 기존 '우리딸' 계정명을 '아람'으로 마이그레이션
            if (userNickname === '우리딸') {
                userNickname = '아람';
                localStorage.setItem('study_currentUser', '아람');
            }

            if (!userNickname) {
                showNameModal();
            } else {
                loadStats();
                updateHeader(todayStr);
                updateStatsUI();
                if (userNickname === '아빠' || userNickname === '희진부모') {
                    switchMainTab('life');
                } else if (userNickname === '희진') {
                    switchMainTab('study');
                }
                loadMyHistory();
                loadHabitRecords();
            }
        }

        function loadStats() {
            // 과거 버전 데이터(studyStats, geminiApiKey) 정리 및 마이그레이션
            const oldDataStr = localStorage.getItem('studyStats');
            if (oldDataStr) {
                try {
                    const oldData = JSON.parse(oldDataStr);
                    // 기존 닉네임과 새 로그인 계정이 연관성이 있으면 데이터 복원
                    if (oldData.nickname && (
                        (userNickname === '아빠' && oldData.nickname.includes('아빠')) ||
                        (userNickname === '아람' && (oldData.nickname.includes('딸') || oldData.nickname.includes('아람'))) ||
                        (userNickname === '친구' && oldData.nickname.includes('친구'))
                    )) {
                        localStorage.setItem('studyStats_' + userNickname, oldDataStr);
                    }
                } catch(e) {}
                // 마이그레이션 후 과거 데이터는 깔끔하게 삭제
                localStorage.removeItem('studyStats');
            }
            // 이제 필요 없는 API 키도 깔끔하게 삭제
            localStorage.removeItem('geminiApiKey');

            const savedData = JSON.parse(localStorage.getItem('studyStats_' + userNickname)) || {};
            if (savedData.date !== new Date().toLocaleDateString()) {
                dailyProgress = 0;
                comboCount = 0;
            } else {
                dailyProgress = savedData.progress || 0;
                comboCount = savedData.combo || 0;
            }

            // 상식 퀴즈 저금통 데이터 로드
            const savedQuizState = JSON.parse(localStorage.getItem('studyQuizState_' + userNickname)) || {};
            const todayStr = getLocalDateStr(new Date());
            quizBankState.totalAnswered = savedQuizState.totalAnswered || 0;
            quizBankState.currentPoints = savedQuizState.currentPoints || 0;
            if (savedQuizState.todayDate === todayStr) {
                quizBankState.todayAnswered = savedQuizState.todayAnswered || 0;
            } else {
                quizBankState.todayAnswered = 0;
                quizBankState.todayDate = todayStr;
            }
        }

        function showNameModal() {
            const modalHtml = `
                <div class="modal-overlay" id="name-modal-overlay">
                    <div class="name-modal">
                        <h2>비밀번호를 입력해주세요 🔒</h2>
                        <input type="password" id="nickname-input" class="name-input" placeholder="비밀번호 4자리" onkeypress="if(event.key === 'Enter') saveNickname()">
                        <button class="name-btn" onclick="saveNickname()">로그인 💖</button>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            document.getElementById('nickname-input').focus();
        }

        function saveNickname() {
            const input = document.getElementById('nickname-input').value.trim();
            if(!input) return;
            
            if (input === '4321') {
                userNickname = '아빠';
            } else if (input === '1234') {
                userNickname = '아람';
            } else if (input === '1111') {
                userNickname = '희진';
            } else if (input === '0000') {
                userNickname = '희진부모';
            } else {
                alert('비밀번호가 틀렸습니다! 다시 입력해주세요. 😊');
                document.getElementById('nickname-input').value = '';
                return;
            }
            
            localStorage.setItem('study_currentUser', userNickname);
            loadStats();

            const overlay = document.getElementById('name-modal-overlay');
            if (overlay) overlay.remove();
            
            const todayStr = new Date().toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'short' });
            updateHeader(todayStr);
            updateStatsUI();
            if (userNickname === '아빠' || userNickname === '희진부모') {
                switchMainTab('life');
            } else if (userNickname === '희진') {
                switchMainTab('study');
            }
            loadMyHistory();
            loadWords();
            loadHabitRecords();
        }

        function logout() {
            localStorage.removeItem('study_currentUser');
            location.reload();
        }

        function scrollToHabit() {
            switchMainTab('life');
            const el = document.getElementById('habit-container');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function switchMainTab(tab) {
            currentMainTab = tab;
            const btnStudy = document.getElementById('nav-btn-study');
            const btnLife = document.getElementById('nav-btn-life');
            const mainModeNav = document.querySelector('.main-mode-nav');
            const statsBar = document.getElementById('stats-bar');
            const cardWrapper = document.getElementById('card-wrapper');
            const lastUpdated = document.getElementById('last-updated');
            const habitContainer = document.getElementById('habit-container');
            const historyContainer = document.getElementById('history-container');

            // 아빠 및 희진부모 계정일 때는 상단 모드 전환 탭을 숨기고 코칭/리포트 화면만 표시
            if (userNickname === '아빠' || userNickname === '희진부모') {
                if (mainModeNav) mainModeNav.style.display = 'none';
                if (statsBar) statsBar.style.display = 'none';
                if (cardWrapper) cardWrapper.style.display = 'none';
                if (lastUpdated) lastUpdated.style.display = 'none';
                if (historyContainer) historyContainer.style.display = 'none';
                if (habitContainer) {
                    habitContainer.style.display = 'block';
                    habitContainer.classList.remove('hidden');
                }
                return;
            } else if (userNickname === '희진') {
                // 희진(학생) 계정: 퀴즈만 풀고 생활코칭/가정사생활 탭 완전 숨김
                if (mainModeNav) mainModeNav.style.display = 'none';
                if (statsBar) statsBar.style.display = '';
                if (cardWrapper) cardWrapper.style.display = '';
                if (lastUpdated) lastUpdated.style.display = '';
                if (historyContainer) historyContainer.style.display = '';
                if (habitContainer) habitContainer.style.display = 'none';
                return;
            } else {
                if (mainModeNav) mainModeNav.style.display = '';
            }

            if (tab === 'study') {
                if (btnStudy) btnStudy.classList.add('active');
                if (btnLife) btnLife.classList.remove('active');
                if (statsBar) statsBar.style.display = '';
                if (cardWrapper) cardWrapper.style.display = '';
                if (lastUpdated) lastUpdated.style.display = '';
                if (historyContainer) historyContainer.style.display = '';
                if (habitContainer) habitContainer.style.display = 'none';
            } else {
                if (btnStudy) btnStudy.classList.remove('active');
                if (btnLife) btnLife.classList.add('active');
                if (statsBar) statsBar.style.display = 'none';
                if (cardWrapper) cardWrapper.style.display = 'none';
                if (lastUpdated) lastUpdated.style.display = 'none';
                if (historyContainer) historyContainer.style.display = 'none';
                if (habitContainer) {
                    habitContainer.style.display = 'block';
                    habitContainer.classList.remove('hidden');
                }
            }
        }

        function updateHeader(dateStr) {
            let habitNavBtn = '';
            if (userNickname === '아빠') {
                habitNavBtn = `<button onclick="scrollToHabit()" style="background:linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%); border:none; color:white; padding:4px 12px; border-radius:12px; font-size:13px; font-weight:bold; margin-left:6px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.15); font-family:'Jua', sans-serif;">📋 출석·공부 체크</button>`;
                document.getElementById('date-stats-text').innerText = `${dateStr} | 아빠 관리자 모드`;
            } else if (userNickname === '희진부모') {
                habitNavBtn = `<button onclick="scrollToHabit()" style="background:linear-gradient(135deg, #6366f1 0%, #a855f7 100%); border:none; color:white; padding:4px 12px; border-radius:12px; font-size:13px; font-weight:bold; margin-left:6px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.15); font-family:'Jua', sans-serif;">📊 희진이 퀴즈 리포트</button>`;
                document.getElementById('date-stats-text').innerText = `${dateStr} | 희진이 학부모 모드`;
            } else if (userNickname === '희진') {
                habitNavBtn = '';
                document.getElementById('date-stats-text').innerText = `${dateStr} | 희진이 상식 퀴즈 모드`;
            } else if (userNickname) {
                habitNavBtn = `<button onclick="scrollToHabit()" style="background:linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); border:none; color:white; padding:4px 12px; border-radius:12px; font-size:13px; font-weight:bold; margin-left:6px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.15); font-family:'Jua', sans-serif;">🌟 내 출석·공부 달력</button>`;
                document.getElementById('date-stats-text').innerText = `${dateStr} | 오늘 암기: ${dailyProgress}개`;
            }
            document.getElementById('greeting-text').innerHTML = `환영해요, ${userNickname}님! 💖 ${habitNavBtn} <button onclick="logout()" style="background:rgba(255,255,255,0.3); border:none; color:white; padding:4px 12px; border-radius:12px; font-size:14px; font-weight:bold; margin-left:8px; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.1); font-family:'Nunito', sans-serif;">로그아웃</button>`;
        }

        function saveStats() {
            const today = new Date().toLocaleDateString();
            localStorage.setItem('studyStats_' + userNickname, JSON.stringify({
                date: today,
                progress: dailyProgress,
                combo: comboCount,
                nickname: userNickname
            }));
            localStorage.setItem('studyQuizState_' + userNickname, JSON.stringify(quizBankState));
            updateStatsUI();
            const todayStr = new Date().toLocaleDateString('ko-KR', { month: 'long', day: 'numeric', weekday: 'short' });
            updateHeader(todayStr);
        }

        function updateStatsUI() {
            const comboEl = document.getElementById('combo-badge');
            if (comboCount >= 2) {
                comboEl.classList.remove('hidden');
                comboEl.innerHTML = `🔥 ${comboCount} Combo!`;
                // Re-trigger animation
                comboEl.style.animation = 'none';
                setTimeout(() => comboEl.style.animation = '', 10);
            } else {
                comboEl.classList.add('hidden');
            }

            const progressEl = document.getElementById('progress-bar');
            const textEl = document.getElementById('progress-text');
            const percent = Math.min((dailyProgress / dailyGoal) * 100, 100);
            progressEl.style.width = `${percent}%`;
            
            // 그래픽(보석)으로 목표 표시 (중2 맞춤형 퀘스트 스타일)
            let graphicGoal = '';
            for(let i = 0; i < dailyGoal; i++) {
                if (i < dailyProgress) {
                    graphicGoal += '<span style="display:inline-block; margin: 0 2px; transform:scale(1.1); text-shadow: 0 0 5px rgba(0,0,0,0.2); transition:all 0.3s;">💎</span>';
                } else {
                    graphicGoal += '<span style="display:inline-block; margin: 0 2px; opacity:0.35; filter:grayscale(100%); transition:all 0.3s;">💎</span>';
                }
            }
            
            if (dailyProgress >= dailyGoal) {
                textEl.innerHTML = `🎉 퀘스트 클리어! ${graphicGoal} 👑`;
                progressEl.style.background = 'linear-gradient(90deg, #f6d365 0%, #fda085 100%)';
            } else {
                textEl.innerHTML = `일일 퀘스트: ${graphicGoal}`;
                progressEl.style.background = 'linear-gradient(90deg, #84fab0 0%, #8fd3f4 100%)';
            }
        }

        async function loadWords() {
            // 부모 계정(아빠, 희진부모)은 학생용 단어/상식퀴즈 카드를 로드할 필요 없음
            if (userNickname === '아빠' || userNickname === '희진부모') {
                const cardWrapper = document.getElementById('card-wrapper');
                const lastUpdated = document.getElementById('last-updated');
                const statsBar = document.getElementById('stats-bar');
                const mainModeNav = document.querySelector('.main-mode-nav');
                if (cardWrapper) { cardWrapper.innerHTML = ''; cardWrapper.style.display = 'none'; }
                if (lastUpdated) lastUpdated.style.display = 'none';
                if (statsBar) statsBar.style.display = 'none';
                if (mainModeNav) mainModeNav.style.display = 'none';
                return;
            }

            const { data, error } = await supabaseClient
                .from('study_words')
                .select('*')
                .order('created_at', { ascending: false })

            if (error) {
                console.log(error)
                return
            }
            const youtubeLinks = data.filter(w => w.subject === 'YOUTUBE_LINK');
            const IGNORED_SUBJECTS = ['YOUTUBE_LINK', 'DAILY_HABIT', 'FAMILY_SCHEDULE', 'CHILD_REWARD'];
            const studyData = data.filter(w => {
                const s = (w.subject || '').trim().toUpperCase();
                return !IGNORED_SUBJECTS.includes(s) && !s.includes('SCHEDULE') && !s.includes('HABIT') && !s.includes('REWARD');
            });

            words = studyData.filter(w => !(w.memorized_users && w.memorized_users.includes(userNickname)))
            memorizedWords = studyData.filter(w => w.memorized_users && w.memorized_users.includes(userNickname))

            if (studyData.length > 0) {
                const latestDate = new Date(studyData[0]?.created_at || data[0].created_at);
                document.getElementById('last-updated').innerHTML = `
                    최근 업데이트: ${latestDate.toLocaleDateString()} ${latestDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}<br>
                    <span style="font-weight: bold; color: rgba(255,255,255,0.9); display: inline-block; margin-top: 5px;">
                        저장된 단어: 총 ${studyData.length}개 (남은 단어: ${words.length}개)
                    </span>
                `;
            } else {
                document.getElementById('last-updated').innerHTML = `저장된 단어가 없습니다.`;
            }

            // renderYoutubeLinks removed
            setupSubjects()
        }

        function setupSubjects() {
            wordsBySubject = {}
            words.forEach(w => {
                const subj = w.subject || '기타'
                if (!wordsBySubject[subj]) {
                    wordsBySubject[subj] = []
                }
                wordsBySubject[subj].push(w)
            })

            subjects = Object.keys(wordsBySubject)

            pickNextWord()
            renderCard()
        }

        function renderCard() {
            const cardContainer = document.getElementById('card-wrapper');
            if (!cardContainer) return;

            // 학부모 관리자 계정(아빠, 희진부모)일 때는 학생용 퀴즈 풀이 카드 자체를 완전히 숨김
            if (userNickname === '아빠' || userNickname === '희진부모') {
                cardContainer.innerHTML = '';
                cardContainer.style.display = 'none';
                return;
            }

            // 상식 퀴즈 100원 저금통 모드 렌더링
            renderCommonKnowledgeQuiz(cardContainer);
        }

        // ===================================================
        // 🧠 중학생 맞춤 상식 퀴즈 & 50원 저금통 뷰 로직
        // ===================================================
        function renderCommonKnowledgeQuiz(container) {
            const quiz = COMMON_QUIZ_POOL[currentQuizIndex % COMMON_QUIZ_POOL.length];
            const currentWon = quizBankState.currentPoints || 0;
            const progressCount = Math.floor(currentWon / 50);
            const remainingToCoupon = Math.max(0, 40 - progressCount);
            const percent = Math.min(100, Math.round((currentWon / 2000) * 100));
            const todayCount = quizBankState.todayAnswered || 0;
            const isTodayCapReached = todayCount >= 10;

            // 저금통 게이지 HTML
            const piggyBankHtml = `
                <div class="piggy-bank-container">
                    <div class="piggy-bank-header">
                        <div class="piggy-bank-title">🪙 ${(userNickname || "학생")}의 상식 저금통 (1문제 = 50원!)</div>
                        <div class="piggy-bank-badge">${currentWon.toLocaleString()}원 / 2,000원</div>
                    </div>
                    <div class="piggy-bar-bg">
                        <div class="piggy-bar-fill" style="width: ${percent}%;"></div>
                    </div>
                    <div class="piggy-bank-meta">
                        <span>오늘 적립 문제: <strong>${Math.min(10, todayCount)} / 10개</strong> ${isTodayCapReached ? '<span style="color:#10b981; font-weight:bold;">(오늘 저금 완료! 500원 달성 👏)</span>' : '(하루 최대 500원)'}</span>
                        <span style="color:#e11d48; font-weight:bold;">${remainingToCoupon > 0 ? remainingToCoupon + '문제 더 풀면 2,000원 쿠폰 지급!' : '🎉 2,000원 쿠폰 발급 완료!'}</span>
                    </div>
                </div>
            `;

            // 4지선다 옵션 버튼 HTML
            const optionsHtml = quiz.options.map((opt, idx) => {
                let btnClass = 'quiz-opt-btn';
                if (isQuizAnswerSubmitted) {
                    if (idx === quiz.answer) {
                        btnClass += ' correct';
                    } else if (selectedQuizOption === idx) {
                        btnClass += ' wrong';
                    }
                } else if (selectedQuizOption === idx) {
                    btnClass += ' selected';
                }

                return `
                    <button type="button" class="${btnClass}" onclick="selectQuizOption(${idx})" ${isQuizAnswerSubmitted ? 'disabled' : ''}>
                        <span class="quiz-opt-num">${idx + 1}</span>
                        <span class="quiz-opt-text">${escapeHtml(opt)}</span>
                    </button>
                `;
            }).join('');

            // 하단 액션 버튼 및 해설 HTML
            let actionHtml = '';
            if (!isQuizAnswerSubmitted) {
                actionHtml = `
                    <div style="margin-top:16px;">
                        <button type="button" class="quiz-submit-btn" onclick="submitQuizAnswer()" ${selectedQuizOption === null ? 'disabled' : ''}>
                            정답 확인하기 (맞히면 +50원! 🪙)
                        </button>
                    </div>
                `;
            } else {
                const isCorrect = (selectedQuizOption === quiz.answer);
                let rewardText = '';
                if (isCorrect) {
                    if (todayCount <= 10) {
                        rewardText = '🎉 딩동댕! 정답입니다! (+50원 적립 🪙)';
                    } else {
                        rewardText = '🎉 딩동댕! 정답입니다! (오늘 500원 적립 완료 ✨)';
                    }
                } else {
                    rewardText = '앗! 아쉽지만 오답이에요! 💡';
                }

                actionHtml = `
                    <div class="quiz-feedback-box ${isCorrect ? 'correct' : 'wrong'}">
                        <div class="feedback-title">${rewardText}</div>
                        <div class="feedback-desc">${escapeHtml(quiz.explanation)}</div>
                        <button type="button" class="quiz-next-btn" onclick="nextCommonQuiz()">
                            다음 문제 풀기 ▶
                        </button>
                    </div>
                `;
            }

            container.innerHTML = `
                ${piggyBankHtml}
                <div class="quiz-card">
                    <div class="quiz-card-top">
                        <span class="quiz-cat-tag">${escapeHtml(quiz.category)}</span>
                        <span class="quiz-num-tag">Q. 문제 ${ (currentQuizIndex % COMMON_QUIZ_POOL.length) + 1 }</span>
                    </div>
                    <div class="quiz-question-text">
                        ${escapeHtml(quiz.question)}
                    </div>
                    <div class="quiz-options-list">
                        ${optionsHtml}
                    </div>
                    ${actionHtml}
                </div>
            `;
        }

        function selectQuizOption(idx) {
            if (isQuizAnswerSubmitted) return;
            selectedQuizOption = idx;
            renderCard();
        }

        async function submitQuizAnswer() {
            if (selectedQuizOption === null || isQuizAnswerSubmitted) return;
            isQuizAnswerSubmitted = true;
            const quiz = COMMON_QUIZ_POOL[currentQuizIndex % COMMON_QUIZ_POOL.length];
            const isCorrect = (selectedQuizOption === quiz.answer);

            // 풀이 기록을 Supabase study_logs에 실시간 저장 (아빠 리포트 및 오답노트용)
            logQuizAnswerToDb(quiz, selectedQuizOption, isCorrect);

            if (isCorrect) {
                const currentTodayAnswered = quizBankState.todayAnswered || 0;
                
                // 하루 최대 10개(=500원, 1문제=50원)까지만 포인트 적립!
                if (currentTodayAnswered < 10) {
                    quizBankState.currentPoints = (quizBankState.currentPoints || 0) + 50;
                }
                
                quizBankState.totalAnswered = (quizBankState.totalAnswered || 0) + 1;
                quizBankState.todayAnswered = currentTodayAnswered + 1;
                dailyProgress++;

                // 2000원(40개) 달성 시 2000원 쿠폰 자동 발급!
                if (quizBankState.currentPoints >= 2000) {
                    await grantQuizRewardCoupon();
                    quizBankState.currentPoints = 0; // 리셋 후 다음 2000원 저금 시작
                }

                saveStats();

                confetti({
                    particleCount: 120,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#fbbf24', '#f59e0b', '#10b981', '#60a5fa']
                });
            } else {
                saveStats();
            }

            renderCard();
        }

                async function logQuizAnswerToDb(quiz, chosenOptionIdx, isCorrect) {
            try {
                const logDetail = JSON.stringify({
                    category: quiz.category,
                    question: quiz.question,
                    chosen: quiz.options[chosenOptionIdx],
                    answer: quiz.options[quiz.answer],
                    isCorrect: isCorrect,
                    explanation: quiz.explanation,
                    user: userNickname || '아람'
                });

                await supabaseClient.from('study_logs').insert([{
                    subject: 'COMMON_QUIZ',
                    content: `[${quiz.category}] ${quiz.question.substring(0, 50)}...`,
                    detail: logDetail,
                    creator: userNickname || '아람'
                }]);
            } catch(e) {
                console.error("logQuizAnswerToDb error:", e);
            }
        }


        function nextCommonQuiz() {
            currentQuizIndex = (currentQuizIndex + 1) % COMMON_QUIZ_POOL.length;
            selectedQuizOption = null;
            isQuizAnswerSubmitted = false;
            renderCard();
        }

        // 2,000원 상식 저금통 달성 시 쿠폰 발급 함수
        async function grantQuizRewardCoupon() {
            const couponId = `REWARD_QUIZ_2000_${Date.now()}`;
            const couponData = {
                title: questConfig.quizRewardTitle || '🏪 편의점 2,000원 상품권 (또는 현금 2,000원)',
                type: 'QUIZ_20_ANSWER',
                rewardDesc: questConfig.quizRewardDesc || '상식 퀴즈 20문제 정답(2,000원 적립) 달성 축하 보상! 🪙',
                date: getLocalDateStr(new Date()),
                status: 'PENDING',
                created_at: new Date().toISOString()
            };

            try {
                await supabaseClient
                    .from('study_words')
                    .insert([{
                        word: couponId,
                        meaning: JSON.stringify(couponData),
                        subject: 'CHILD_REWARD',
                        category: '아람',
                        example: userNickname || '아람'
                    }]);

                rewardCoupons.unshift({ id: couponId, ...couponData });

                confetti({
                    particleCount: 200,
                    spread: 100,
                    origin: { y: 0.5 },
                    colors: ['#f59e0b', '#ef4444', '#10b981', '#8b5cf6']
                });

                alert("🎉 축하합니다! 상식 저금통 2,000원 달성! 🏪 편의점 2,000원 쿠폰이 보물상자에 발급되었습니다! 💖");
            } catch(e) {
                console.error("Grant quiz coupon error:", e);
            }
        }
async function insertStudyLog(subject, content, detail) {
            await supabaseClient.from('study_logs').insert([{
                subject: subject,
                content: content,
                detail: detail,
                creator: userNickname
            }]);
        }

        async function markAsMemorizedManually() {
            if (isSubmitting) return;
            isSubmitting = true;
            await updateMemorizedState();
            await insertStudyLog(currentWord.subject || '기타', currentWord.word, '직접 완료 처리');
            finalizeTest();
            isSubmitting = false;
        }

        async function updateMemorizedState() {
            const newUsers = currentWord.memorized_users ? [...currentWord.memorized_users] : [];
            if (!newUsers.includes(userNickname)) {
                newUsers.push(userNickname);
            }

            const { error } = await supabaseClient
                .from('study_words')
                .update({ memorized_users: newUsers })
                .eq('id', currentWord.id);
                
            if (error) {
                console.error("DB 업데이트 에러:", error);
                alert("서버 저장 중 오류가 발생했어요. 다시 시도해주세요! 😥");
                return false;
            }
            return true;
        }

        function finalizeTest() {
            comboCount++;
            dailyProgress++;
            saveStats();

            confetti({
                particleCount: 150,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#ffc3a0', '#ffafbd', '#84fab0', '#8fd3f4', '#f6d365']
            });
            
            const memorizedWord = currentWord;
            words = words.filter(w => w.id !== currentWord.id);
            memorizedWords.push(memorizedWord);
            isTestMode = false;
            isIrregularTestMode = false;
            isMathAiMode = false;
            mathAiResult = null;
            setupSubjects();
            loadMyHistory();
        }

        function toggleMeaning() {
            meaningVisible = !meaningVisible
            renderCard()
        }
        
        function toggleTestMode() {
            isTestMode = true
            renderCard()
        }

        function toggleIrregularTestMode() {
            isIrregularTestMode = true
            renderCard()
        }
        
        function cancelTest() {
            isTestMode = false
            isIrregularTestMode = false
            isMathAiMode = false
            renderCard()
        }
        
        async function checkTest() {
            if (isSubmitting) return;
            const inputVal = document.getElementById('test-input').value.trim();
            if (inputVal.toLowerCase() === cleanWord(currentWord.word).toLowerCase()) {
                isSubmitting = true;
                const success = await updateMemorizedState();
                if(!success) { isSubmitting = false; return; }

                await insertStudyLog(currentWord.subject || '영어', cleanWord(currentWord.word), '스펠링 테스트 완료');
                finalizeTest();
                isSubmitting = false;
            } else {
                // Combo Breaks
                comboCount = 0;
                saveStats();

                alert("앗, 틀렸어요! 다시 한 번 시도해볼까요? 😉");
                const inputEl = document.getElementById('test-input');
                inputEl.value = '';
                inputEl.focus();
            }
        }

        async function checkIrregularTest() {
            if (isSubmitting) return;
            const inputVal = document.getElementById('irregular-test-input').value.trim();
            
            // 공백, 쉼표, 하이픈 등 기호 무시하고 소문자로 알파벳만 비교 (또는 한글도 포함)
            const normalizedInput = inputVal.toLowerCase().replace(/[\s\-\,\.]/g, '');
            const normalizedTarget = currentWord.irregular.toLowerCase().replace(/[\s\-\,\.]/g, '');

            if (normalizedInput === normalizedTarget) {
                isSubmitting = true;
                const success = await updateMemorizedState();
                if(!success) { isSubmitting = false; return; }

                await insertStudyLog(currentWord.subject || '영어', cleanWord(currentWord.word), '불규칙 변화 테스트 완료');
                finalizeTest();
                isSubmitting = false;
            } else {
                comboCount = 0;
                saveStats();

                alert("앗, 틀렸어요! 불규칙 형태를 다시 한 번 확인해볼까요? 😉");
                const inputEl = document.getElementById('irregular-test-input');
                inputEl.value = '';
                inputEl.focus();
            }
        }

        function startQuiz() {
            if (memorizedWords.length < 4) {
                alert("앗! 퀴즈를 풀려면 최소 4개의 단어를 암기해야 해요! (현재 암기완료: " + memorizedWords.length + "개)");
                return;
            }
            isQuizMode = true;
            
            // Pick 1 target from memorizedWords
            const targetIndex = Math.floor(Math.random() * memorizedWords.length);
            quizTargetWord = memorizedWords[targetIndex];
            
            // Pick 3 distractors
            let allAvailable = [...words, ...memorizedWords].filter(w => w.id !== quizTargetWord.id);
            allAvailable.sort(() => 0.5 - Math.random());
            
            const targetClean = cleanWord(quizTargetWord.word).toLowerCase();
            let uniqueDistractors = [];
            let seenCleanWords = new Set([targetClean]);
            
            for (let w of allAvailable) {
                const wClean = cleanWord(w.word).toLowerCase();
                if (!seenCleanWords.has(wClean)) {
                    uniqueDistractors.push(w);
                    seenCleanWords.add(wClean);
                    if (uniqueDistractors.length === 3) break;
                }
            }
            if (uniqueDistractors.length < 3) {
                uniqueDistractors = allAvailable.slice(0, 3);
            }
            
            quizOptions = [quizTargetWord, ...uniqueDistractors];
            quizOptions.sort(() => 0.5 - Math.random());
            
            renderCard();
        }

        async function submitQuiz(selectedWord) {
            if (isSubmitting) return;
            if (selectedWord === quizTargetWord.word) {
                isSubmitting = true;
                confetti({
                    particleCount: 100,
                    spread: 60,
                    origin: { y: 0.6 }
                });
                await insertStudyLog(quizTargetWord.subject || '복습', quizTargetWord.word, '복습 퀴즈 정답');
                alert("정답이에요! 🎉 멋져요!");
                setTimeout(() => {
                    isSubmitting = false;
                    startQuiz();
                }, 500);
            } else {
                alert(`앗, 틀렸어요! 😥 정답은 '${quizTargetWord.word}' 였어요.`);
            }
        }

        function cancelQuiz() {
            isQuizMode = false;
            renderCard();
        }

        function pickNextWord() {
            if (subjects.length === 0) return

            const subj = subjects[currentSubjectIndex]
            currentSubjectIndex++
            if (currentSubjectIndex >= subjects.length) {
                currentSubjectIndex = 0
            }

            const list = wordsBySubject[subj]
            const randomIndex = Math.floor(Math.random() * list.length)
            currentWord = list[randomIndex]
        }

        async function startMathAiMode() {
            isMathAiMode = true;
            isMathLoading = true;
            mathAiResult = null;
            renderCard();

            try {
                const response = await fetch('/api/math', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ word: currentWord.word })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`상태 코드: ${response.status}, 내용: ${errorText}`);
                }

                mathAiResult = await response.json();
            } catch (err) {
                console.error(err);
                alert("AI 문제 생성에 실패했습니다.\n사유: " + err.message);
                isMathAiMode = false;
            } finally {
                isMathLoading = false;
                renderCard();
            }
        }

        async function finishMathAi() {
            if (isSubmitting) return;
            isSubmitting = true;
            const success = await updateMemorizedState();
            if(!success) { isSubmitting = false; return; }
            
            await insertStudyLog(currentWord.subject || '수학', cleanWord(currentWord.word), 'AI 맞춤 수학 문제 풀이 완료');
            finalizeTest();
            isSubmitting = false;
        }

        function nextWord() {
            meaningVisible = false
            isMathAiMode = false
            pickNextWord()
            renderCard()
        }

        function speakWord(text) {
            text = cleanWord(text);
            if ('speechSynthesis' in window) {
                // 기존 재생중인 음성 취소
                window.speechSynthesis.cancel();
                
                // 한글 제거 (영어 발음 기호나 기타 텍스트만 남김)
                const englishOnly = text.replace(/[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]/g, '').trim();
                
                if (!englishOnly) return;
                
                const utterance = new SpeechSynthesisUtterance(englishOnly);
                
                // 중학생 학습용 추천 목소리 적용 (자동)
                const voices = window.speechSynthesis.getVoices();
                const recommendedVoices = ['Google US English', 'Samantha', 'Microsoft Zira - English (United States)', 'Microsoft Zira', 'Alex'];
                
                const bestVoice = voices.find(v => recommendedVoices.includes(v.name));
                if (bestVoice) {
                    utterance.voice = bestVoice;
                } else {
                    // 추천 목소리가 없으면 기본 영어 목소리
                    const fallbackVoice = voices.find(v => v.lang.startsWith('en') && v.default) || voices.find(v => v.lang.startsWith('en'));
                    if (fallbackVoice) {
                        utterance.voice = fallbackVoice;
                    } else {
                        utterance.lang = 'en-US';
                    }
                }

                utterance.rate = 0.85;    // 약간 천천히 (아이들이 듣기 편하게)
                utterance.pitch = 1.1;    // 살짝 높은 톤으로 밝게
                
                window.speechSynthesis.speak(utterance);
            } else {
                alert("앗! 지금 사용 중인 브라우저에서는 발음 듣기가 안 돼요. 😥 (크롬/사파리를 추천해요)");
            }
        }

        async function loadMyHistory() {
            if (!userNickname) return;
            
            const targetDate = new Date();
            targetDate.setDate(targetDate.getDate() - 6);
            targetDate.setHours(0, 0, 0, 0);
            const targetIso = targetDate.toISOString();

            const { data, error } = await supabaseClient
                .from('study_logs')
                .select('*')
                .eq('creator', userNickname)
                .gte('created_at', targetIso)
                .order('created_at', { ascending: false });

            if (error) {
                console.error("DB 로드 에러:", error);
                return;
            }

            // DAILY_HABIT 및 CHILD_REWARD 기록은 단어 암기 그래프에 포함되지 않도록 필터링
            const wordLogs = (data || []).filter(log => log.subject !== 'DAILY_HABIT' && log.subject !== 'CHILD_REWARD');
            renderHistory(wordLogs);
        }

        function renderHistory(logs) {
            const container = document.getElementById('history-container');
            if (!container) return;
            
            if (logs.length === 0) {
                container.innerHTML = `
                    <div class="history-title">📈 나의 일주일 공부 기록</div>
                    <div style="text-align:center; color:#636e72; font-size:14px; padding: 20px 0; font-family:'Jua', sans-serif;">아직 최근 기록이 없어요. 오늘도 파이팅! 💖</div>
                `;
                container.classList.remove('hidden');
                return;
            }

            // Aggregate by date
            const countsByDate = {};
            // Initialize last 7 days to maintain order
            for(let i=6; i>=0; i--) {
                const d = new Date();
                d.setDate(d.getDate() - i);
                const dateStr = `${d.getMonth()+1}/${d.getDate()}`;
                countsByDate[dateStr] = { total: 0 };
            }

            logs.forEach(log => {
                const d = new Date(log.created_at);
                const dateStr = `${d.getMonth()+1}/${d.getDate()}`;
                if (countsByDate[dateStr]) {
                    countsByDate[dateStr].total++;
                }
            });

            let html = `<div class="history-title">📈 나의 일주일 공부 기록</div>`;
            html += `<div style="display:flex; flex-direction:column; gap:4px; margin-top: 15px;">`;

            // Max value for bar chart scaling (minimum 10)
            const maxTotal = Math.max(10, ...Object.values(countsByDate).map(c => c.total));

            Object.keys(countsByDate).reverse().forEach((dateStr, index) => {
                const count = countsByDate[dateStr];
                const barWidth = Math.min((count.total / maxTotal) * 100, 100);
                const isToday = index === 0;
                
                html += `
                    <div class="history-chart-row">
                        <div class="history-chart-date" style="${isToday ? 'color:#ff758c;' : ''}">${dateStr}</div>
                        <div class="history-chart-bar-bg">
                            <div class="history-chart-bar-fill" style="width: ${barWidth}%; ${isToday ? 'background: linear-gradient(90deg, #84fab0 0%, #8fd3f4 100%);' : ''}"></div>
                        </div>
                        <div class="history-chart-count" style="${isToday ? 'color:#ff758c;' : ''}">${count.total}개</div>
                    </div>
                `;
            });
            html += `</div>`;
            
            container.innerHTML = html;
            container.classList.remove('hidden');
        }

        // ===================================================
        // Daily Habit State & Logic (지각 / 저녁 공부 관리)
        // ===================================================
        let habitRecordsMap = {};
        let selectedHabitDate = getLocalDateStr(new Date());
        let habitCalYear = new Date().getFullYear();
        let habitCalMonth = new Date().getMonth(); // 0-indexed
        let isHabitSaving = false;
        let isDadPreviewMode = false;
        let habitWeekOffset = 0; // 0 = 이번 주, -1 = 지난주, +1 = 다음주
        let isHabitMonthExpanded = false; // 월간 달력 전체보기 접기/펼치기 여부
        let familySchedules = []; // 아빠가 등록한 주요 일정 (중간고사, 제사, 기념일 등)

        let draftAttendance = null; // 'ON_TIME' | 'LATE' | 'EARLY_LEAVE' | 'ABSENT' | 'HOLIDAY' | null
        let draftAttendanceReason = null; // 'SICK' | 'EXPERIENCE' | 'FAMILY' | 'CUSTOM' | null
        let draftAttendanceReasonText = ''; // 결석/조퇴 구체적인 사유
        let draftEveningStudy = null; // true | false | null
        let draftStudyAttitude = null; // 'EXCELLENT' | 'GOOD' | 'NEEDS_FOCUS' | null
        let draftFocusOnTime = false; // [⏰ 정시 시작 / 시간 엄수]
        let draftFocusDeep = false; // [🌟 집중 몰입]
        let draftAbsenceReason = null; // 'REST_SICK' | 'REST_EXAM' | 'REST_TRAVEL' | 'REST_FATIGUE' | 'REST_CUSTOM' | null
        let draftReasonText = ''; // 사유 상세 텍스트
        let draftAssignments = []; // [{ id, text, dueDate, done }]
        let draftPromises = []; // [{ id, text, done }]
        let draftMemo = '';

        // ===================================================
        // 보상 & 퀘스트 시스템 State (CHILD_REWARD)
        // ===================================================
        let rewardCoupons = []; // [{ id, dbId, title, type, rewardDesc, date, status, claimedAt, usedAt }]
        let questConfig = {
            focusRewardTitle: '🏪 편의점 3,000원 상품권',
            focusRewardDesc: '정시 시작 & 몰입 퀘스트 5회 달성 축하 선물! 💖 (또는 아람이가 원하는 3,000원 간식 선물!) 🍰',
            goldRewardTitle: '🏖️ 1일 학습 자유 휴식권 (골드 티켓)',
            goldRewardDesc: '2주 퍼펙트 출결(14일 무결석·무지각·무조퇴) 대기록 달성 보상! 👑',
            quizRewardTitle: '🏪 편의점 2,000원 상품권 (또는 현금 2,000원)',
            quizRewardDesc: '상식 퀴즈 20문제 정답(2,000원 적립) 달성 축하 보상! 🪙'
        };
        let currentMainTab = 'study'; // 'study' | 'life'

        // ===================================================
        // 상식 퀴즈 100원 저금통 시스템 State
        // ===================================================
        let quizBankState = {
            totalAnswered: 0,
            currentPoints: 0, // 0 ~ 2000원 (20개 달성 시 리셋 및 쿠폰 발급)
            todayAnswered: 0, // 오늘 푼 개수 (최대 5개 = 500원)
            todayDate: ''
        };
        let currentQuizIndex = 0;
        let selectedQuizOption = null;
        let isQuizAnswerSubmitted = false;

        // 중학생 눈높이 맞춤 필수 상식 퀴즈 풀 (어휘·국어, 사회·역사, 과학·환경, 시사·잡학)
        const COMMON_QUIZ_POOL = [
            // ==================== [수학 핵심 개념어] ====================
            {
                category: "📐 수학 개념",
                question: "다항식에서 문자와 차수가 완전히 같아서 서로 덧셈·뺄셈을 할 수 있는 항을 무엇이라고 할까요?",
                options: ["상수항", "동류항", "계수", "미지수"],
                answer: 1,
                explanation: "동류항(同類項)은 '같은 종류의 항'이라는 뜻이에요! 예를 들어 3x와 5x는 문자와 차수가 같아 8x로 묶어서 계산할 수 있어요."
            },
            {
                category: "📐 수학 개념",
                question: "식 3x²에서 문자 x²의 바로 앞에 곱해져 있는 숫자 '3'을 무엇이라고 부를까요?",
                options: ["지수", "계수", "상수", "분모"],
                answer: 1,
                explanation: "계수(係數)는 '문자에 맺어져 곱해진 수'라는 뜻이에요! 3x에서 x의 계수는 3, -5y에서 y의 계수는 -5입니다."
            },
            {
                category: "📐 수학 개념",
                question: "다항식 2x + 7에서 문자(x) 없이 오직 숫자로만 이루어진 항(7)을 무엇이라고 할까요?",
                options: ["상수항", "단항식", "동류항", "차수"],
                answer: 0,
                explanation: "상수항(常數項)은 '항상 변하지 않는 일정한 수'라는 뜻으로, 문자가 곱해지지 않은 순수한 숫자 항을 말해요."
            },
            {
                category: "📐 수학 개념",
                question: "수직선 위에서 어떤 수와 기준점인 '0' 사이의 실제 거리를 나타내며 항상 0 이상인 값을 무엇이라고 할까요?",
                options: ["유리수", "절댓값", "역수", "제곱근"],
                answer: 1,
                explanation: "절댓값은 방향(+ 또는 -)을 떼고 0과의 순수한 거리를 뜻해요! 그래서 -5의 절댓값도 5, +5의 절댓값도 5가 됩니다."
            },
            {
                category: "📐 수학 개념",
                question: "두 수를 곱했을 때 결과가 '1'이 되게 만드는 상대방 수를 무엇이라고 할까요? (예: 2/3의 상대는 3/2)",
                options: ["반수", "약수", "역수", "배수"],
                answer: 2,
                explanation: "역수(逆數)는 분자와 분모를 거꾸로 뒤집은 수예요! 분수의 나눗셈을 할 때는 곱하기 역수로 바꾸어 계산하죠."
            },
            {
                category: "📐 수학 개념",
                question: "1보다 큰 자연수 중에서 1과 자기 자신만을 약수로 가지는 고유한 수(예: 2, 3, 5, 7, 11...)를 무엇이라고 할까요?",
                options: ["합성수", "소수(Prime Number)", "유리수", "음의 정수"],
                answer: 1,
                explanation: "소수(素數)는 '바탕이 되는 수'라는 뜻으로 더 이상 다른 수로 쪼갤 수 없는 수예요. 2는 유일한 짝수 소수랍니다!"
            },

            // ==================== [과학 핵심 개념 & 생활 과학] ====================
            {
                category: "🔬 과학 개념",
                question: "추운 겨울철 따뜻한 방 안 창문에 수증기가 닿아 물방울로 맺히는 것처럼, 기체가 액체로 변하는 현상은?",
                options: ["응고", "기화", "액화", "승화"],
                answer: 2,
                explanation: "액화(液化)는 '액체가 된다'는 뜻이에요! 반대로 물이 끓어 수증기가 되는 것은 '기화', 물이 얼어 얼음이 되는 것은 '응고'라고 해요."
            },
            {
                category: "🔬 과학 개념",
                question: "철이 공기 중의 산소와 결합하여 녹이 슬거나, 촛불이 타는 것처럼 어떤 물질이 '산소와 결합하는 반응'을 무엇이라고 할까요?",
                options: ["산화", "환원", "중화", "용해"],
                answer: 0,
                explanation: "산화(酸化)는 '산소와 결합하다'는 뜻이에요! 반대로 산소를 잃어버리는 반응은 원래대로 돌아간다는 뜻의 '환원'이라고 부릅니다."
            },
            {
                category: "🔬 과학 개념",
                question: "물질의 가볍고 무거운 정도를 나타내며, '단위 부피당 질량(질량 ÷ 부피)'으로 정의되는 고유한 성질은?",
                options: ["무게", "밀도", "농도", "점도"],
                answer: 1,
                explanation: "밀도(密度)는 물질이 얼마나 '빽빽하게 뭉쳐있는가'를 나타내요! 기름이 물 위에 뜨는 이유는 기름의 밀도가 물보다 작기 때문이에요."
            },
            {
                category: "🔬 과학 개념",
                question: "식물의 엽록체에서 햇빛 에너지, 물, 이산화탄소를 이용해 스스로 포도당(양분)과 산소를 만들어내는 과정은?",
                options: ["증산작용", "광합성", "호흡작용", "세포분열"],
                answer: 1,
                explanation: "광합성(光合成)은 '빛(光)으로 물질을 합성한다'는 뜻이에요. 지구상의 생명체가 숨 쉬는 산소의 대부분을 만들어줘요."
            },
            {
                category: "🔬 과학 개념",
                question: "벽을 손으로 세게 밀면 내 몸도 뒤로 밀려나는 것처럼, 한 물체에 힘을 가하면 크기는 같고 방향이 반대인 힘이 동시에 작용하는 법칙은?",
                options: ["관성의 법칙", "작용·반작용의 법칙", "가속도의 법칙", "만유인력의 법칙"],
                answer: 1,
                explanation: "뉴턴의 운동 제3법칙인 '작용·반작용'이에요! 로켓이 가스를 뒤로 뿜어내면서 앞으로 날아가는 것도 같은 원리랍니다."
            },
            {
                category: "🔬 과학 개념",
                question: "드라이아이스가 액체 단계를 거치지 않고 곧바로 기체로 날아가거나, 반대로 서리가 생기는 것처럼 고체와 기체 사이의 직접적인 상태 변화는?",
                options: ["승화", "융해", "기화", "액화"],
                answer: 0,
                explanation: "승화(昇華)는 액체를 건너뛰고 '고체 ➔ 기체' 또는 '기체 ➔ 고체'로 단번에 변하는 신기한 현상이에요."
            },
            {
                category: "🔬 생활·물리 상식",
                question: "비행기 날개 위쪽과 아래쪽의 공기 흐름 속도 차이에 의해 비행기를 위로 번쩍 뜨게 하는 힘은?",
                options: ["중력", "마찰력", "양력", "부력"],
                answer: 2,
                explanation: "비행기는 날개 위쪽이 볼록하여 공기가 빠르게 흐르고, 압력 차이로 위로 뜨는 '양력(Lift)'이 발생해 하늘을 날 수 있어요."
            },

            // ==================== [사회·경제·정치 상식] ====================
            {
                category: "🌍 사회·경제",
                question: "물가가 지속적으로 오르고, 반대로 돈(화폐)의 가치는 떨어지는 경제 현상을 무엇이라고 부를까요?",
                options: ["디플레이션", "인플레이션", "스태그플레이션", "환율 상승"],
                answer: 1,
                explanation: "인플레이션(Inflation)은 풍선이 부풀듯 물가가 오르는 현상이에요. 1,000원으로 사던 과자가 2,000원이 되면 돈의 힘이 약해진 것이죠."
            },
            {
                category: "🌍 사회·경제",
                question: "여러 가지 선택지 중에서 하나를 선택했을 때, 포기해야 하는 다른 선택지들 중 '가장 가치가 큰 것'을 무엇이라고 할까요?",
                options: ["매몰비용", "기회비용", "한계비용", "고정비용"],
                answer: 1,
                explanation: "기회비용(Opportunity Cost)은 '하나를 얻기 위해 포기한 최고의 기회'를 뜻해요! 현명한 선택은 기회비용보다 얻는 만족이 더 커야 해요."
            },
            {
                category: "🌍 사회·정치",
                question: "국가 권력이 특정인에게 집중되어 남용되는 것을 막기 위해 권력을 입법부, 사법부, 행정부로 나누는 민주주의 제도는?",
                options: ["삼권분립", "직접민주주의", "지방자치제", "의원내각제"],
                answer: 0,
                explanation: "삼권분립은 국민의 자유와 권리를 지키기 위해 법을 만드는 국회(입법), 법을 집행하는 정부(행정), 법을 판단하는 법원(사법)으로 권력을 나누는 원리예요."
            },
            {
                category: "🌍 사회·정치",
                question: "국가의 주권이 국민에게 있고, 모든 권력은 국민으로부터 나온다는 대한민국 헌법 제1조의 기본 원리는?",
                options: ["국민주권주의", "입헌군주제", "자유방임주의", "관료제"],
                answer: 0,
                explanation: "국민주권(國民主權)은 국가의 진짜 주인은 왕이나 대통령이 아니라 바로 모든 국민이라는 민주주의의 대원칙이에요."
            },
            {
                category: "🌍 사회·경제",
                question: "물건을 사려는 사람들의 욕구를 '수요'라고 할 때, 시장에서 물건을 만들어 팔려는 욕구를 무엇이라고 할까요?",
                options: ["공급", "소비", "유통", "독점"],
                answer: 0,
                explanation: "시장의 가격은 사려는 사람(수요)과 팔려는 사람(공급)이 만나는 균형점에서 결정됩니다."
            },
            {
                category: "🌍 사회·법률",
                question: "국회에서 만든 법률이 국민의 기본권을 침해하거나 헌법에 어긋나는지 전문적으로 심판하는 국가 기관은?",
                options: ["대법원", "헌법재판소", "감사원", "국가인권위원회"],
                answer: 1,
                explanation: "헌법재판소는 법이 헌법에 위배되는지 심판(위헌법률심판)하고, 대통령 탄핵 심판 등을 통해 국민의 헌법적 권리를 지켜줘요."
            },

            // ==================== [국어·문해력 & 필수 상식] ====================
            {
                category: "📚 어휘·문해력",
                question: "'어부지리(漁父之利)'의 정확한 뜻으로 알맞은 것은 무엇일까요?",
                options: ["어부가 물고기를 많이 잡아 부자가 됨", "두 사람이 다투는 틈을 타 제3자가 이득을 얻음", "어려운 상황에서도 끝까지 포기하지 않음", "스스로 힘으로 바다를 건너 큰 성공을 거둠"],
                answer: 1,
                explanation: "어부지리는 조개와 도요새가 서로 다투느라 도망치지 못하는 사이, 지나가던 어부가 둘 다 쉽게 잡았다는 고사성어에서 유래했어요!"
            },
            {
                category: "📚 국어 개념",
                question: "어떤 사실이나 현상이 원인과 결과의 관계로 얽혀 있는 것을 가리키는 말은?",
                options: ["상관관계", "인과관계", "대등관계", "모순관계"],
                answer: 1,
                explanation: "인과(因果)는 원인 인(因)과 결과 과(果)가 합쳐진 말이에요! '비가 와서(원인) 땅이 젖었다(결과)'가 인과관계의 대표적인 예예요."
            },
            {
                category: "📚 국어 개념",
                question: "'내 마음은 호수요'처럼 '~처럼', '~같이' 같은 말을 쓰지 않고 A는 곧 B라고 빗대어 표현하는 수사법은?",
                options: ["직유법", "은유법", "의인법", "도치법"],
                answer: 1,
                explanation: "은유법(隱喩法)은 숨겨서(隱) 빗대는 표현이에요! 반대로 '~처럼, ~같이'를 대놓고 드러내면 '직유법'이라고 합니다."
            },
            {
                category: "📚 국어 개념",
                question: "개인적인 감정이나 생각에 치우치지 않고, 제3자의 입장에서 사실 그대로를 바라보는 태도를 무엇이라고 할까요?",
                options: ["주관적", "객관적", "상대적", "비판적"],
                answer: 1,
                explanation: "손님(客)의 눈으로 공정하게 사실을 본다는 뜻의 '객관적(客觀的)'이에요. 반대로 내 개인적인 감정 중심이면 '주관적'이라고 해요."
            },
            {
                category: "📚 국어 개념",
                question: "'이것은 소리 없는 아우성'처럼 겉으로는 서로 말이 안 되고 모순되지만, 그 속에 깊은 진실을 담고 있는 표현 방법은?",
                options: ["반어법", "역설법", "풍자법", "과장법"],
                answer: 1,
                explanation: "역설법(Paradox)은 이치에 맞지 않아 보이는 말 속에 참뜻을 숨겨놓은 표현이에요! (소리가 없는데 아우성일 수는 없지만 절규하는 심정을 강조)"
            },
            {
                category: "📚 맞춤법 상식",
                question: "다음 중 올바른 맞춤법으로 쓰인 문장은 무엇일까요?",
                options: ["어의가 없어서 말이 안 나온다.", "어이가 없어서 말이 안 나온다.", "어의가 업서서 말이 안 나온다.", "어의없네 정말로."],
                answer: 1,
                explanation: "뜻밖의 일에 기가 막히다는 뜻의 표준어는 '어이없다'입니다! ('어의'는 조선시대 임금님을 진료하던 의사를 뜻해요.)"
            },
            {
                category: "📚 어휘·한자",
                question: "겉으로는 화려하고 좋아 보이지만 실속은 전혀 없음을 뜻하는 사자성어는 무엇일까요?",
                options: ["유비무환", "외유내강", "유명무실", "동병상련"],
                answer: 2,
                explanation: "유명무실(有名無實)은 '이름만 있고(有名) 실제 알맹이는 없다(無實)'는 뜻으로, 겉포장만 그럴듯할 때 쓰는 말이에요."
            },

            // ==================== [역사·시사·문화 상식] ====================
            {
                category: "🏛️ 역사·문화 상식",
                question: "조선 세종대왕 때 장영실 등이 만든 우리나라 최초의 자동 물시계 이름은?",
                options: ["자격루", "앙부일구", "혼천의", "측우기"],
                answer: 0,
                explanation: "자격루(自擊漏)는 물이 차오르면 쇠구슬이 굴러 종과 북을 저절로 쳐서 시간을 알려주던 세계적인 발명품이에요!"
            },
            {
                category: "🏛️ 역사·지리 상식",
                question: "신라 지증왕 때 이사부 장군이 복속시켰으며, 역사적·지리적·국제법적으로 명백한 대한민국의 고유 영토인 동해의 섬은?",
                options: ["거문도", "독도", "완도", "마라도"],
                answer: 1,
                explanation: "'삼국사기'에 512년 이사부가 우산국(울릉도·독도)을 복속시켰다는 기록이 있으며, 독도는 대한민국의 소중한 영토입니다."
            },
            {
                category: "💡 시사·디지털 상식",
                question: "인터넷이나 SNS에서 거짓 정보나 조작된 사실을 진짜 뉴스처럼 퍼뜨리는 가짜 정보를 뜻하는 용어는?",
                options: ["딥페이크", "페이크 뉴스(가짜 뉴스)", "알고리즘", "빅데이터"],
                answer: 1,
                explanation: "페이크 뉴스는 사회적 혼란을 일으키므로, 정보를 볼 때는 항상 출처가 확실한지 비판적으로 확인하는 태도가 중요해요!"
            }
        ];

        function getStudyStatusInfo(val) {
            if (val === true) {
                return {
                    badge: '📖',
                    title: '저녁 공부 완료',
                    childClass: 'study-done',
                    icon: '📖',
                    childTitle: '저녁 공부',
                    childText: '저녁 공부 완료! 오늘도 한 걸음 더 성장했어요! 👑',
                    modalText: '📖 저녁 공부 완료! 👑'
                };
            }
            if (val === 'REST_EXAM') {
                return {
                    badge: '📝',
                    title: '공부 쉼 (수행평가)',
                    childClass: 'study-exam',
                    icon: '📝',
                    childTitle: '공부 쉼 (수행평가)',
                    childText: '수행평가 준비로 저녁 공부를 쉬어갑니다 📝 화이팅!',
                    modalText: '📝 공부 쉼 (수행평가 집중)'
                };
            }
            if (val === 'REST_SICK') {
                return {
                    badge: '🤒',
                    title: '공부 쉼 (질병/아픔)',
                    childClass: 'study-sick',
                    icon: '🤒',
                    childTitle: '공부 쉼 (질병/아픔)',
                    childText: '몸이 아파서 푹 쉬고 회복하는 중이에요 💊 얼른 나아요!',
                    modalText: '🤒 공부 쉼 (질병 / 건강 회복)'
                };
            }
            if (val === 'REST_TRAVEL') {
                return {
                    badge: '✈️',
                    title: '공부 쉼 (여행/외출)',
                    childClass: 'study-travel',
                    icon: '✈️',
                    childTitle: '공부 쉼 (여행/외출)',
                    childText: '즐거운 여행·일정 중이에요! 좋은 추억 만들어요 🎈',
                    modalText: '✈️ 공부 쉼 (여행 / 가족 일정)'
                };
            }
            if (val === false || val === 'REST_NORMAL') {
                return {
                    badge: '💤',
                    title: '공부 쉼 (일반 휴식)',
                    childClass: 'study-rest',
                    icon: '💤',
                    childTitle: '저녁 공부',
                    childText: '오늘은 편안하게 쉬어가는 날이에요 ☕',
                    modalText: '💤 공부 쉼 / 일반 휴식'
                };
            }
            return null;
        }

        function getSchedulesForDate(dateStr) {
            if (!familySchedules || !familySchedules.length) return [];
            return familySchedules.filter(s => {
                const start = s.startDate;
                const end = s.endDate || s.startDate;
                return start <= dateStr && dateStr <= end;
            });
        }

        function formatScheduleRange(startDate, endDate) {
            if (!startDate) return '';
            if (!endDate || startDate === endDate) {
                const parts = startDate.split('-').map(Number);
                const d = new Date(parts[0], parts[1] - 1, parts[2]);
                const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
                return `${parts[1]}월 ${parts[2]}일(${dayNames[d.getDay()]})`;
            }
            const p1 = startDate.split('-').map(Number);
            const d1 = new Date(p1[0], p1[1] - 1, p1[2]);
            const p2 = endDate.split('-').map(Number);
            const d2 = new Date(p2[0], p2[1] - 1, p2[2]);
            const dayNames = ['일', '월', '화', '수', '목', '금', '토'];
            return `${p1[1]}월 ${p1[2]}일(${dayNames[d1.getDay()]}) ~ ${p2[1]}월 ${p2[2]}일(${dayNames[d2.getDay()]})`;
        }

        function getScheduleDDayInfo(startDate, endDate) {
            const todayStr = getLocalDateStr(new Date());

            if (todayStr >= startDate && todayStr <= (endDate || startDate)) {
                return {
                    label: (startDate === endDate) ? '오늘 D-Day! 🌟' : '진행 중! 🔥',
                    className: 'active',
                    isOngoing: true,
                    isUpcoming: false,
                    isPassed: false,
                    diff: 0
                };
            }

            const todayParts = todayStr.split('-').map(Number);
            const todayDate = new Date(todayParts[0], todayParts[1] - 1, todayParts[2]);

            const startParts = startDate.split('-').map(Number);
            const startDateObj = new Date(startParts[0], startParts[1] - 1, startParts[2]);

            const diffDays = Math.round((startDateObj - todayDate) / (1000 * 60 * 60 * 24));

            if (diffDays > 0) {
                return {
                    label: `D-${diffDays}`,
                    className: (diffDays <= 7) ? 'urgent' : 'normal',
                    isOngoing: false,
                    isUpcoming: true,
                    isPassed: false,
                    diff: diffDays
                };
            } else {
                const endParts = (endDate || startDate).split('-').map(Number);
                const endDateObj = new Date(endParts[0], endParts[1] - 1, endParts[2]);
                const pastDays = Math.round((todayDate - endDateObj) / (1000 * 60 * 60 * 24));
                return {
                    label: '종료',
                    className: 'passed',
                    isOngoing: false,
                    isUpcoming: false,
                    isPassed: true,
                    diff: -pastDays
                };
            }
        }

        function generateScheduleCardHtml(isDad) {
            const activeList = [];
            const upcomingList = [];
            const passedList = [];

            familySchedules.forEach(ev => {
                const info = getScheduleDDayInfo(ev.startDate, ev.endDate);
                if (info.isOngoing) activeList.push({ ...ev, info });
                else if (info.isUpcoming) upcomingList.push({ ...ev, info });
                else passedList.push({ ...ev, info });
            });

            // 아람이 화면 및 메인 카드에는 [진행 중] 또는 [예정된 D-Day] 일정만 표시하고, 이미 지난(종료된) 일정은 숨김 처리
            // (종료된 지난 일정은 아빠 관리 모달에서 확인하거나 내년 날짜로 갱신 가능)
            let displayList = [...activeList, ...upcomingList];
            if (isDad && displayList.length === 0 && passedList.length > 0) {
                // 아빠 관리 모드에서는 등록된 일정이 모두 종료되었을 때만 최근 종료 일정 1건을 안내용으로 표시
                displayList.push(passedList[passedList.length - 1]);
            }

            let itemsHtml = '';
            if (displayList.length === 0) {
                itemsHtml = `
                    <div style="text-align:center; padding:12px; color:#94a3b8; font-size:13px; font-family:'Jua', sans-serif;">
                        ${isDad ? '등록된 시험이나 가족 일정이 없습니다. 우측 버튼을 눌러 일정을 등록해보세요! 😊' : '등록된 주요 일정이 없습니다 💖'}
                    </div>
                `;
            } else {
                itemsHtml = displayList.slice(0, 4).map(ev => {
                    const rangeStr = formatScheduleRange(ev.startDate, ev.endDate);
                    const deleteBtn = isDad 
                        ? `<button type="button" onclick="deleteSchedule(${ev.id}, '${escapeHtml(ev.title)}')" style="background:none; border:none; color:#cbd5e1; cursor:pointer; font-size:14px; padding:2px 4px;" title="일정 삭제" onmouseover="this.style.color='#ef4444'" onmouseout="this.style.color='#cbd5e1'">🗑️</button>` 
                        : '';
                    const activeClass = ev.info.isOngoing ? 'active-now' : '';
                    return `
                        <div class="schedule-item ${activeClass}">
                            <div class="schedule-item-left">
                                <div class="schedule-icon-badge">${ev.icon}</div>
                                <div class="schedule-info">
                                    <div class="schedule-name">${escapeHtml(ev.title)}</div>
                                    <div class="schedule-dates">📅 ${rangeStr}</div>
                                    ${ev.memo ? `<div class="schedule-memo-text">💬 ${escapeHtml(ev.memo)}</div>` : ''}
                                </div>
                            </div>
                            <div class="schedule-item-right">
                                <span class="schedule-dday-badge ${ev.info.className}">${ev.info.label}</span>
                                ${deleteBtn}
                            </div>
                        </div>
                    `;
                }).join('');
            }

            const manageBtn = isDad
                ? `<button type="button" class="schedule-add-btn" onclick="openScheduleModal()">➕ 일정 등록 / 관리</button>`
                : (familySchedules.length > 0 ? `<button type="button" class="habit-cal-btn" onclick="openScheduleModal()" style="font-size:11px; padding:3px 8px;">전체 (${familySchedules.length})</button>` : '');

            return `
                <div class="schedule-section-card">
                    <div class="schedule-header">
                        <div class="schedule-title">
                            <span>🗓️ 우리 집 주요 일정 & D-Day</span>
                        </div>
                        ${manageBtn}
                    </div>
                    <div class="schedule-list">
                        ${itemsHtml}
                    </div>
                </div>
            `;
        }

        function openScheduleModal() {
            const overlay = document.getElementById('schedule-modal-overlay');
            if (!overlay) return;
            overlay.classList.remove('hidden');

            const startInput = document.getElementById('sched-input-start');
            const endInput = document.getElementById('sched-input-end');
            if (startInput && !startInput.value) {
                startInput.value = selectedHabitDate || getLocalDateStr(new Date());
            }
            if (endInput && !endInput.value) {
                endInput.value = startInput ? startInput.value : getLocalDateStr(new Date());
            }

            renderScheduleModalList();
        }

        function closeScheduleModal() {
            const overlay = document.getElementById('schedule-modal-overlay');
            if (overlay) overlay.classList.add('hidden');
        }

        function selectSchedCat(btn) {
            document.querySelectorAll('.sched-cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        function syncSchedEndDate(val) {
            const endInput = document.getElementById('sched-input-end');
            if (endInput && (!endInput.value || endInput.value < val)) {
                endInput.value = val;
            }
        }

        async function saveNewSchedule() {
            const titleInput = document.getElementById('sched-input-title');
            const startInput = document.getElementById('sched-input-start');
            const endInput = document.getElementById('sched-input-end');
            const memoInput = document.getElementById('sched-input-memo');
            const saveBtn = document.getElementById('sched-save-btn');

            const title = (titleInput?.value || '').trim();
            const startDate = startInput?.value;
            let endDate = endInput?.value || startDate;
            const memo = (memoInput?.value || '').trim();

            if (!title) {
                alert("일정 제목을 입력해주세요! (예: 2학기 중간고사, 할아버지 제사 등)");
                titleInput?.focus();
                return;
            }
            if (!startDate) {
                alert("시작 날짜를 선택해주세요!");
                startInput?.focus();
                return;
            }
            if (endDate < startDate) {
                endDate = startDate;
            }

            const selectedCatBtn = document.querySelector('.sched-cat-btn.active');
            const icon = selectedCatBtn ? selectedCatBtn.getAttribute('data-icon') : '📌';
            const category = selectedCatBtn ? selectedCatBtn.getAttribute('data-cat') : 'OTHER';

            const schedObj = {
                title,
                startDate,
                endDate,
                icon,
                category,
                memo,
                author: userNickname || '아빠',
                created_at: new Date().toISOString()
            };

            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.innerText = "저장 중... ⏳";
            }

            try {
                const schedKey = `SCHED_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`;
                const { error } = await supabaseClient
                    .from('study_words')
                    .insert([{
                        word: schedKey,
                        meaning: JSON.stringify(schedObj),
                        subject: 'FAMILY_SCHEDULE',
                        category: '아람',
                        example: userNickname || '아빠'
                    }]);

                if (error) throw error;

                confetti({
                    particleCount: 80,
                    spread: 60,
                    origin: { y: 0.5 }
                });

                alert(`💖 [${icon} ${title}] 일정이 등록되었습니다!`);
                
                await loadHabitRecords();
                
                if (titleInput) titleInput.value = '';
                if (memoInput) memoInput.value = '';
                
                renderScheduleModalList();
                
            } catch(err) {
                console.error("Save schedule error:", err);
                alert("일정 저장 중 오류가 발생했습니다: " + (err.message || err));
            } finally {
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.innerText = "💾 일정 추가하기 💖";
                }
            }
        }

        async function deleteSchedule(id, title) {
            if (!confirm(`[${title}] 일정을 삭제하시겠습니까?`)) return;

            try {
                const { error } = await supabaseClient
                    .from('study_words')
                    .delete()
                    .eq('id', id);

                if (error) throw error;

                alert(`[${title}] 일정이 삭제되었습니다.`);
                await loadHabitRecords();
                renderScheduleModalList();
            } catch(err) {
                console.error("Delete schedule error:", err);
                alert("삭제 중 오류가 발생했습니다: " + (err.message || err));
            }
        }

        function renderScheduleModalList() {
            const container = document.getElementById('sched-modal-list');
            if (!container) return;

            if (!familySchedules || familySchedules.length === 0) {
                container.innerHTML = `<div style="text-align:center; color:#94a3b8; font-size:12px; padding:16px;">등록된 일정이 없습니다.</div>`;
                return;
            }

            const isDad = (userNickname === '아빠');
            let html = '';
            familySchedules.forEach(ev => {
                const dday = getScheduleDDayInfo(ev.startDate, ev.endDate);
                const delBtn = isDad 
                    ? `<button type="button" onclick="deleteSchedule(${ev.id}, '${escapeHtml(ev.title)}')" style="background:#fee2e2; color:#ef4444; border:none; padding:4px 8px; border-radius:8px; font-size:11px; font-weight:bold; cursor:pointer;">🗑️ 삭제</button>` 
                    : '';
                html += `
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:8px 12px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-size:18px;">${ev.icon}</span>
                            <div>
                                <div style="font-size:13px; font-weight:bold; color:#1e293b;">${escapeHtml(ev.title)}</div>
                                <div style="font-size:11px; color:#64748b;">${formatScheduleRange(ev.startDate, ev.endDate)} <span style="font-weight:bold; color:#6366f1;">(${dday.label})</span></div>
                                ${ev.memo ? `<div style="font-size:11px; color:#8b5cf6;">💬 ${escapeHtml(ev.memo)}</div>` : ''}
                            </div>
                        </div>
                        ${delBtn}
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function getWeekDays(offset = 0) {
            const now = new Date();
            const day = now.getDay(); // 0 is Sun, 1 is Mon, ... 6 is Sat
            const diffToMonday = (day === 0 ? -6 : 1 - day);
            const monday = new Date(now.getFullYear(), now.getMonth(), now.getDate() + diffToMonday + (offset * 7));
            
            const week = [];
            for (let i = 0; i < 7; i++) {
                const d = new Date(monday.getFullYear(), monday.getMonth(), monday.getDate() + i);
                week.push(d);
            }
            return week;
        }

        function getWeekOffsetFromDate(targetDateStr) {
            if (!targetDateStr) return 0;
            const now = new Date();
            const day = now.getDay();
            const diffToMonday = (day === 0 ? -6 : 1 - day);
            const currMonday = new Date(now.getFullYear(), now.getMonth(), now.getDate() + diffToMonday);
            currMonday.setHours(0,0,0,0);

            const parts = targetDateStr.split('-').map(Number);
            const targetDate = new Date(parts[0], parts[1] - 1, parts[2]);
            const targetDay = targetDate.getDay();
            const targetDiffToMonday = (targetDay === 0 ? -6 : 1 - targetDay);
            const targetMonday = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate() + targetDiffToMonday);
            targetMonday.setHours(0,0,0,0);

            const diffDays = Math.round((targetMonday - currMonday) / (1000 * 60 * 60 * 24));
            return Math.round(diffDays / 7);
        }

        function getWeekRangeTitle(monday, sunday) {
            const y1 = monday.getFullYear();
            const m1 = monday.getMonth() + 1;
            const d1 = monday.getDate();
            const y2 = sunday.getFullYear();
            const m2 = sunday.getMonth() + 1;
            const d2 = sunday.getDate();

            if (y1 === y2) {
                if (m1 === m2) {
                    return `${y1}년 ${m1}월 ${d1}일 ~ ${d2}일`;
                }
                return `${y1}년 ${m1}월 ${d1}일 ~ ${m2}월 ${d2}일`;
            }
            return `${y1}년 ${m1}월 ${d1}일 ~ ${y2}년 ${m2}월 ${d2}일`;
        }

        function getWeeklyHabitStats(weekDays) {
            let onTimeCount = 0;
            let lateCount = 0;
            let holidayCount = 0;
            let studyCount = 0;

            weekDays.forEach(d => {
                const dStr = getLocalDateStr(d);
                const rec = habitRecordsMap[dStr];
                if (rec) {
                    if (rec.attendance === 'ON_TIME') onTimeCount++;
                    else if (rec.attendance === 'LATE') lateCount++;
                    else if (rec.attendance === 'HOLIDAY') holidayCount++;

                    if (rec.evening_study === true) studyCount++;
                }
            });

            return { onTimeCount, lateCount, holidayCount, studyCount };
        }

        function changeHabitWeek(delta) {
            habitWeekOffset += delta;
            renderHabitSection();
        }

        function resetHabitWeek() {
            habitWeekOffset = 0;
            renderHabitSection();
        }

        function toggleHabitMonthCalendar() {
            isHabitMonthExpanded = !isHabitMonthExpanded;
            renderHabitSection();
        }

        function generateHabitWeekStripHtml(isDad) {
            const weekDays = getWeekDays(habitWeekOffset);
            const monday = weekDays[0];
            const sunday = weekDays[6];
            const todayStr = getLocalDateStr(new Date());

            const weekStats = getWeeklyHabitStats(weekDays);
            const weekTitle = getWeekRangeTitle(monday, sunday);
            const dayNames = ['월', '화', '수', '목', '금', '토', '일'];

            let daysHtml = '';
            weekDays.forEach((d, idx) => {
                const dateStr = getLocalDateStr(d);
                const isToday = (dateStr === todayStr);
                const isSelected = (isDad && dateStr === selectedHabitDate);
                const rec = habitRecordsMap[dateStr];

                let badgesHtml = '';
                if (rec) {
                    if (rec.attendance === 'ON_TIME') badgesHtml += '<span title="정상 등교">☀️</span>';
                    else if (rec.attendance === 'LATE') badgesHtml += '<span title="지각">⏰</span>';
                    else if (rec.attendance === 'HOLIDAY') badgesHtml += '<span title="휴일/주말">🏖️</span>';

                    const studyInfo = getStudyStatusInfo(rec.evening_study);
                    if (studyInfo) {
                        badgesHtml += `<span title="${studyInfo.title}">${studyInfo.badge}</span>`;
                    }

                    if (rec.memo) badgesHtml += '<span title="아빠 응원">💌</span>';
                }

                const dayEvents = getSchedulesForDate(dateStr);
                let eventPillsHtml = '';
                if (dayEvents && dayEvents.length > 0) {
                    dayEvents.forEach(ev => {
                        let catClass = 'other';
                        if (ev.category === 'EXAM') catClass = 'exam';
                        else if (ev.category === 'FAMILY') catClass = 'family';
                        else if (ev.category === 'BIRTHDAY') catClass = 'birthday';
                        else if (ev.category === 'VACATION') catClass = 'vacation';
                        eventPillsHtml += `<div class="habit-week-event-pill ${catClass}" title="${escapeHtml(ev.title)}">${ev.icon} ${escapeHtml(ev.title)}</div>`;
                    });
                }

                const clickHandler = isDad 
                    ? `changeHabitDate('${dateStr}')` 
                    : `showChildDayDetail('${dateStr}')`;

                const isSat = (idx === 5);
                const isSun = (idx === 6);
                const weekdayClass = isSun ? 'sun' : (isSat ? 'sat' : '');

                daysHtml += `
                    <div class="habit-week-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}" onclick="${clickHandler}" title="${dateStr}">
                        ${isToday ? '<span class="habit-today-tag">오늘</span>' : ''}
                        <div class="habit-week-weekday ${weekdayClass}">${dayNames[idx]}</div>
                        <div class="habit-week-date-num">${d.getDate()}</div>
                        <div class="habit-week-badges">${badgesHtml || '<span class="habit-badge-empty">·</span>'}</div>
                        ${eventPillsHtml}
                    </div>
                `;
            });

            return `
                <div class="habit-week-wrap">
                    <div class="habit-week-nav">
                        <button type="button" class="habit-cal-btn" onclick="changeHabitWeek(-1)">◀ 지난주</button>
                        <div class="habit-date-center">
                            <div class="habit-week-title">📅 ${weekTitle}</div>
                            ${habitWeekOffset !== 0 
                                ? `<button type="button" onclick="resetHabitWeek()" class="habit-week-reset-btn">이번 주로 돌아가기</button>` 
                                : `<span class="habit-week-current-pill">이번 주</span>`}
                        </div>
                        <button type="button" class="habit-cal-btn" onclick="changeHabitWeek(1)">다음주 ▶</button>
                    </div>

                    <!-- 주간 성취 요약 바 -->
                    <div class="habit-week-stats-bar">
                        <span>✨ 이번 주 성취:</span>
                        <strong>📖 저녁 공부 <span style="color:#6366f1;">${weekStats.studyCount}일</span></strong>
                        <span style="color:#cbd5e1;">·</span>
                        <strong>☀️ 정상 등교 <span style="color:#059669;">${weekStats.onTimeCount}일</span></strong>
                        ${weekStats.lateCount > 0 ? `<span style="color:#cbd5e1;">·</span> <strong>⏰ 지각 <span style="color:#ef4444;">${weekStats.lateCount}일</span></strong>` : ''}
                    </div>

                    <!-- 주간 7일 스트립 -->
                    <div class="habit-week-grid">
                        ${daysHtml}
                    </div>
                    <div style="font-size:11px; color:#888; text-align:center; margin-top:10px;">
                        ☀️ 정상등교 · ⏰ 지각 · 🏖️ 주말/휴일 · 📖 저녁공부 · 📝 수행평가 · 🤒 질병 · ✈️ 여행 · 💤 휴식 · 💌 응원
                    </div>
                </div>
            `;
        }

        function getLocalDateStr(d = new Date()) {
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        function formatFriendlyDate(dateStr) {
            if (!dateStr) return '';
            const parts = dateStr.split('-').map(Number);
            const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
            const days = ['일', '월', '화', '수', '목', '금', '토'];
            const dayName = days[dateObj.getDay()];
            return `${parts[0]}년 ${parts[1]}월 ${parts[2]}일 (${dayName}요일)`;
        }

        function escapeHtml(str) {
            if (!str) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#039;');
        }

        async function loadHabitRecords() {
            const container = document.getElementById('habit-container');
            if (!container || !userNickname) return;
            container.classList.remove('hidden');

            try {
                const [habitRes, schedRes, rewardRes] = await Promise.all([
                    supabaseClient
                        .from('study_words')
                        .select('*')
                        .eq('subject', 'DAILY_HABIT')
                        .order('word', { ascending: false }),
                    supabaseClient
                        .from('study_words')
                        .select('*')
                        .eq('subject', 'FAMILY_SCHEDULE')
                        .order('created_at', { ascending: true }),
                    supabaseClient
                        .from('study_words')
                        .select('*')
                        .eq('subject', 'CHILD_REWARD')
                        .order('created_at', { ascending: false })
                ]);

                if (habitRes.error) {
                    console.error("Habit logs fetch error:", habitRes.error);
                } else if (habitRes.data) {
                    habitRecordsMap = {};
                    habitRes.data.forEach(item => {
                        try {
                            const detail = typeof item.meaning === 'string' ? JSON.parse(item.meaning) : (item.meaning || {});
                            habitRecordsMap[item.word] = {
                                ...detail,
                                id: item.id,
                                rawCreatedAt: item.created_at
                            };
                        } catch(e) {
                            console.error("Habit parse error:", e);
                        }
                    });
                }

                if (schedRes.error) {
                    console.error("Schedule fetch error:", schedRes.error);
                } else if (schedRes.data) {
                    familySchedules = [];
                    schedRes.data.forEach(item => {
                        try {
                            const detail = typeof item.meaning === 'string' ? JSON.parse(item.meaning) : (item.meaning || {});
                            familySchedules.push({
                                id: item.id,
                                word: item.word,
                                title: detail.title || item.word,
                                startDate: detail.startDate,
                                endDate: detail.endDate || detail.startDate,
                                icon: detail.icon || '📌',
                                category: detail.category || 'OTHER',
                                memo: detail.memo || '',
                                author: detail.author || item.example || '아빠'
                            });
                        } catch(e) {
                            console.error("Schedule parse error:", e);
                        }
                    });
                    // Sort by startDate
                    familySchedules.sort((a, b) => (a.startDate || '').localeCompare(b.startDate || ''));
                }

                if (rewardRes.error) {
                    console.error("Reward fetch error:", rewardRes.error);
                } else if (rewardRes.data) {
                    rewardCoupons = [];
                    rewardRes.data.forEach(item => {
                        try {
                            const detail = typeof item.meaning === 'string' ? JSON.parse(item.meaning) : (item.meaning || {});
                            if (item.word === 'QUEST_REWARD_SETTINGS') {
                                questConfig = {
                                    focusRewardTitle: detail.focusRewardTitle || questConfig.focusRewardTitle,
                                    focusRewardDesc: detail.focusRewardDesc || questConfig.focusRewardDesc,
                                    goldRewardTitle: detail.goldRewardTitle || questConfig.goldRewardTitle,
                                    goldRewardDesc: detail.goldRewardDesc || questConfig.goldRewardDesc
                                };
                            } else {
                                rewardCoupons.push({
                                    dbId: item.id,
                                    id: item.word,
                                    ...detail
                                });
                            }
                        } catch(e) {
                            console.error("Reward parse error:", e);
                        }
                    });
                }
            } catch(err) {
                console.error("loadHabitRecords error:", err);
            }

            syncDraftWithSelectedDate();
            if (userNickname !== '희진' && userNickname !== '희진부모') {
                await checkAndGrantRewards();
            }
            if ((userNickname === '아빠' || userNickname === '희진부모') && recentQuizLogs.length === 0) {
                loadRecentQuizLogs();
            }
            renderHabitSection();
            if (userNickname === '아빠' || userNickname === '희진부모') {
                currentMainTab = 'life';
            }
            if (currentMainTab) switchMainTab(currentMainTab);
        }

        function syncDraftWithSelectedDate() {
            const existing = habitRecordsMap[selectedHabitDate];
            if (existing) {
                draftAttendance = existing.attendance || null;
                draftAttendanceReason = existing.attendance_reason || null;
                draftAttendanceReasonText = existing.attendance_reason_text || '';
                draftEveningStudy = (existing.evening_study !== undefined && existing.evening_study !== null) ? existing.evening_study : null;
                draftStudyAttitude = existing.study_attitude || null;
                draftFocusOnTime = !!existing.focus_ontime;
                draftFocusDeep = !!existing.focus_deep;
                draftAbsenceReason = existing.absence_reason || null;
                draftReasonText = existing.reason_text || '';
                draftAssignments = Array.isArray(existing.assignments) ? JSON.parse(JSON.stringify(existing.assignments)) : [];
                draftPromises = Array.isArray(existing.promises) ? JSON.parse(JSON.stringify(existing.promises)) : [];
                draftMemo = existing.memo || '';
            } else {
                draftAttendance = null;
                draftAttendanceReason = null;
                draftAttendanceReasonText = '';
                draftEveningStudy = null;
                draftStudyAttitude = null;
                draftFocusOnTime = false;
                draftFocusDeep = false;
                draftAbsenceReason = null;
                draftReasonText = '';
                draftAssignments = [];
                draftPromises = [];
                draftMemo = '';
            }
        }

                        function getTargetChild() {
            if (userNickname === '희진부모' || userNickname === '희진') return '희진';
            return '아람';
        }

        // ===================================================
        // 📊 학부모 전용: 퀴즈 풀이 & 오답노트 리포트
        // ===================================================
        let recentQuizLogs = [];
        let isQuizLogsLoading = false;
        let aiAnalysisResult = null;
        let isAiAnalyzing = false;

        async function loadRecentQuizLogs() {
            if (isQuizLogsLoading) return;
            isQuizLogsLoading = true;
            const targetChild = getTargetChild();
            try {
                const { data, error } = await supabaseClient
                    .from('study_logs')
                    .select('*')
                    .eq('subject', 'COMMON_QUIZ')
                    .eq('creator', targetChild)
                    .order('created_at', { ascending: false })
                    .limit(50);

                if (!error && data) {
                    recentQuizLogs = data;
                }
            } catch(e) {
                console.error("loadRecentQuizLogs error:", e);
            } finally {
                isQuizLogsLoading = false;
                renderHabitSection();
            }
        }

        // 오답 텍스트 추출 및 모달/클립보드 복사
        function getWrongQuizText() {
            const parsedLogs = recentQuizLogs.map(l => {
                let d = {};
                try { d = JSON.parse(l.detail); } catch(e) { d = { isCorrect: false }; }
                return { ...l, parsed: d };
            });

            const wrongItems = parsedLogs.filter(item => !item.parsed.isCorrect);
            if (wrongItems.length === 0) {
                return null;
            }

            const targetChild = getTargetChild();
            let text = `📝 [${targetChild}의 오답노트 모음] (총 ${wrongItems.length}문제)\n`;
            text += `기록 일시: ${new Date().toLocaleDateString('ko-KR', { year:'numeric', month:'long', day:'numeric' })}\n`;
            text += `--------------------------------------------------\n\n`;

            wrongItems.forEach((item, idx) => {
                const p = item.parsed;
                const d = new Date(item.created_at);
                const timeStr = `${d.getMonth() + 1}월 ${d.getDate()}일 ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
                
                text += `${idx + 1}. [${p.category || '상식'}] ${p.question || item.content}\n`;
                text += `   ❌ ${targetChild}이가 고른 답: ${p.chosen || '(미선택)'}\n`;
                text += `   ⭕ 실제 정답: ${p.answer || '(정답 미표기)'}\n`;
                if (p.explanation) {
                    text += `   💡 핵심 해설: ${p.explanation}\n`;
                }
                text += `   🕒 풀이 시간: ${timeStr}\n\n`;
            });

            text += `--------------------------------------------------\n`;
            text += `Tip: ${targetChild}와 복습할 때 정답을 바로 알려주기보다는 왜 헷갈렸는지 힌트를 주며 대화해 보세요! 💖\n`;

            return text;
        }

        function openWrongQuizModal() {
            const text = getWrongQuizText();
            if (!text) {
                alert(`🎉 최근 푼 문제 중 틀린 문제가 없습니다! ${getTargetChild()}이가 아주 잘하고 있어요! 👏`);
                return;
            }

            const modalHtml = `
                <div class="child-detail-modal" id="wrong-quiz-modal" onclick="if(event.target === this) closeWrongQuizModal()">
                    <div class="child-modal-body" style="max-width: 540px; width: 92%;">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                            <div style="font-family:'Jua', sans-serif; font-size:18px; color:#1e293b; display:flex; align-items:center; gap:6px;">
                                <span>📋 ${getTargetChild()} 오답노트 모아보기</span>
                            </div>
                            <button type="button" onclick="closeWrongQuizModal()" style="background:none; border:none; font-size:20px; color:#94a3b8; cursor:pointer;">✕</button>
                        </div>
                        <div style="font-size:12px; color:#64748b; margin-bottom:10px; text-align:left;">
                            틀린 문제만 모아서 텍스트로 정리했습니다. 복사해서 카톡이나 메모장에 붙여넣어 활용하세요!
                        </div>
                        <textarea id="wrong-quiz-textarea" readonly style="width:100%; height:260px; padding:12px; border-radius:12px; border:1.5px solid #cbd5e1; font-size:13px; font-family:monospace; line-height:1.5; resize:none; background:#f8fafc; color:#1e293b; box-sizing:border-box;">${escapeHtml(text)}</textarea>
                        <div style="display:flex; gap:10px; margin-top:14px;">
                            <button type="button" onclick="copyWrongQuizText()" style="flex:1; background:linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color:white; border:none; padding:10px 14px; border-radius:12px; font-weight:bold; font-family:'Jua', sans-serif; cursor:pointer; font-size:14px; box-shadow:0 3px 10px rgba(79, 70, 229, 0.25);">📋 전체 텍스트 복사</button>
                            <button type="button" onclick="closeWrongQuizModal()" style="background:#e2e8f0; color:#475569; border:none; padding:10px 16px; border-radius:12px; font-weight:bold; font-family:'Jua', sans-serif; cursor:pointer; font-size:14px;">닫기</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        function closeWrongQuizModal() {
            const modal = document.getElementById('wrong-quiz-modal');
            if (modal) modal.remove();
        }

        function copyWrongQuizText() {
            const textarea = document.getElementById('wrong-quiz-textarea');
            if (!textarea) return;
            textarea.select();
            textarea.setSelectionRange(0, 99999);
            try {
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(textarea.value).then(() => {
                        alert("✅ 오답노트가 클립보드에 복사되었습니다! 카톡이나 메모장에 붙여넣으세요.");
                    });
                } else {
                    document.execCommand('copy');
                    alert("✅ 오답노트가 클립보드에 복사되었습니다!");
                }
            } catch(e) {
                document.execCommand('copy');
                alert("✅ 오답노트가 복사되었습니다!");
            }
        }

        // AI 학습 분석 & 취약점 총평 실행
        function runAiQuizAnalysis() {
            if (recentQuizLogs.length === 0) {
                const targetChild = getTargetChild();
            alert(`분석할 풀이 기록이 없습니다. ${targetChild}이가 문제를 푼 뒤 분석해 주세요!`);
                return;
            }

            isAiAnalyzing = true;
            renderHabitSection();

            setTimeout(() => {
                try {
                    const parsedLogs = recentQuizLogs.map(l => {
                        let d = {};
                        try { d = JSON.parse(l.detail); } catch(e) { d = { isCorrect: false }; }
                        return { ...l, parsed: d };
                    });

                    const totalCount = parsedLogs.length;
                    const correctCount = parsedLogs.filter(p => p.parsed.isCorrect).length;
                    const wrongCount = totalCount - correctCount;
                    const accuracy = Math.round((correctCount / totalCount) * 100);

                    // 카테고리별 통계 집계
                    const catMap = {};
                    parsedLogs.forEach(item => {
                        const cat = item.parsed.category || '일반상식';
                        if (!catMap[cat]) catMap[cat] = { total: 0, correct: 0, wrong: 0, wrongQuestions: [] };
                        catMap[cat].total++;
                        if (item.parsed.isCorrect) {
                            catMap[cat].correct++;
                        } else {
                            catMap[cat].wrong++;
                            catMap[cat].wrongQuestions.push(item.parsed.question || item.content);
                        }
                    });

                    // 강점 및 취약 카테고리 선별
                    const catList = Object.entries(catMap).map(([cat, stats]) => ({
                        cat,
                        ...stats,
                        rate: Math.round((stats.correct / stats.total) * 100)
                    }));

                    catList.sort((a, b) => a.rate - b.rate); // 정답률 낮은 순 (취약 순)
                    const weakest = catList.filter(c => c.wrong > 0)[0] || null;
                    const strongest = [...catList].reverse().filter(c => c.rate >= 70)[0] || null;

                    // 코칭 조언 및 총평 메시지 도출
                    let evaluation = "";
                    let advice = "";

                    if (accuracy >= 85) {
                        evaluation = `🌟 대단해요! 최근 정답률 ${accuracy}%로 대부분의 상식 개념을 아주 정확하게 이해하고 있습니다. 문제 해결에 대한 자신감이 높은 상태입니다.`;
                        advice = `정답을 많이 맞힌 만큼 큰 칭찬을 해주시고, 틀린 소수의 문제는 "아빠도 헷갈릴 뻔했다"며 가볍게 원리를 짚어주면 동기부여가 극대화됩니다.`;
                    } else if (accuracy >= 65) {
                        evaluation = `👍 기초 상식 이해도가 탄탄합니다 (최근 정답률 ${accuracy}%). 특정 분야에서 헷갈리는 보기를 마주쳤을 때 오답이 발생하고 있습니다.`;
                        advice = weakest 
                            ? `특히 [${weakest.cat}] 분야(오답 ${weakest.wrong}건)의 어휘나 개념을 헷갈려하고 있으니, 일상 대화에서 해당 주제를 자연스럽게 퀴즈로 내주며 복습을 도와주세요.`
                            : `전반적으로 골고루 잘 풀고 있습니다. 헷갈렸던 보기를 왜 선택했는지 아람이의 생각을 먼저 들어보는 코칭을 추천합니다.`;
                    } else {
                        evaluation = `🌱 열심히 도전 중입니다 (최근 정답률 ${accuracy}%). 아직 생소한 단어나 교과 외 개념이 포함되어 있어 짐작으로 고르는 경우가 관찰됩니다.`;
                        advice = `결과 점수보다는 "오늘도 어려운 퀴즈에 도전한 끈기"를 칭찬해 주세요. 아래 오답 텍스트를 복사해 쉬운 예시와 그림으로 개념을 한 번씩 이야기 나눠보세요.`;
                    }

                    aiAnalysisResult = {
                        analyzedAt: new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }),
                        totalCount,
                        correctCount,
                        wrongCount,
                        accuracy,
                        catList,
                        weakest,
                        strongest,
                        evaluation,
                        advice
                    };
                } catch(e) {
                    console.error("AI Analysis error:", e);
                    alert("분석 중 일시적인 오류가 발생했습니다.");
                } finally {
                    isAiAnalyzing = false;
                    renderHabitSection();
                }
            }, 600);
        }

        function generateQuizReportHtml() {
            const totalCount = recentQuizLogs.length;
            let correctCount = 0;
            let wrongCount = 0;

            const parsedLogs = recentQuizLogs.map(l => {
                let d = {};
                try { d = JSON.parse(l.detail); } catch(e) { d = { isCorrect: false }; }
                if (d.isCorrect) correctCount++;
                else wrongCount++;
                return { ...l, parsed: d };
            });

            const accuracy = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

            let logItemsHtml = '';
            if (parsedLogs.length === 0) {
                logItemsHtml = `
                    <div style="text-align:center; padding:18px; color:#94a3b8; font-size:13px; font-family:'Jua', sans-serif;">
                        아직 ${getTargetChild()}이가 푼 퀴즈 기록이 없습니다. 문제를 풀면 여기에 실시간으로 기록됩니다! 💖
                    </div>
                `;
            } else {
                logItemsHtml = parsedLogs.map(item => {
                    const p = item.parsed;
                    const isCor = !!p.isCorrect;
                    const dateObj = new Date(item.created_at);
                    const timeStr = `${dateObj.getMonth() + 1}월 ${dateObj.getDate()}일 ${dateObj.getHours().toString().padStart(2, '0')}:${dateObj.getMinutes().toString().padStart(2, '0')}`;

                    return `
                        <div class="quiz-log-item ${isCor ? 'correct' : 'wrong'}">
                            <div class="quiz-log-top">
                                <span class="quiz-log-tag">${isCor ? '⭕ 정답 (+50원)' : '❌ 오답'}</span>
                                <span class="quiz-log-time">🕒 ${timeStr}</span>
                            </div>
                            <div class="quiz-log-question">
                                [${escapeHtml(p.category || '상식')}] ${escapeHtml(p.question || item.content)}
                            </div>
                            <div class="quiz-log-detail">
                                ${isCor 
                                    ? `선택한 정답: <span class="correct-choice">${escapeHtml(p.chosen || p.answer)}</span>`
                                    : `선택한 오답: <span class="wrong-choice">${escapeHtml(p.chosen)}</span> / 실제 정답: <span class="correct-choice">${escapeHtml(p.answer)}</span>`
                                }
                                ${!isCor && p.explanation ? `<div style="margin-top:4px; font-size:11px; color:#64748b;">💡 해설: ${escapeHtml(p.explanation)}</div>` : ''}
                            </div>
                        </div>
                    `;
                }).join('');
            }

            // AI 분석 결과 카드 HTML
            let aiBoxHtml = '';
            if (isAiAnalyzing) {
                aiBoxHtml = `
                    <div class="quiz-ai-analysis-card loading">
                        <div style="font-size:14px; font-weight:bold; color:#6366f1; margin-bottom:4px;">🤖 AI가 ${getTargetChild()}의 풀이 데이터를 꼼꼼히 분석하고 있습니다...</div>
                        <div style="font-size:12px; color:#94a3b8;">오답 패턴, 취약 카테고리, 맞춤형 칭찬 코칭 팁을 도출하는 중입니다.</div>
                    </div>
                `;
            } else if (aiAnalysisResult) {
                const r = aiAnalysisResult;
                const catBadges = r.catList.map(c => `
                    <div class="quiz-cat-badge ${c.wrong > 0 ? (c.rate < 60 ? 'bad' : 'warn') : 'good'}">
                        <strong>${escapeHtml(c.cat)}</strong> ${c.rate}% (${c.correct}/${c.total})
                    </div>
                `).join('');

                aiBoxHtml = `
                    <div class="quiz-ai-analysis-card">
                        <div class="quiz-ai-header">
                            <div class="quiz-ai-title">🤖 AI 학습 진단 & 아빠표 코칭 리포트</div>
                            <span class="quiz-ai-time">분석 시각: ${r.analyzedAt}</span>
                        </div>
                        <div class="quiz-ai-body">
                            <div class="quiz-ai-section">
                                <div class="quiz-ai-sec-title">📌 종합 진단 총평</div>
                                <div class="quiz-ai-sec-desc">${r.evaluation}</div>
                            </div>

                            <div class="quiz-ai-section">
                                <div class="quiz-ai-sec-title">📊 영역별 성취도</div>
                                <div class="quiz-cat-list">${catBadges}</div>
                            </div>

                            ${r.weakest ? `
                            <div class="quiz-ai-section highlight-weak">
                                <div class="quiz-ai-sec-title">⚠️ 취약 영역 주의보: [${escapeHtml(r.weakest.cat)}]</div>
                                <div class="quiz-ai-sec-desc">${r.weakest.total}문제 중 ${r.weakest.wrong}문제를 틀렸습니다. 헷갈려 한 문제들을 오답노트로 복습하면 실력이 쑥쑥 늘어납니다!</div>
                            </div>
                            ` : ''}

                            <div class="quiz-ai-section highlight-advice">
                                <div class="quiz-ai-sec-title">💡 아빠를 위한 맞춤 코칭 가이드</div>
                                <div class="quiz-ai-sec-desc">${r.advice}</div>
                            </div>
                        </div>
                    </div>
                `;
            }

            return `
                <div class="quiz-report-card">
                    <div class="quiz-report-header">
                        <div class="quiz-report-title">
                            <span>📊 ${getTargetChild()}의 퀴즈 풀이 & 오답노트 리포트</span>
                        </div>
                        <div class="quiz-report-actions">
                            <button type="button" class="quiz-report-btn secondary" onclick="openWrongQuizModal()" title="틀린 문제만 텍스트로 모아보기">📋 오답 텍스트</button>
                            <button type="button" class="quiz-report-btn primary" onclick="runAiQuizAnalysis()" title="AI 정오답 및 취약점 분석">🤖 AI 분석</button>
                            <button type="button" class="quiz-report-refresh-btn" onclick="loadRecentQuizLogs()" title="최근 풀이 새로고침">🔄</button>
                        </div>
                    </div>

                    <div class="quiz-stat-summary-row">
                        <div class="quiz-stat-box">
                            <div class="label">총 풀이 문제</div>
                            <div class="val" style="color:#6366f1;">${totalCount}개</div>
                        </div>
                        <div class="quiz-stat-box">
                            <div class="label">정답 / 오답</div>
                            <div class="val" style="color:#10b981;">${correctCount} / <span style="color:#ef4444;">${wrongCount}</span></div>
                        </div>
                        <div class="quiz-stat-box">
                            <div class="label">정답률</div>
                            <div class="val" style="color:#f59e0b;">${accuracy}%</div>
                        </div>
                    </div>

                    ${aiBoxHtml}

                    <div style="font-size:12px; font-weight:bold; color:#475569; margin-bottom:8px; margin-top:14px; display:flex; justify-content:space-between; align-items:center;">
                        <span>📝 최근 풀이 상세 내역 (최근 50개):</span>
                        <span style="font-size:11px; color:#94a3b8; font-weight:normal;">틀린 문제는 붉은색 라벨</span>
                    </div>
                    <div class="quiz-log-list">
                        ${logItemsHtml}
                    </div>
                </div>
            `;
        }


        function renderHabitSection() {
            const container = document.getElementById('habit-container');
            if (!container) return;

            if (userNickname === '희진부모') {
                renderHeejinParentView(container);
            } else if (userNickname === '희진') {
                container.innerHTML = `<div style="text-align:center; padding:30px; font-family:'Jua', sans-serif; color:#64748b;">희진이는 상식 퀴즈 풀이 전용 모드입니다. 😊</div>`;
            } else if (userNickname === '아빠' && !isDadPreviewMode) {
                renderDadHabitView(container);
            } else {
                renderChildHabitView(container);
            }
        }

        // 🌟 희진 학부모 전용 뷰: 아람이네 출결/약속/과제/일정은 철저히 차단하고 오직 희진이 퀴즈 리포트만 깔끔하게 노출
        function renderHeejinParentView(container) {
            container.innerHTML = `
                <div class="habit-content-card" style="margin-bottom:18px;">
                    <div class="habit-header">
                        <div class="habit-title">👩‍👧 희진이 상식 퀴즈 &amp; 학습 관리</div>
                        <div class="habit-subtitle">희진이가 푼 퀴즈 정오답 현황 및 AI 취약점 분석 리포트입니다. 💖</div>
                    </div>
                    <!-- 📊 희진이 퀴즈 풀이 &amp; 오답 리포트 -->
                    ${generateQuizReportHtml()}
                </div>
            `;
        }

        function renderDadHabitView(container) {
            const existing = habitRecordsMap[selectedHabitDate];
            const hasRecord = !!existing;
            const stats = getMonthlyHabitStats(habitCalYear, habitCalMonth);

            // 출결 버튼 활성화 상태
            const isOntimeActive = (draftAttendance === 'ON_TIME') ? 'active-ontime' : '';
            const isLateActive = (draftAttendance === 'LATE') ? 'active-late' : '';
            const isEarlyActive = (draftAttendance === 'EARLY_LEAVE') ? 'active-early' : '';
            const isAbsentActive = (draftAttendance === 'ABSENT') ? 'active-absent' : '';
            const isHolidayActive = (draftAttendance === 'HOLIDAY') ? 'active-holiday' : '';

            // 공부 여부 활성화 상태
            const isStudyActive = (draftEveningStudy === true) ? 'active-study' : '';
            const isNoStudyActive = (draftEveningStudy === false) ? 'active-nostudy' : '';

            // 공부 태도 활성화 상태 (공부한 날)
            const isAttExcellent = (draftStudyAttitude === 'EXCELLENT') ? 'active-study' : '';
            const isAttGood = (draftStudyAttitude === 'GOOD') ? 'active-ontime' : '';
            const isAttPoor = (draftStudyAttitude === 'NEEDS_FOCUS') ? 'active-late' : '';

            // 못한 날 사유 활성화 상태 (공부 쉼/못함)
            const isR_Sick = (draftAbsenceReason === 'REST_SICK') ? 'active-sick' : '';
            const isR_Exam = (draftAbsenceReason === 'REST_EXAM') ? 'active-exam' : '';
            const isR_Travel = (draftAbsenceReason === 'REST_TRAVEL') ? 'active-travel' : '';
            const isR_Fatigue = (draftAbsenceReason === 'REST_FATIGUE') ? 'active-nostudy' : '';
            const isR_Custom = (draftAbsenceReason === 'REST_CUSTOM') ? 'active-late' : '';

            // 과제 목록 HTML 생성
            let assignmentsHtml = '';
            if (draftAssignments.length === 0) {
                assignmentsHtml = `<div style="font-size:12px; color:#94a3b8; text-align:center; padding:10px;">등록된 과제가 없습니다. 아래에서 숙제를 내주세요! ✍️</div>`;
            } else {
                draftAssignments.forEach((task, idx) => {
                    assignmentsHtml += `
                        <div class="task-item ${task.done ? 'completed' : ''}">
                            <input type="checkbox" class="task-checkbox" ${task.done ? 'checked' : ''} onchange="toggleAssignment(${idx})">
                            <span class="task-text">${escapeHtml(task.text)}</span>
                            ${task.dueDate ? `<span class="task-due-badge">~${task.dueDate.slice(5)}까지</span>` : ''}
                            <button type="button" class="task-del-btn" onclick="deleteAssignment(${idx})" title="과제 삭제">✕</button>
                        </div>
                    `;
                });
            }

            // 약속 목록 HTML 생성
            let promisesHtml = '';
            if (draftPromises.length === 0) {
                promisesHtml = `<div style="font-size:12px; color:#94a3b8; text-align:center; padding:10px;">아람이와 함께 지키기로 한 약속을 적어보세요! 🤝</div>`;
            } else {
                draftPromises.forEach((prom, idx) => {
                    promisesHtml += `
                        <div class="task-item ${prom.done ? 'completed' : ''}">
                            <input type="checkbox" class="task-checkbox" ${prom.done ? 'checked' : ''} onchange="togglePromise(${idx})">
                            <span class="task-text">🤙 ${escapeHtml(prom.text)}</span>
                            <button type="button" class="task-del-btn" onclick="deletePromise(${idx})" title="약속 삭제">✕</button>
                        </div>
                    `;
                });
            }

            let html = `
                <div class="habit-header">
                    <div class="habit-title">👨‍👧 아람이 출결·생활·과제 코칭 관리</div>
                    <div class="habit-subtitle">매일 출결, 공부 태도 및 과제·약속을 꼼꼼하게 챙겨주세요! 💖</div>
                    <button onclick="toggleDadPreview(true)" style="margin-top:10px; background:linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); color:white; border:none; padding:6px 14px; border-radius:14px; font-size:13px; font-weight:bold; cursor:pointer; font-family:'Jua', sans-serif; box-shadow:0 2px 6px rgba(0,0,0,0.1);">👀 아람이 화면(달력) 미리보기</button>
                </div>

                <!-- 🎯 아빠가 준 특별 미션 & 과제 카드 (아람이 화면) -->
                ${generateChildMissionBoxHtml()}

                <!-- 주요 일정 & D-Day 카드 -->
                ${generateScheduleCardHtml(true)}

                <!-- 날짜 선택 바 -->
                <div class="habit-date-bar">
                    <button class="habit-date-btn" onclick="stepHabitDate(-1)">◀ 어제</button>
                    <div class="habit-date-center">
                        <input type="date" class="habit-date-picker" id="habit-date-input" value="${selectedHabitDate}" onchange="changeHabitDate(this.value)">
                        <span style="font-size:12px; color:#ff758c; font-weight:bold; font-family:'Nunito', sans-serif;">${formatFriendlyDate(selectedHabitDate)}</span>
                    </div>
                    <div style="display:flex; gap:4px; flex-shrink:0;">
                        <button class="habit-date-btn" onclick="setHabitDateToToday()">오늘 📅</button>
                        <button class="habit-date-btn" onclick="stepHabitDate(1)">내일 ▶</button>
                    </div>
                </div>

                <!-- 1) 출결 관리 (정상, 지각, 조퇴, 결석, 주말/휴일) -->
                <div class="habit-form-group">
                    <div class="habit-form-label">
                        <span>⏰ 학교 출결 상태</span>
                        <span style="font-size:12px; color:#94a3b8; font-weight:normal;">(클릭하여 선택/해제)</span>
                    </div>
                    <div class="habit-toggle-grid" style="grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));">
                        <button type="button" class="habit-toggle-btn ${isOntimeActive}" onclick="setHabitAttendance('ON_TIME')">
                            <span>☀️</span> 정상 출석
                        </button>
                        <button type="button" class="habit-toggle-btn ${isLateActive}" onclick="setHabitAttendance('LATE')">
                            <span>⏰</span> 지각
                        </button>
                        <button type="button" class="habit-toggle-btn ${isEarlyActive}" onclick="setHabitAttendance('EARLY_LEAVE')">
                            <span>🚪</span> 조퇴
                        </button>
                        <button type="button" class="habit-toggle-btn ${isAbsentActive}" onclick="setHabitAttendance('ABSENT')">
                            <span>🚫</span> 결석
                        </button>
                        <button type="button" class="habit-toggle-btn ${isHolidayActive}" onclick="setHabitAttendance('HOLIDAY')">
                            <span>🏖️</span> 주말/휴일
                        </button>
                    </div>

                    <!-- 1-A) 결석 또는 조퇴 시 사유 작성 영역 -->
                    ${(draftAttendance === 'ABSENT' || draftAttendance === 'EARLY_LEAVE') ? `
                    <div class="coaching-section" style="background:#fff1f2; border:1.5px solid #fecdd3; margin-top:10px;">
                        <div class="coaching-section-title" style="color:#b91c1c;">
                            <span>${draftAttendance === 'ABSENT' ? '🚫 결석 사유 기록' : '🚪 조퇴 사유 기록'}</span>
                            <span style="font-size:11px; font-weight:normal; color:#dc2626;">사유 유형과 상세 내용을 기록해주세요</span>
                        </div>
                        <div class="habit-toggle-grid" style="grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); margin-bottom:10px;">
                            <button type="button" class="habit-toggle-btn ${draftAttendanceReason === 'SICK' ? 'active-absent' : ''}" onclick="setAttendanceReason('SICK')">
                                <span>🤒</span> 질병/감기 (병결)
                            </button>
                            <button type="button" class="habit-toggle-btn ${draftAttendanceReason === 'EXPERIENCE' ? 'active-absent' : ''}" onclick="setAttendanceReason('EXPERIENCE')">
                                <span>✈️</span> 체험/가정학습
                            </button>
                            <button type="button" class="habit-toggle-btn ${draftAttendanceReason === 'FAMILY' ? 'active-absent' : ''}" onclick="setAttendanceReason('FAMILY')">
                                <span>💐</span> 경조사/가족일
                            </button>
                            <button type="button" class="habit-toggle-btn ${draftAttendanceReason === 'CUSTOM' ? 'active-absent' : ''}" onclick="setAttendanceReason('CUSTOM')">
                                <span>✏️</span> 기타 사유
                            </button>
                        </div>
                        <input type="text" id="attendance-reason-input" class="habit-memo-input" style="background:white; border:1px solid #fda4af;" placeholder="${draftAttendance === 'ABSENT' ? '결석' : '조퇴'} 사유 상세 (예: 독감으로 인한 병원 진료 및 가정보육, 진료확인서 제출 예정)" value="${escapeHtml(draftAttendanceReasonText)}" oninput="draftAttendanceReasonText = this.value" maxlength="80">
                    </div>
                    ` : ''}
                </div>

                <!-- 2) 오늘 공부 여부 -->
                <div class="habit-form-group">
                    <div class="habit-form-label">
                        <span>📖 오늘 공부 진행 여부</span>
                        <span style="font-size:12px; color:#94a3b8; font-weight:normal;">(공부한 날 vs 쉼/못한 날)</span>
                    </div>
                    <div class="habit-toggle-grid" style="grid-template-columns: 1fr 1fr;">
                        <button type="button" class="habit-toggle-btn ${isStudyActive}" onclick="setHabitEveningStudy(true)">
                            <span>✨</span> 오늘 공부 완료! 👑
                        </button>
                        <button type="button" class="habit-toggle-btn ${isNoStudyActive}" onclick="setHabitEveningStudy(false)">
                            <span>💤</span> 오늘 공부 쉼 / 못함
                        </button>
                    </div>
                </div>

                <!-- 2-A) 공부한 날: 태도 평가 (공부 완료 시 표시) -->
                ${draftEveningStudy === true ? `
                <div class="coaching-section" style="background:#f0fdf4; border-color:#bbf7d0;">
                    <div class="coaching-section-title" style="color:#166534;">
                        <span>🌟 공부한 날 태도 평가</span>
                        <span style="font-size:11px; font-weight:normal; color:#15803d;">오늘 공부 몰입도는 어땠나요?</span>
                    </div>
                    <div class="habit-toggle-grid" style="grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));">
                        <button type="button" class="habit-toggle-btn ${isAttExcellent}" onclick="setHabitStudyAttitude('EXCELLENT')">
                            <span>🌟</span> 최고! (집중 만점)
                        </button>
                        <button type="button" class="habit-toggle-btn ${isAttGood}" onclick="setHabitStudyAttitude('GOOD')">
                            <span>😊</span> 보통 (성실하게 완수)
                        </button>
                        <button type="button" class="habit-toggle-btn ${isAttPoor}" onclick="setHabitStudyAttitude('NEEDS_FOCUS')">
                            <span>🥱</span> 집중 부족 (딴짓/피곤)
                        </button>
                    <!-- 2-A-2) 정시 시작 & 몰입 퀘스트 스탬프 토글 -->
                    <div style="margin-top:10px; padding-top:10px; border-top:1px dashed #bbf7d0;">
                        <div style="font-size:12px; font-weight:bold; color:#15803d; margin-bottom:6px;">🎯 정시 시작 &amp; 몰입 퀘스트 체크 (5회 달성 시 편의점 쿠폰/맛있는 간식 선물!)</div>
                        <div class="habit-toggle-grid" style="grid-template-columns: 1fr 1fr;">
                            <button type="button" class="habit-toggle-btn ${draftFocusOnTime ? 'active-ontime' : ''}" onclick="toggleFocusOnTime()">
                                <span>⏰</span> 정시 시작 / 시간 엄수
                            </button>
                            <button type="button" class="habit-toggle-btn ${draftFocusDeep ? 'active-study' : ''}" onclick="toggleFocusDeep()">
                                <span>🌟</span> 집중 몰입 완료
                            </button>
                        </div>
                    </div>
                </div>
                ` : ''}

                <!-- 2-B) 못한 날: 사유 관리 (공부 쉼/못함 선택 시 표시) -->
                ${draftEveningStudy === false ? `
                <div class="coaching-section" style="background:#fff1f2; border-color:#fecdd3;">
                    <div class="coaching-section-title" style="color:#9f1239;">
                        <span>📝 공부 못한 날 사유 관리</span>
                        <span style="font-size:11px; font-weight:normal; color:#be123c;">사유를 선택하고 메모를 남겨주세요</span>
                    </div>
                    <div class="habit-toggle-grid" style="grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); margin-bottom:10px;">
                        <button type="button" class="habit-toggle-btn ${isR_Sick}" onclick="setHabitAbsenceReason('REST_SICK')">
                            <span>🤒</span> 감기/병원
                        </button>
                        <button type="button" class="habit-toggle-btn ${isR_Exam}" onclick="setHabitAbsenceReason('REST_EXAM')">
                            <span>📝</span> 시험/수행
                        </button>
                        <button type="button" class="habit-toggle-btn ${isR_Travel}" onclick="setHabitAbsenceReason('REST_TRAVEL')">
                            <span>✈️</span> 가족행사
                        </button>
                        <button type="button" class="habit-toggle-btn ${isR_Fatigue}" onclick="setHabitAbsenceReason('REST_FATIGUE')">
                            <span>😴</span> 피로/컨디션
                        </button>
                        <button type="button" class="habit-toggle-btn ${isR_Custom}" onclick="setHabitAbsenceReason('REST_CUSTOM')">
                            <span>✏️</span> 기타 사유
                        </button>
                    </div>
                    <input type="text" id="habit-reason-text" class="habit-memo-input" style="background:white;" placeholder="구체적인 사유를 적어주세요 (예: 치과 진료 후 휴식, 친척 결혼식)" value="${escapeHtml(draftReasonText)}" oninput="draftReasonText = this.value" maxlength="80">
                </div>
                ` : ''}

                <!-- 3) 내준 과제 관리 (Assignments) -->
                <div class="coaching-section">
                    <div class="coaching-section-title">
                        <span>📝 내준 과제 (숙제 체크)</span>
                        <span style="font-size:11px; color:#64748b; font-weight:normal;">완료 시 체크박스 클릭</span>
                    </div>
                    <div class="task-list" id="assignment-list">
                        ${assignmentsHtml}
                    </div>
                    <div class="task-input-row">
                        <input type="text" id="new-assignment-input" class="task-input" placeholder="새 과제 입력 (예: 수학 익힘책 20~24p 풀기)" onkeydown="if(event.key==='Enter') addAssignment()">
                        <input type="date" id="new-assignment-date" class="habit-date-picker" style="padding:6px; font-size:12px;" title="마감일">
                        <button type="button" class="task-add-btn" onclick="addAssignment()">과제 추가</button>
                    </div>
                </div>

                <!-- 4) 함께 하기로 한 약속 (Commitments) -->
                <div class="coaching-section">
                    <div class="coaching-section-title">
                        <span>🤝 함께 하기로 한 약속</span>
                        <span style="font-size:11px; color:#64748b; font-weight:normal;">서로 약속한 실천 사항</span>
                    </div>
                    <div class="task-list" id="promise-list">
                        ${promisesHtml}
                    </div>
                    <div class="task-input-row">
                        <input type="text" id="new-promise-input" class="task-input" placeholder="함께할 약속 입력 (예: 자기 전 가방 미리 싸놓기)" onkeydown="if(event.key==='Enter') addPromise()">
                        <button type="button" class="task-add-btn" onclick="addPromise()">약속 추가</button>
                    </div>
                </div>

                <!-- 5) 칭찬 메모 / 응원 한마디 -->
                <div class="habit-form-group" style="margin-top:16px;">
                    <div class="habit-form-label">
                        <span>💌 아람이에게 전할 응원 한마디 / 코칭 피드백</span>
                    </div>
                    <input type="text" id="habit-memo-input" class="habit-memo-input" placeholder="예: 약속한 과제를 스스로 먼저 끝낸 아람이 최고야! 💕" value="${escapeHtml(draftMemo)}" oninput="draftMemo = this.value" maxlength="80">
                </div>

                <!-- 저장 및 삭제 액션 바 -->
                <div class="habit-action-bar">
                    <button type="button" id="habit-save-btn" class="habit-save-btn" onclick="saveHabitRecord()">
                        💾 ${hasRecord ? '기록 수정하기' : '기록 저장하기'} 💖
                    </button>
                    ${hasRecord ? `<button type="button" class="habit-delete-btn" onclick="deleteHabitRecord()" title="기록 삭제">🗑️ 삭제</button>` : ''}
                </div>

                <!-- 📊 아람이 퀴즈 풀이 & 오답 리포트 (아빠 화면) -->
                ${generateQuizReportHtml()}

                <!-- 퀘스트 & 보상 쿠폰 관리 섹션 (아빠 화면) -->
                ${renderDadRewardManagerHtml()}

                <!-- 주간 달력 스트립 (기본 1주일 단위) -->
                ${generateHabitWeekStripHtml(true)}

                <!-- 필요할 때만 월간 달력 전체보기 토글 버튼 -->
                <div style="text-align:center; margin-top:16px;">
                    <button type="button" class="habit-toggle-month-btn" onclick="toggleHabitMonthCalendar()">
                        ${isHabitMonthExpanded ? '▲ 월간 달력 접기' : '📅 월간 달력 전체보기 ▾'}
                    </button>
                </div>

                <!-- 월간 달력 (펼쳤을 때만 표시) -->
                ${isHabitMonthExpanded ? `
                <div id="habit-dad-month-section" style="margin-top:14px;">
                    <div style="margin-top:10px; padding-top:14px; border-top: 1px dashed #ffd1dc;">
                        <div style="font-family:'Jua', sans-serif; font-size:15px; color:#2d3436; text-align:center;">
                            📊 ${habitCalYear}년 ${habitCalMonth + 1}월 현황 요약
                        </div>
                        <div class="habit-stats-row">
                            <div class="habit-stat-badge">
                                <div class="habit-stat-label">☀️ 정상 등교</div>
                                <div class="habit-stat-value" style="color:#059669;">${stats.onTimeCount}일</div>
                            </div>
                            <div class="habit-stat-badge">
                                <div class="habit-stat-label">⏰ 지각</div>
                                <div class="habit-stat-value" style="color:#ef4444;">${stats.lateCount}일</div>
                            </div>
                            <div class="habit-stat-badge highlight">
                                <div class="habit-stat-label">📖 저녁 공부 완료</div>
                                <div class="habit-stat-value" style="color:#6366f1;">${stats.studyCount}일</div>
                            </div>
                        </div>
                    </div>
                    ${generateHabitCalendarHtml(habitCalYear, habitCalMonth, true)}
                </div>
                ` : ''}
            `;

            container.innerHTML = html;
        }

                function getActiveTasksAndPromises() {
            // 모든 날짜의 기록을 순회하며 미완료된(done: false) 과제와 약속을 수집
            const uncompletedAssignments = [];
            const uncompletedPromises = [];
            const seenTaskIds = new Set();
            const seenPromiseIds = new Set();

            // 1. 현재 선택된 날짜의 draft 항목 우선
            draftAssignments.forEach(t => {
                if (!seenTaskIds.has(t.text)) {
                    seenTaskIds.add(t.text);
                    uncompletedAssignments.push(t);
                }
            });
            draftPromises.forEach(p => {
                if (!seenPromiseIds.has(p.text)) {
                    seenPromiseIds.add(p.text);
                    uncompletedPromises.push(p);
                }
            });

            // 2. 다른 날짜들의 기록에서 아직 완료 안 된 과제/약속도 함께 취합
            const sortedDates = Object.keys(habitRecordsMap).sort().reverse();
            sortedDates.forEach(dateStr => {
                const rec = habitRecordsMap[dateStr];
                if (rec) {
                    if (Array.isArray(rec.assignments)) {
                        rec.assignments.forEach(t => {
                            if (!t.done && !seenTaskIds.has(t.text)) {
                                seenTaskIds.add(t.text);
                                uncompletedAssignments.push(t);
                            }
                        });
                    }
                    if (Array.isArray(rec.promises)) {
                        rec.promises.forEach(p => {
                            if (!p.done && !seenPromiseIds.has(p.text)) {
                                seenPromiseIds.add(p.text);
                                uncompletedPromises.push(p);
                            }
                        });
                    }
                }
            });

            // 기본 필수 미션이 없으면 '오답노트 만들 시험지 가져오기' 자동 보장
            if (uncompletedAssignments.length === 0 && !seenTaskIds.has('오답노트 만들 시험지 가져오기')) {
                uncompletedAssignments.push({
                    id: Date.now(),
                    text: '오답노트 만들 시험지 가져오기',
                    dueDate: '',
                    done: false
                });
            }

            return {
                assignments: uncompletedAssignments,
                promises: uncompletedPromises
            };
        }

        function generateChildMissionBoxHtml() {
            const { assignments, promises } = getActiveTasksAndPromises();

            if (assignments.length === 0 && promises.length === 0) {
                return '';
            }

            let taskItemsHtml = '';
            assignments.forEach((task, idx) => {
                taskItemsHtml += `
                    <div class="child-task-card ${task.done ? 'done' : ''}">
                        <div class="child-task-left">
                            <span class="child-task-icon">${task.done ? '✅' : '📌'}</span>
                            <div class="child-task-text-wrap">
                                <span class="child-task-title ${task.done ? 'completed' : ''}">${escapeHtml(task.text)}</span>
                                ${task.dueDate ? `<span class="child-task-due">~${task.dueDate.slice(5)} 마감</span>` : ''}
                            </div>
                        </div>
                        <span class="child-task-status-badge ${task.done ? 'done' : 'ing'}">
                            ${task.done ? '완료 🎉' : '진행 중 ⏳'}
                        </span>
                    </div>
                `;
            });

            let promiseItemsHtml = '';
            promises.forEach((p, idx) => {
                promiseItemsHtml += `
                    <div class="child-task-card ${p.done ? 'done' : ''}">
                        <div class="child-task-left">
                            <span class="child-task-icon">${p.done ? '🤝' : '🌱'}</span>
                            <div class="child-task-text-wrap">
                                <span class="child-task-title ${p.done ? 'completed' : ''}">${escapeHtml(p.text)}</span>
                            </div>
                        </div>
                        <span class="child-task-status-badge ${p.done ? 'done' : 'ing'}">
                            ${p.done ? '실천 완료! 💖' : '약속 지키기 ✨'}
                        </span>
                    </div>
                `;
            });

            return `
                <div class="child-mission-container">
                    <div class="child-mission-header">
                        <div class="child-mission-title">
                            <span>🎯 아빠가 준 오늘의 특별 미션 & 과제</span>
                        </div>
                        <span class="child-mission-count">미션 ${assignments.length + promises.length}개</span>
                    </div>

                    ${assignments.length > 0 ? `
                        <div class="child-mission-subtitle">📝 실천 과제 (숙제/미션)</div>
                        <div class="child-task-list">${taskItemsHtml}</div>
                    ` : ''}

                    ${promises.length > 0 ? `
                        <div class="child-mission-subtitle" style="margin-top:10px;">🤝 아빠와 한 소중한 약속</div>
                        <div class="child-task-list">${promiseItemsHtml}</div>
                    ` : ''}
                </div>
            `;
        }


        function renderChildHabitView(container) {
            const todayStr = getLocalDateStr(new Date());
            const todayRecord = habitRecordsMap[todayStr];
            const stats = getMonthlyHabitStats(habitCalYear, habitCalMonth);
            const streak = calculateStudyStreak();

            let previewBanner = '';
            if (userNickname === '아빠' && isDadPreviewMode) {
                previewBanner = `
                    <div style="background:#eef2ff; border:2px solid #818cf8; border-radius:16px; padding:10px; margin-bottom:16px; text-align:center;">
                        <span style="font-size:13px; color:#3730a3; font-weight:bold;">[아이(아람이) 화면 미리보기 모드입니다]</span><br>
                        <button onclick="toggleDadPreview(false)" style="margin-top:6px; background:#4f46e5; color:white; border:none; padding:5px 14px; border-radius:10px; font-size:13px; font-weight:bold; cursor:pointer; font-family:'Jua', sans-serif;">✏️ 아빠 체크 화면으로 돌아가기</button>
                    </div>
                `;
            }

            // 아침 출결 상태 박스
            let attendanceHtml = '';
            if (todayRecord && todayRecord.attendance === 'ON_TIME') {
                attendanceHtml = `
                    <div class="child-item-box ontime">
                        <div class="child-item-icon">☀️</div>
                        <div class="child-item-content">
                            <div class="child-item-title">학교 출결</div>
                            <div class="child-item-text">지각 안 함! 멋지게 정시 등교 완료 ✨ (칭찬해요!)</div>
                        </div>
                    </div>
                `;
            } else if (todayRecord && todayRecord.attendance === 'LATE') {
                attendanceHtml = `
                    <div class="child-item-box late">
                        <div class="child-item-icon">⏰</div>
                        <div class="child-item-content">
                            <div class="child-item-title">학교 출결</div>
                            <div class="child-item-text">오늘은 조금 늦었어요! 내일은 10분 일찍 출발해봐요 💪</div>
                        </div>
                    </div>
                `;
            } else if (todayRecord && todayRecord.attendance === 'EARLY_LEAVE') {
                let earlyReason = todayRecord.attendance_reason_text || (todayRecord.attendance_reason === 'SICK' ? '병원 진료/질병' : '');
                attendanceHtml = `
                    <div class="child-item-box late" style="border-left-color:#f97316;">
                        <div class="child-item-icon">🚪</div>
                        <div class="child-item-content">
                            <div class="child-item-title">학교 출결 (조퇴)</div>
                            <div class="child-item-text">오늘 조퇴했어요.${earlyReason ? ` [사유: ${escapeHtml(earlyReason)}]` : ''} 푹 쉬고 건강 회복해요! 토닥토닥 🧡</div>
                        </div>
                    </div>
                `;
            } else if (todayRecord && todayRecord.attendance === 'ABSENT') {
                let absReason = todayRecord.attendance_reason_text || (todayRecord.attendance_reason === 'SICK' ? '질병/감기(병결)' : (todayRecord.attendance_reason === 'EXPERIENCE' ? '체험학습' : ''));
                attendanceHtml = `
                    <div class="child-item-box late" style="border-left-color:#ef4444; background:#fef2f2;">
                        <div class="child-item-icon">🚫</div>
                        <div class="child-item-content">
                            <div class="child-item-title">학교 출결 (결석)</div>
                            <div class="child-item-text">오늘 결석했어요.${absReason ? ` [사유: ${escapeHtml(absReason)}]` : ''} 컨디션 관리 잘하고 푹 쉬어요! 🌿</div>
                        </div>
                    </div>
                `;
            } else if (todayRecord && todayRecord.attendance === 'HOLIDAY') {
                attendanceHtml = `
                    <div class="child-item-box holiday">
                        <div class="child-item-icon">🏖️</div>
                        <div class="child-item-content">
                            <div class="child-item-title">학교 출결</div>
                            <div class="child-item-text">즐거운 주말 / 휴일이에요! 푹 쉬고 재충전해요 😊</div>
                        </div>
                    </div>
                `;
            } else {
                attendanceHtml = `
                    <div class="child-item-box waiting">
                        <div class="child-item-icon">⏳</div>
                        <div class="child-item-content">
                            <div class="child-item-title">학교 출결</div>
                            <div class="child-item-text">오늘 출석 체크 대기 중이에요 😊</div>
                        </div>
                    </div>
                `;
            }

            // 저녁 공부 상태 박스
            let studyHtml = '';
            const todayStudyInfo = getStudyStatusInfo(todayRecord ? todayRecord.evening_study : null);
            if (todayStudyInfo) {
                studyHtml = `
                    <div class="child-item-box ${todayStudyInfo.childClass}">
                        <div class="child-item-icon">${todayStudyInfo.icon}</div>
                        <div class="child-item-content">
                            <div class="child-item-title">${todayStudyInfo.childTitle}</div>
                            <div class="child-item-text">${todayStudyInfo.childText}</div>
                        </div>
                    </div>
                `;
            } else {
                studyHtml = `
                    <div class="child-item-box waiting">
                        <div class="child-item-icon">⏳</div>
                        <div class="child-item-content">
                            <div class="child-item-title">저녁 공부</div>
                            <div class="child-item-text">저녁 공부 체크 대기 중이에요 🌙</div>
                        </div>
                    </div>
                `;
            }

            // 칭찬 메모
            let memoHtml = '';
            if (todayRecord && todayRecord.memo) {
                memoHtml = `
                    <div class="child-memo-box">
                        💌 아빠의 응원: "${escapeHtml(todayRecord.memo)}" 💖
                    </div>
                `;
            }

            let html = `
                ${previewBanner}
                <div class="habit-header">
                    <div class="habit-title">🌟 나의 매일 출석 & 열공 현황판 🌟</div>
                    <div class="habit-subtitle">아빠가 매일 응원하며 챙겨주시는 나의 출석과 공부 기록이에요! 💖</div>
                </div>

                <!-- 오늘의 현황 카드 -->
                <div class="child-today-card">
                    <div class="child-today-header">
                        <div class="child-today-date">📅 오늘: ${formatFriendlyDate(todayStr)}</div>
                        <span style="font-size:12px; background:#ffe4e8; color:#ff758c; padding:3px 8px; border-radius:10px; font-weight:bold;">실시간</span>
                    </div>
                    ${attendanceHtml}
                    ${studyHtml}
                    ${memoHtml}
                </div>

                <!-- 주요 일정 & D-Day 카드 -->
                ${generateScheduleCardHtml(false)}

                <!-- 아람이 보물상자 & 보상 플랜 (퀘스트 & 인벤토리) -->
                ${generateChildRewardBoxHtml()}

                <!-- 주간 달력 스트립 (생활패턴에 맞춘 1주일 단위 기본 뷰) -->
                ${generateHabitWeekStripHtml(false)}

                <!-- 성취 요약 뱃지 -->
                <div class="habit-stats-row" style="margin-top:16px;">
                    <div class="habit-stat-badge highlight">
                        <div class="habit-stat-label">🏆 이번 달 저녁 공부</div>
                        <div class="habit-stat-value" style="color:#6366f1;">${stats.studyCount}일</div>
                    </div>
                    <div class="habit-stat-badge">
                        <div class="habit-stat-label">☀️ 정시 등교</div>
                        <div class="habit-stat-value" style="color:#059669;">${stats.onTimeCount}일</div>
                    </div>
                    <div class="habit-stat-badge">
                        <div class="habit-stat-label">🔥 연속 열공</div>
                        <div class="habit-stat-value" style="color:#f59e0b;">${streak}일째!</div>
                    </div>
                </div>

                <!-- 필요할 때만 월간 달력 전체보기 토글 버튼 -->
                <div style="text-align:center; margin-top:16px;">
                    <button type="button" class="habit-toggle-month-btn" onclick="toggleHabitMonthCalendar()">
                        ${isHabitMonthExpanded ? '▲ 월간 달력 접기' : '📅 이번 달 전체 달력 보기 ▾'}
                    </button>
                </div>

                <!-- 월간 달력 (펼쳤을 때만 표시) -->
                ${isHabitMonthExpanded ? `
                <div id="child-habit-month-section" style="margin-top:14px;">
                    ${generateHabitCalendarHtml(habitCalYear, habitCalMonth, false)}
                </div>
                ` : ''}
            `;

            container.innerHTML = html;
        }

        function generateHabitCalendarHtml(year, month, isDad) {
            const monthNames = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
            const firstDay = new Date(year, month, 1).getDay();
            const daysInMonth = new Date(year, month + 1, 0).getDate();
            const todayStr = getLocalDateStr(new Date());

            let html = `
                <div class="habit-calendar-wrap">
                    <div class="habit-cal-nav">
                        <button type="button" class="habit-cal-btn" onclick="changeHabitCalMonth(-1)">◀ 이전 달</button>
                        <div class="habit-cal-title">📅 ${year}년 ${monthNames[month]}</div>
                        <button type="button" class="habit-cal-btn" onclick="changeHabitCalMonth(1)">다음 달 ▶</button>
                    </div>
                    <div class="habit-cal-grid">
                        <div class="habit-cal-weekday sun">일</div>
                        <div class="habit-cal-weekday">월</div>
                        <div class="habit-cal-weekday">화</div>
                        <div class="habit-cal-weekday">수</div>
                        <div class="habit-cal-weekday">목</div>
                        <div class="habit-cal-weekday">금</div>
                        <div class="habit-cal-weekday sat">토</div>
            `;

            for (let i = 0; i < firstDay; i++) {
                html += `<div class="habit-cal-day other-month"></div>`;
            }

            for (let day = 1; day <= daysInMonth; day++) {
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                const isToday = (dateStr === todayStr);
                const isSelected = (isDad && dateStr === selectedHabitDate);
                const rec = habitRecordsMap[dateStr];

                let badgesHtml = '';
                if (rec) {
                    if (rec.attendance === 'ON_TIME') badgesHtml += '<span title="정상 등교">☀️</span>';
                    else if (rec.attendance === 'LATE') badgesHtml += '<span title="지각">⏰</span>';
                    else if (rec.attendance === 'HOLIDAY') badgesHtml += '<span title="휴일/주말">🏖️</span>';

                    const studyInfo = getStudyStatusInfo(rec.evening_study);
                    if (studyInfo) {
                        badgesHtml += `<span title="${studyInfo.title}">${studyInfo.badge}</span>`;
                    }

                    if (rec.memo) badgesHtml += '<span title="아빠 응원">💌</span>';
                }

                const dayEvents = getSchedulesForDate(dateStr);
                if (dayEvents && dayEvents.length > 0) {
                    dayEvents.forEach(ev => {
                        badgesHtml += `<span title="일정: ${escapeHtml(ev.title)}">${ev.icon}</span>`;
                    });
                }

                const clickHandler = isDad 
                    ? `changeHabitDate('${dateStr}')` 
                    : `showChildDayDetail('${dateStr}')`;

                html += `
                    <div class="habit-cal-day ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}" onclick="${clickHandler}" title="${dateStr}">
                        <div class="habit-cal-day-num">${day}</div>
                        <div class="habit-cal-badges">${badgesHtml}</div>
                    </div>
                `;
            }

            const totalCells = firstDay + daysInMonth;
            const remainder = totalCells % 7;
            if (remainder > 0) {
                for (let i = 0; i < 7 - remainder; i++) {
                    html += `<div class="habit-cal-day other-month"></div>`;
                }
            }

            html += `
                    </div>
                    <div style="font-size:11px; color:#888; text-align:center; margin-top:10px;">
                        ☀️ 정상등교 · ⏰ 지각 · 🏖️ 주말/휴일 · 📖 저녁공부 · 📝 수행평가 · 🤒 질병 · ✈️ 여행 · 💤 휴식 · 💌 응원 · 🗓️ 주요일정
                    </div>
                </div>
            `;
            return html;
        }

        function getMonthlyHabitStats(year, month) {
            const prefix = `${year}-${String(month + 1).padStart(2, '0')}`;
            let onTimeCount = 0;
            let lateCount = 0;
            let holidayCount = 0;
            let studyCount = 0;

            Object.keys(habitRecordsMap).forEach(dateStr => {
                if (dateStr.startsWith(prefix)) {
                    const rec = habitRecordsMap[dateStr];
                    if (rec.attendance === 'ON_TIME') onTimeCount++;
                    else if (rec.attendance === 'LATE') lateCount++;
                    else if (rec.attendance === 'HOLIDAY') holidayCount++;

                    if (rec.evening_study === true) studyCount++;
                }
            });

            return { onTimeCount, lateCount, holidayCount, studyCount };
        }

        function calculateStudyStreak() {
            let streak = 0;
            let checkDate = new Date();
            const todayStr = getLocalDateStr(checkDate);
            const todayRec = habitRecordsMap[todayStr];
            
            if (todayRec && todayRec.evening_study === true) {
                streak++;
                checkDate.setDate(checkDate.getDate() - 1);
            } else {
                checkDate.setDate(checkDate.getDate() - 1);
            }

            for (let i = 0; i < 60; i++) {
                const dStr = getLocalDateStr(checkDate);
                const rec = habitRecordsMap[dStr];
                if (rec && rec.evening_study === true) {
                    streak++;
                    checkDate.setDate(checkDate.getDate() - 1);
                } else {
                    break;
                }
            }
            return streak;
        }

        // 1) 정시 시작 & 몰입 퀘스트 스탬프 계산 (총 유효 스탬프 수)
        function getFocusStampCount() {
            let count = 0;
            Object.keys(habitRecordsMap).forEach(dStr => {
                const rec = habitRecordsMap[dStr];
                if (rec && rec.focus_ontime && rec.focus_deep) {
                    count++;
                }
            });
            return count;
        }

        // 2) 2주 퍼펙트 출결 퀘스트 연속일 수 계산 (최근 14일 연속 무결석·무지각·무조퇴)
        function getPerfectAttendanceStreak() {
            let streak = 0;
            let checkDate = new Date();
            // 오늘 날짜부터 역순으로 확인
            for (let i = 0; i < 60; i++) {
                const dStr = getLocalDateStr(checkDate);
                const rec = habitRecordsMap[dStr];
                const dayOfWeek = checkDate.getDay(); // 0: 일, 6: 토
                const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);

                if (rec) {
                    if (rec.attendance === 'ON_TIME' || (isWeekend && rec.attendance === 'HOLIDAY')) {
                        streak++;
                    } else if (rec.attendance === 'LATE' || rec.attendance === 'ABSENT' || rec.attendance === 'EARLY_LEAVE') {
                        break;
                    } else if (isWeekend) {
                        streak++; // 주말 미기록은 연속 유지
                    } else if (i === 0) {
                        // 오늘 아직 미체크면 이전 날부터 계산
                    } else {
                        break;
                    }
                } else if (isWeekend) {
                    streak++; // 기록 없어도 주말은 기본 통과
                } else if (i === 0) {
                    // 오늘 미체크인 경우 통과
                } else {
                    break;
                }
                checkDate.setDate(checkDate.getDate() - 1);
            }
            return Math.min(streak, 14);
        }

        // 3) 쿠폰 자동 발급 및 상태 체크 함수
        async function checkAndGrantRewards() {
            if (!userNickname) return;
            const focusCount = getFocusStampCount();
            const earnedFocusCoupons = Math.floor(focusCount / 5);
            const currentFocusCoupons = rewardCoupons.filter(c => c.type === 'FOCUS_5_STAMP');

            let updatedAny = false;
            // 도장 5개마다 쿠폰 1장씩 발급
            for (let i = currentFocusCoupons.length; i < earnedFocusCoupons; i++) {
                const newCouponId = `REWARD_FOCUS_${Date.now()}_${i + 1}`;
                const couponData = {
                    title: questConfig.focusRewardTitle || '🏪 편의점 3,000원 상품권',
                    type: 'FOCUS_5_STAMP',
                    rewardDesc: questConfig.focusRewardDesc || '정시 시작 & 몰입 퀘스트 5회 달성 축하 선물! 💖 (또는 아람이가 원하는 3,000원 간식 선물!) 🍰',
                    date: getLocalDateStr(new Date()),
                    status: 'PENDING', // PENDING (지급 대기) -> CLAIMED (아이가 부모님께 수령 완료) -> USED (맛있게 사용 완료)
                    created_at: new Date().toISOString()
                };

                try {
                    const { error } = await supabaseClient
                        .from('study_words')
                        .insert([{
                            word: newCouponId,
                            meaning: JSON.stringify(couponData),
                            subject: 'CHILD_REWARD',
                            category: '아람',
                            example: userNickname || '시스템'
                        }]);

                    if (!error) {
                        rewardCoupons.unshift({ id: newCouponId, ...couponData });
                        updatedAny = true;
                    }
                } catch(e) {
                    console.error("Grant focus reward error:", e);
                }
            }

            // 14일 퍼펙트 출결 골드 티켓
            const perfectStreak = getPerfectAttendanceStreak();
            const hasGoldTicket = rewardCoupons.some(c => c.type === 'PERFECT_ATTEND_14');
            if (perfectStreak >= 14 && !hasGoldTicket) {
                const goldCouponId = `REWARD_GOLD_${Date.now()}`;
                const goldData = {
                    title: questConfig.goldRewardTitle || '🏖️ 1일 학습 자유 휴식권 (골드 티켓)',
                    type: 'PERFECT_ATTEND_14',
                    rewardDesc: questConfig.goldRewardDesc || '2주 퍼펙트 출결(14일 무결석·무지각·무조퇴) 대기록 달성 보상! 👑',
                    date: getLocalDateStr(new Date()),
                    status: 'PENDING',
                    created_at: new Date().toISOString()
                };

                try {
                    const { error } = await supabaseClient
                        .from('study_words')
                        .insert([{
                            word: goldCouponId,
                            meaning: JSON.stringify(goldData),
                            subject: 'CHILD_REWARD',
                            category: '아람',
                            example: userNickname || '시스템'
                        }]);

                    if (!error) {
                        rewardCoupons.unshift({ id: goldCouponId, ...goldData });
                        updatedAny = true;
                    }
                } catch(e) {
                    console.error("Grant gold reward error:", e);
                }
            }

            return updatedAny;
        }

        // 아이 또는 아빠가 쿠폰 상태 변경 (수령 완료 / 사용 완료)
        async function updateCouponStatus(couponId, newStatus) {
            const coupon = rewardCoupons.find(c => c.id === couponId);
            if (!coupon) return;

            const oldStatus = coupon.status;
            coupon.status = newStatus;
            if (newStatus === 'CLAIMED') coupon.claimedAt = new Date().toISOString();
            if (newStatus === 'USED') coupon.usedAt = new Date().toISOString();

            try {
                await supabaseClient
                    .from('study_words')
                    .upsert({
                        word: coupon.id,
                        meaning: JSON.stringify(coupon),
                        subject: 'CHILD_REWARD',
                        category: '아람',
                        example: userNickname || '아람'
                    }, { onConflict: 'word' });

                confetti({
                    particleCount: 120,
                    spread: 80,
                    origin: { y: 0.6 },
                    colors: ['#ffc3a0', '#ffafbd', '#f6d365', '#fda085', '#84fab0']
                });

                renderHabitSection();
            } catch(e) {
                console.error("Update coupon status error:", e);
                coupon.status = oldStatus;
                alert("상태 저장 중 오류가 발생했습니다.");
            }
        }

        // 아이 화면 '보물상자 & 보상 플랜' HTML 생성
        function generateChildRewardBoxHtml() {
            const focusCount = getFocusStampCount();
            const currentCycleStamps = focusCount % 5;
            const remainingToNextCoupon = 5 - currentCycleStamps;
            const perfectStreak = getPerfectAttendanceStreak();
            const remainingToGold = Math.max(0, 14 - perfectStreak);
            const perfectPercent = Math.min(100, Math.round((perfectStreak / 14) * 100));

            // 스탬프 5칸 시각화
            let stampSlotsHtml = '';
            for (let i = 1; i <= 5; i++) {
                if (i <= currentCycleStamps) {
                    stampSlotsHtml += `<div class="quest-stamp-slot active" title="달성 완료!">⭐</div>`;
                } else {
                    stampSlotsHtml += `<div class="quest-stamp-slot empty" title="도전 중">${i}</div>`;
                }
            }

            // 인벤토리 쿠폰 목록 HTML
            let couponsHtml = '';
            if (rewardCoupons.length === 0) {
                couponsHtml = `<div style="text-align:center; color:#94a3b8; font-size:13px; padding:16px 0;">아직 획득한 보상 티켓이 없어요.<br>매일 정시 시작과 출결을 지키면 반짝이는 티켓이 생겨요! 🎁</div>`;
            } else {
                couponsHtml = rewardCoupons.map(coupon => {
                    let statusBadge = '';
                    let actionBtn = '';

                    if (coupon.status === 'PENDING') {
                        statusBadge = `<span class="coupon-status-badge pending">🎁 지급 대기</span>`;
                        actionBtn = `<button type="button" class="coupon-action-btn claim-btn" onclick="updateCouponStatus('${coupon.id}', 'CLAIMED')">✅ 부모님께 수령 완료!</button>`;
                    } else if (coupon.status === 'CLAIMED') {
                        statusBadge = `<span class="coupon-status-badge claimed">보관 중 (수령완료)</span>`;
                        actionBtn = `<button type="button" class="coupon-action-btn use-btn" onclick="updateCouponStatus('${coupon.id}', 'USED')">🎉 맛있게 사용 완료!</button>`;
                    } else if (coupon.status === 'USED') {
                        statusBadge = `<span class="coupon-status-badge used">✨ 사용 완료</span>`;
                        actionBtn = `<div style="font-size:12px; color:#10b981; font-weight:bold; margin-top:6px;">기분 좋은 보상 완료! 💖</div>`;
                    }

                    const isGold = (coupon.type === 'PERFECT_ATTEND_14');
                    return `
                        <div class="reward-coupon-card ${isGold ? 'gold' : ''}">
                            <div class="coupon-header">
                                <div class="coupon-title">${escapeHtml(coupon.title)}</div>
                                ${statusBadge}
                            </div>
                            <div class="coupon-desc">${escapeHtml(coupon.rewardDesc || '')}</div>
                            <div class="coupon-meta">발급일: ${coupon.date || ''}</div>
                            <div class="coupon-actions">${actionBtn}</div>
                        </div>
                    `;
                }).join('');
            }

            return `
                <div class="child-reward-box">
                    <div class="child-reward-title">
                        <span>🎁 아람이의 보물상자 &amp; 보상 플랜 💎</span>
                    </div>
                    <div class="child-reward-subtitle">
                        열심히 달성하면 멋진 선물 티켓이 지급돼요! ✨
                    </div>

                    <!-- 퀘스트 진행 상태 -->
                    <div class="quest-card-grid">
                        <!-- 퀘스트 1: 정시 시작 & 몰입 -->
                        <div class="quest-card">
                            <div class="quest-card-header">
                                <span class="quest-badge">퀘스트 1</span>
                                <span class="quest-tag-highlight">도장 5개 모으면 즉시 발급!</span>
                            </div>
                            <div class="quest-name">🎯 정시 시작 + 집중 몰입 퀘스트</div>
                            <div class="quest-mission-desc">
                                📌 <strong>미션:</strong> 아빠와 약속한 시간에 딱 맞춰 공부를 시작하고, 집중해서 끝내기!
                            </div>
                            
                            <!-- 획득할 선물 안내 배너 -->
                            <div class="quest-reward-banner">
                                <div class="reward-banner-label">🎁 달성 시 받는 선물:</div>
                                <div class="reward-banner-title">${escapeHtml(questConfig.focusRewardTitle)}</div>
                                ${questConfig.focusRewardDesc ? `<div class="reward-banner-desc">${escapeHtml(questConfig.focusRewardDesc)}</div>` : ''}
                            </div>

                            <div class="quest-stamps-row">
                                ${stampSlotsHtml}
                            </div>
                            <div class="quest-progress-txt">
                                도장 <strong>${currentCycleStamps} / 5</strong>개 달성 
                                <span style="color:#e11d48; font-weight:bold;">(앞으로 ${remainingToNextCoupon}개 남음!)</span>
                            </div>
                        </div>

                        <!-- 퀘스트 2: 2주 퍼펙트 출결 -->
                        <div class="quest-card gold-border">
                            <div class="quest-card-header">
                                <span class="quest-badge gold">퀘스트 2 (대기록)</span>
                                <span class="quest-tag-highlight gold">14일 연속 달성!</span>
                            </div>
                            <div class="quest-name">🔥 2주 퍼펙트 출결 퀘스트</div>
                            <div class="quest-mission-desc">
                                📌 <strong>미션:</strong> 14일 동안 지각, 결석, 조퇴 없이 씩씩하게 연속 등교하기!
                            </div>

                            <!-- 획득할 선물 안내 배너 -->
                            <div class="quest-reward-banner gold">
                                <div class="reward-banner-label gold">👑 대기록 달성 선물 (골드 티켓):</div>
                                <div class="reward-banner-title gold">${escapeHtml(questConfig.goldRewardTitle)}</div>
                                ${questConfig.goldRewardDesc ? `<div class="reward-banner-desc">${escapeHtml(questConfig.goldRewardDesc)}</div>` : ''}
                            </div>

                            <div class="quest-bar-bg">
                                <div class="quest-bar-fill" style="width: ${perfectPercent}%;"></div>
                            </div>
                            <div class="quest-progress-txt">
                                연속 <strong>${perfectStreak} / 14일</strong> 달성 (${perfectPercent}%)
                                ${remainingToGold > 0 ? `<span style="color:#d97706; font-weight:bold;">(앞으로 ${remainingToGold}일 더 출석하면 획득!)</span>` : `<span style="color:#059669; font-weight:bold;">(대기록 성공! 골드티켓 지급 완료!)</span>`}
                            </div>
                        </div>
                    </div>

                    <!-- 보관함(인벤토리) -->
                    <div class="inventory-section">
                        <div class="inventory-title">
                            <span>🎟️ 내 보관함 (보상 티켓 인벤토리)</span>
                            <span style="font-size:12px; color:#6366f1; font-weight:normal;">총 ${rewardCoupons.length}개 보유</span>
                        </div>
                        <div class="inventory-list">
                            ${couponsHtml}
                        </div>
                    </div>
                </div>
            `;
        }

        // 아빠 화면 '퀘스트 & 보상 쿠폰 현황 및 선물 설정' HTML
        function renderDadRewardManagerHtml() {
            const focusCount = getFocusStampCount();
            const perfectStreak = getPerfectAttendanceStreak();

            let couponsListHtml = '';
            if (rewardCoupons.length === 0) {
                couponsListHtml = `<div style="text-align:center; color:#94a3b8; font-size:12px; padding:10px;">아직 발급된 보상 쿠폰이 없습니다.</div>`;
            } else {
                couponsListHtml = rewardCoupons.map(c => `
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:10px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="flex:1; margin-right:8px;">
                            <div style="font-weight:bold; font-size:13px; color:#1e293b;">${escapeHtml(c.title)}</div>
                            <div style="font-size:11px; color:#64748b;">${c.date} 발급 | 상태: <strong>${c.status === 'PENDING' ? '지급 대기' : (c.status === 'CLAIMED' ? '수령 완료' : '사용 완료')}</strong></div>
                            ${c.rewardDesc ? `<div style="font-size:11px; color:#94a3b8;">${escapeHtml(c.rewardDesc)}</div>` : ''}
                        </div>
                        <div style="display:flex; gap:6px; flex-shrink:0;">
                            ${c.status === 'PENDING' ? `<button onclick="updateCouponStatus('${c.id}', 'CLAIMED')" style="background:#10b981; color:white; border:none; padding:5px 9px; border-radius:8px; font-size:11px; cursor:pointer; font-weight:bold;">수령확인</button>` : ''}
                            ${c.status === 'CLAIMED' ? `<button onclick="updateCouponStatus('${c.id}', 'USED')" style="background:#6366f1; color:white; border:none; padding:5px 9px; border-radius:8px; font-size:11px; cursor:pointer; font-weight:bold;">사용완료처리</button>` : ''}
                            <button onclick="deleteRewardCoupon('${c.id}')" style="background:#f1f5f9; color:#ef4444; border:1px solid #fecdd3; padding:5px 8px; border-radius:8px; font-size:11px; cursor:pointer;">삭제</button>
                        </div>
                    </div>
                `).join('');
            }

            return `
                <div class="coaching-section" style="background:#fff7ed; border-color:#fed7aa; margin-top:16px;">
                    <div class="coaching-section-title" style="color:#9a3412; display:flex; justify-content:space-between; align-items:center;">
                        <span>🎁 퀘스트 &amp; 보상 선물 설정 및 쿠폰 관리</span>
                    </div>

                    <!-- 1) 퀘스트 선물 설정 (아빠가 직접 선물 내용 변경 가능) -->
                    <div style="background:#ffffff; border:1.5px solid #fed7aa; border-radius:14px; padding:12px; margin-bottom:14px;">
                        <div style="font-size:13px; font-weight:bold; color:#7c2d12; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <span>⚙️ 퀘스트 달성 보상(선물) 변경</span>
                            <span style="font-size:11px; color:#ea580c; font-weight:normal;">원하는 선물로 수정 후 저장하세요</span>
                        </div>
                        
                        <div style="margin-bottom:10px;">
                            <label style="font-size:12px; font-weight:bold; color:#334155; display:block; margin-bottom:4px;">
                                🎯 퀘스트 1 선물 (정시+몰입 5회 도장):
                            </label>
                            <input type="text" id="cfg-focus-title" class="habit-memo-input" style="background:#f8fafc; font-size:13px; padding:8px 10px; margin-bottom:4px;" value="${escapeHtml(questConfig.focusRewardTitle)}" placeholder="예: 🏪 편의점 3,000원 상품권 / 🍨 베스킨 싱글킹">
                            <input type="text" id="cfg-focus-desc" class="habit-memo-input" style="background:#f8fafc; font-size:11px; padding:6px 10px; color:#64748b;" value="${escapeHtml(questConfig.focusRewardDesc)}" placeholder="선물 부가 설명">
                        </div>

                        <div style="margin-bottom:12px;">
                            <label style="font-size:12px; font-weight:bold; color:#334155; display:block; margin-bottom:4px;">
                                🔥 퀘스트 2 선물 (2주 14일 퍼펙트 출결 골드 티켓):
                            </label>
                            <input type="text" id="cfg-gold-title" class="habit-memo-input" style="background:#f8fafc; font-size:13px; padding:8px 10px; margin-bottom:4px;" value="${escapeHtml(questConfig.goldRewardTitle)}" placeholder="예: 🏖️ 1일 학습 자유 휴식권 (골드 티켓) / 🍕 주말 피자 파티">
                            <input type="text" id="cfg-gold-desc" class="habit-memo-input" style="background:#f8fafc; font-size:11px; padding:6px 10px; color:#64748b;" value="${escapeHtml(questConfig.goldRewardDesc)}" placeholder="선물 부가 설명">
                        </div>

                        <div style="display:flex; gap:8px;">
                            <button type="button" onclick="saveQuestSettings()" style="flex:1; background:linear-gradient(135deg, #f97316 0%, #ea580c 100%); color:white; border:none; padding:8px 12px; border-radius:10px; font-size:12px; font-weight:bold; cursor:pointer;">💾 선물 설정 저장하기</button>
                            <button type="button" onclick="giveManualBonusReward()" style="background:#4f46e5; color:white; border:none; padding:8px 12px; border-radius:10px; font-size:12px; font-weight:bold; cursor:pointer;">+ 깜짝 선물 즉시 지급</button>
                        </div>
                    </div>

                    <!-- 2) 현재 퀘스트 진행 통계 -->
                    <div style="font-size:12px; color:#475569; margin-bottom:12px; line-height:1.6; background:#fff7ed; padding:8px 10px; border-radius:10px;">
                        • 현재 정시+몰입 스탬프: <strong>${focusCount}회</strong> (5회마다 위 설정 선물 자동 발급)<br>
                        • 2주 퍼펙트 출결 연속 스트릭: <strong>${perfectStreak} / 14일</strong> (14일 달성 시 골드티켓 자동 발급)
                    </div>

                    <!-- 3) 발급된 쿠폰 목록 및 상태 관리 -->
                    <div>
                        <div style="font-size:13px; font-weight:bold; color:#7c2d12; margin-bottom:8px;">🎟️ 발급된 쿠폰 인벤토리 현황</div>
                        ${couponsListHtml}
                    </div>
                </div>
            `;
        }

        // 선물 설정 저장 함수
        async function saveQuestSettings() {
            const focusTitle = (document.getElementById('cfg-focus-title')?.value || '').trim();
            const focusDesc = (document.getElementById('cfg-focus-desc')?.value || '').trim();
            const goldTitle = (document.getElementById('cfg-gold-title')?.value || '').trim();
            const goldDesc = (document.getElementById('cfg-gold-desc')?.value || '').trim();

            if (!focusTitle || !goldTitle) {
                alert("선물 제목을 입력해주세요!");
                return;
            }

            questConfig = {
                focusRewardTitle: focusTitle,
                focusRewardDesc: focusDesc,
                goldRewardTitle: goldTitle,
                goldRewardDesc: goldDesc
            };

            try {
                await supabaseClient
                    .from('study_words')
                    .upsert({
                        word: 'QUEST_REWARD_SETTINGS',
                        meaning: JSON.stringify(questConfig),
                        subject: 'CHILD_REWARD',
                        category: '설정',
                        example: userNickname || '아빠'
                    }, { onConflict: 'word' });

                alert("💖 퀘스트 보상(선물) 설정이 저장되었습니다! 아람이 화면에도 바로 반영됩니다.");
                renderHabitSection();
            } catch(e) {
                console.error("Save quest settings error:", e);
                alert("선물 설정 저장 실패: " + e.message);
            }
        }

        // 아빠가 깜짝 보너스 선물 즉시 발급
        async function giveManualBonusReward() {
            const title = prompt("아람이에게 줄 깜짝 선물 이름을 입력하세요:", "🎉 아빠의 특별 칭찬 선물 (자유 이용권)");
            if (!title || !title.trim()) return;

            const desc = prompt("선물 설명 또는 칭찬 메시지를 적어주세요:", "오늘 스스로 열심히 노력한 아람이를 위한 깜짝 선물! 💖") || '';

            const couponId = `REWARD_MANUAL_${Date.now()}`;
            const newCoupon = {
                title: title.trim(),
                type: 'MANUAL_BONUS',
                rewardDesc: desc.trim(),
                date: getLocalDateStr(new Date()),
                status: 'PENDING',
                created_at: new Date().toISOString()
            };

            try {
                await supabaseClient
                    .from('study_words')
                    .insert([{
                        word: couponId,
                        meaning: JSON.stringify(newCoupon),
                        subject: 'CHILD_REWARD',
                        category: '아람',
                        example: userNickname || '아빠'
                    }]);

                rewardCoupons.unshift({ id: couponId, ...newCoupon });
                alert(`✨ [${title.trim()}] 깜짝 선물이 아람이 보관함으로 발급되었습니다!`);
                renderHabitSection();
            } catch(e) {
                console.error("Manual reward error:", e);
                alert("선물 발급 실패: " + e.message);
            }
        }

        // 쿠폰 삭제 함수
        async function deleteRewardCoupon(couponId) {
            if (!confirm("이 보상 쿠폰을 삭제하시겠습니까?")) return;

            try {
                await supabaseClient
                    .from('study_words')
                    .delete()
                    .eq('subject', 'CHILD_REWARD')
                    .eq('word', couponId);

                rewardCoupons = rewardCoupons.filter(c => c.id !== couponId);
                renderHabitSection();
                alert("쿠폰이 삭제되었습니다.");
            } catch(e) {
                console.error("Delete coupon error:", e);
                alert("삭제 실패: " + e.message);
            }
        }

        function changeHabitDate(val) {
            if (!val) return;
            selectedHabitDate = val;
            const parts = val.split('-').map(Number);
            habitCalYear = parts[0];
            habitCalMonth = parts[1] - 1;
            habitWeekOffset = getWeekOffsetFromDate(val);
            syncDraftWithSelectedDate();
            renderHabitSection();
            const el = document.getElementById('habit-container');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        function stepHabitDate(offset) {
            const parts = selectedHabitDate.split('-').map(Number);
            const curr = new Date(parts[0], parts[1] - 1, parts[2]);
            curr.setDate(curr.getDate() + offset);
            selectedHabitDate = getLocalDateStr(curr);
            habitCalYear = curr.getFullYear();
            habitCalMonth = curr.getMonth();
            habitWeekOffset = getWeekOffsetFromDate(selectedHabitDate);
            syncDraftWithSelectedDate();
            renderHabitSection();
        }

        function setHabitDateToToday() {
            selectedHabitDate = getLocalDateStr(new Date());
            habitCalYear = new Date().getFullYear();
            habitCalMonth = new Date().getMonth();
            habitWeekOffset = 0;
            syncDraftWithSelectedDate();
            renderHabitSection();
        }

        function setHabitAttendance(val) {
            if (draftAttendance === val) {
                draftAttendance = null;
                draftAttendanceReason = null;
                draftAttendanceReasonText = '';
            } else {
                draftAttendance = val;
                if ((val === 'ABSENT' || val === 'EARLY_LEAVE') && !draftAttendanceReason) {
                    draftAttendanceReason = 'SICK'; // 기본값: 질병/감기(병결)
                }
            }
            renderHabitSection();
        }

        function setAttendanceReason(val) {
            draftAttendanceReason = (draftAttendanceReason === val) ? null : val;
            renderHabitSection();
        }

        function setHabitEveningStudy(val) {
            if (draftEveningStudy === val) {
                draftEveningStudy = null;
            } else {
                draftEveningStudy = val;
                if (val === true && !draftStudyAttitude) {
                    draftStudyAttitude = 'EXCELLENT';
                }
                if (val === false && !draftAbsenceReason) {
                    draftAbsenceReason = 'REST_SICK';
                }
            }
            renderHabitSection();
        }

        function setHabitStudyAttitude(val) {
            draftStudyAttitude = (draftStudyAttitude === val) ? null : val;
            renderHabitSection();
        }

        function toggleFocusOnTime() {
            draftFocusOnTime = !draftFocusOnTime;
            renderHabitSection();
        }

        function toggleFocusDeep() {
            draftFocusDeep = !draftFocusDeep;
            renderHabitSection();
        }

        function setHabitAbsenceReason(val) {
            draftAbsenceReason = (draftAbsenceReason === val) ? null : val;
            renderHabitSection();
        }

        // 과제 추가 / 토글 / 삭제
        function addAssignment() {
            const input = document.getElementById('new-assignment-input');
            const dateInput = document.getElementById('new-assignment-date');
            if (!input || !input.value.trim()) return;

            const text = input.value.trim();
            const dueDate = dateInput ? dateInput.value : '';

            draftAssignments.push({
                id: Date.now(),
                text: text,
                dueDate: dueDate,
                done: false
            });

            renderHabitSection();
        }

        function toggleAssignment(idx) {
            if (draftAssignments[idx]) {
                draftAssignments[idx].done = !draftAssignments[idx].done;
                renderHabitSection();
            }
        }

        function deleteAssignment(idx) {
            draftAssignments.splice(idx, 1);
            renderHabitSection();
        }

        // 약속 추가 / 토글 / 삭제
        function addPromise() {
            const input = document.getElementById('new-promise-input');
            if (!input || !input.value.trim()) return;

            draftPromises.push({
                id: Date.now(),
                text: input.value.trim(),
                done: false
            });

            renderHabitSection();
        }

        function togglePromise(idx) {
            if (draftPromises[idx]) {
                draftPromises[idx].done = !draftPromises[idx].done;
                renderHabitSection();
            }
        }

        function deletePromise(idx) {
            draftPromises.splice(idx, 1);
            renderHabitSection();
        }

        // 아이(아람이) 모드에서 과제/약속 실시간 체크 및 DB 저장
        async function toggleChildAssignment(dateStr, idx) {
            const rec = habitRecordsMap[dateStr];
            if (!rec || !Array.isArray(rec.assignments) || !rec.assignments[idx]) return;

            rec.assignments[idx].done = !rec.assignments[idx].done;
            renderHabitSection();

            try {
                await supabaseClient
                    .from('study_words')
                    .upsert({
                        word: dateStr,
                        meaning: JSON.stringify(rec),
                        subject: 'DAILY_HABIT',
                        category: '아람',
                        example: userNickname || '아람'
                    }, { onConflict: 'word' });
            } catch(e) {
                console.error("Auto save child assignment error:", e);
            }
        }

        async function toggleChildPromise(dateStr, idx) {
            const rec = habitRecordsMap[dateStr];
            if (!rec || !Array.isArray(rec.promises) || !rec.promises[idx]) return;

            rec.promises[idx].done = !rec.promises[idx].done;
            renderHabitSection();

            try {
                await supabaseClient
                    .from('study_words')
                    .upsert({
                        word: dateStr,
                        meaning: JSON.stringify(rec),
                        subject: 'DAILY_HABIT',
                        category: '아람',
                        example: userNickname || '아람'
                    }, { onConflict: 'word' });
            } catch(e) {
                console.error("Auto save child promise error:", e);
            }
        }

        function changeHabitCalMonth(delta) {
            habitCalMonth += delta;
            if (habitCalMonth < 0) {
                habitCalMonth = 11;
                habitCalYear--;
            } else if (habitCalMonth > 11) {
                habitCalMonth = 0;
                habitCalYear++;
            }
            renderHabitSection();
        }

        function toggleDadPreview(val) {
            isDadPreviewMode = val;
            renderHabitSection();
        }

        async function saveHabitRecord() {
            if (isHabitSaving) return;

            if (!draftAttendance && draftEveningStudy === null && !draftMemo.trim() && draftAssignments.length === 0 && draftPromises.length === 0) {
                alert("출결 상태나 공부 여부, 또는 과제나 약속을 하나 이상 입력해주세요! 😊");
                return;
            }

            isHabitSaving = true;
            const saveBtn = document.getElementById('habit-save-btn');
            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.innerText = "저장 중... ⏳";
            }

            const memoVal = (document.getElementById('habit-memo-input')?.value || draftMemo || '').trim();
            const reasonVal = (document.getElementById('habit-reason-text')?.value || draftReasonText || '').trim();
            const attendReasonTextVal = (document.getElementById('attendance-reason-input')?.value || draftAttendanceReasonText || '').trim();

            const detailObj = {
                attendance: draftAttendance,
                attendance_reason: draftAttendanceReason,
                attendance_reason_text: attendReasonTextVal,
                evening_study: draftEveningStudy,
                study_attitude: draftStudyAttitude,
                focus_ontime: !!draftFocusOnTime,
                focus_deep: !!draftFocusDeep,
                absence_reason: draftAbsenceReason,
                reason_text: reasonVal,
                assignments: draftAssignments,
                promises: draftPromises,
                memo: memoVal,
                student: '아람',
                recorded_by: userNickname || '아빠',
                updated_at: new Date().toISOString()
            };

            try {
                // Supabase upsert를 사용하여 중복 키 충돌(unique_word violation)을 원천 방지
                const { data: upsertData, error: upsertErr } = await supabaseClient
                    .from('study_words')
                    .upsert({
                        word: selectedHabitDate,
                        meaning: JSON.stringify(detailObj),
                        subject: 'DAILY_HABIT',
                        category: '아람',
                        example: userNickname || '아빠'
                    }, { onConflict: 'word' })
                    .select();

                if (upsertErr) throw upsertErr;

                const savedId = (upsertData && upsertData[0]?.id) || (habitRecordsMap[selectedHabitDate]?.id);
                habitRecordsMap[selectedHabitDate] = {
                    ...detailObj,
                    id: savedId,
                    rawCreatedAt: new Date().toISOString()
                };

                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#ffc3a0', '#ffafbd', '#84fab0', '#8fd3f4', '#a18cd1']
                });

                alert(`💖 ${selectedHabitDate} 아람이의 출석·공부 기록이 저장되었습니다!`);
                await checkAndGrantRewards();
                renderHabitSection();

            } catch (err) {
                console.error("Save habit record error:", err);
                alert("저장 중 오류가 발생했습니다: " + (err.message || err));
            } finally {
                isHabitSaving = false;
                if (saveBtn) {
                    saveBtn.disabled = false;
                    const hasRecord = !!habitRecordsMap[selectedHabitDate];
                    saveBtn.innerHTML = `💾 ${hasRecord ? '기록 수정하기' : '기록 저장하기'} 💖`;
                }
            }
        }

        async function deleteHabitRecord() {
            if (!confirm(`${selectedHabitDate}의 기록을 삭제하시겠습니까?`)) return;

            try {
                const { error } = await supabaseClient
                    .from('study_words')
                    .delete()
                    .eq('subject', 'DAILY_HABIT')
                    .eq('word', selectedHabitDate);

                if (error) throw error;

                delete habitRecordsMap[selectedHabitDate];
                syncDraftWithSelectedDate();
                renderHabitSection();
                alert(`${selectedHabitDate} 기록이 삭제되었습니다.`);
            } catch(err) {
                console.error("Delete habit record error:", err);
                alert("삭제 실패: " + err.message);
            }
        }

        function showChildDayDetail(dateStr) {
            const rec = habitRecordsMap[dateStr];
            const friendlyDate = formatFriendlyDate(dateStr);
            
            let attendanceText = '기록 없음 (미체크)';
            if (rec && rec.attendance === 'ON_TIME') attendanceText = '☀️ 정상 등교 (지각 안 함 ✨)';
            else if (rec && rec.attendance === 'LATE') attendanceText = '⏰ 지각함';
            else if (rec && rec.attendance === 'HOLIDAY') attendanceText = '🏖️ 주말 / 휴일';

            let studyText = '기록 없음 (미체크)';
            const dayStudyInfo = rec ? getStudyStatusInfo(rec.evening_study) : null;
            if (dayStudyInfo) {
                studyText = dayStudyInfo.modalText;
            }

            let memoHtml = '';
            if (rec && rec.memo) {
                memoHtml = `<div class="child-memo-box" style="margin-top:12px;">💌 아빠의 응원: "${escapeHtml(rec.memo)}" 💖</div>`;
            }

            const dayEvents = getSchedulesForDate(dateStr);
            let eventsModalHtml = '';
            if (dayEvents && dayEvents.length > 0) {
                const items = dayEvents.map(ev => `
                    <div style="background:#ffffff; border:1px solid #c7d2fe; border-radius:10px; padding:8px 10px; margin-top:4px;">
                        <div style="font-weight:bold; color:#3730a3; font-size:13px;">${ev.icon} ${escapeHtml(ev.title)}</div>
                        <div style="font-size:12px; color:#64748b;">기간: ${formatScheduleRange(ev.startDate, ev.endDate)}</div>
                        ${ev.memo ? `<div style="font-size:11px; color:#6366f1; margin-top:2px;">💬 ${escapeHtml(ev.memo)}</div>` : ''}
                    </div>
                `).join('');
                eventsModalHtml = `
                    <div style="margin-top:10px; padding-top:10px; border-top:1px dashed #cbd5e1; text-align:left;">
                        <strong style="color:#4338ca; font-size:13px;">🗓️ 이날의 주요 일정:</strong>
                        ${items}
                    </div>
                `;
            }

            const modalHtml = `
                <div class="child-detail-modal" id="child-day-modal" onclick="if(event.target === this) closeChildDayDetail()">
                    <div class="child-modal-body">
                        <div style="font-size: 32px; margin-bottom: 8px;">📅</div>
                        <div style="font-family:'Jua', sans-serif; font-size:20px; color:#2d3436; margin-bottom:14px;">${friendlyDate}</div>
                        <div style="background:#f8fafc; border-radius:16px; padding:14px; text-align:left; font-size:14px; display:flex; flex-direction:column; gap:8px;">
                            <div><strong>등교 상태:</strong> ${attendanceText}</div>
                            <div><strong>저녁 공부:</strong> ${studyText}</div>
                        </div>
                        ${eventsModalHtml}
                        ${memoHtml}
                        <button onclick="closeChildDayDetail()" style="margin-top:16px; width:100%; background:linear-gradient(135deg, #ff758c 0%, #ff7eb3 100%); color:white; border:none; padding:10px 18px; border-radius:14px; font-weight:bold; font-family:'Jua', sans-serif; cursor:pointer;">확인 💖</button>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        function closeChildDayDetail() {
            const modal = document.getElementById('child-day-modal');
            if (modal) modal.remove();
        }

        initStats()
        loadWords()
