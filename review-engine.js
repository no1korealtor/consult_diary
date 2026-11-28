/**
 * ===================================================================
 * 🧠 Universal Review Engine (통합 오답 기억 및 에빙하우스 간격 복습 엔진)
 * ===================================================================
 * 모든 학습형 퀴즈(상식, 기말고사, 영단어, 향후 추가 퀴즈)에 공통 적용
 * 
 * [망각곡선 간격 복습 주기 (Spaced Repetition Schedule)]
 * - 오답 발생 시: 다음 복습일 = +1일, streak = 0, wrongCount++
 * - 1차 정답: 다음 복습일 = +1일, streak = 1
 * - 2차 연속 정답: 다음 복습일 = +3일, streak = 2
 * - 3차 연속 정답: 다음 복습일 = +7일, streak = 3
 * - 4차 연속 정답: 다음 복습일 = +14일, streak = 4 (숙달 완료 Graduated)
 */

const UniversalReviewManager = (function() {
    const STORAGE_KEY_PREFIX = 'study_universal_review_records_';

    // 간격 일수 테이블
    const INTERVAL_DAYS = [1, 3, 7, 14, 30];

    function getStorageKey(user) {
        const u = user || (typeof userNickname !== 'undefined' ? userNickname : 'default');
        return `${STORAGE_KEY_PREFIX}${u}`;
    }

    function loadRecords(user) {
        try {
            const raw = localStorage.getItem(getStorageKey(user));
            return raw ? JSON.parse(raw) : {};
        } catch (e) {
            console.error('[UniversalReviewManager] loadRecords error:', e);
            return {};
        }
    }

    function saveRecords(records, user) {
        try {
            localStorage.setItem(getStorageKey(user), JSON.stringify(records));
        } catch (e) {
            console.error('[UniversalReviewManager] saveRecords error:', e);
        }
    }

    /**
     * 연속 정답 수(streak)에 따른 다음 복습 간격(일) 계산
     */
    function calculateNextInterval(streak, isCorrect) {
        if (!isCorrect) return 1; // 오답 시 1일 뒤 바로 재복습
        const idx = Math.min(streak, INTERVAL_DAYS.length - 1);
        return INTERVAL_DAYS[idx] || 1;
    }

    /**
     * 풀이 결과 기록 (모든 퀴즈에서 공통 호출)
     * @param {Object} item { id, quizType, subject, unit, category, question, options, answer, explanation, chosen, isCorrect, user }
     */
    function recordAttempt(item) {
        if (!item || !item.id) return null;

        const user = item.user || (typeof userNickname !== 'undefined' ? userNickname : 'default');
        const records = loadRecords(user);
        const now = new Date();
        const prev = records[item.id] || {
            id: item.id,
            quizType: item.quizType || 'COMMON',
            subject: item.subject || '상식',
            unit: item.unit || '',
            category: item.category || '',
            question: item.question || '',
            options: item.options || [],
            answer: item.answer,
            explanation: item.explanation || '',
            wrongCount: 0,
            correctCount: 0,
            streak: 0,
            lastAttemptAt: null,
            nextReviewAt: null,
            isMastered: false,
            history: []
        };

        const isCorrect = !!item.isCorrect;
        let newStreak = isCorrect ? (prev.streak + 1) : 0;
        let wrongCount = prev.wrongCount + (isCorrect ? 0 : 1);
        let correctCount = prev.correctCount + (isCorrect ? 1 : 0);
        let isMastered = newStreak >= 4; // 4회 연속 정답 시 숙달 완료

        const intervalDays = calculateNextInterval(newStreak, isCorrect);
        const nextDate = new Date(now.getTime() + intervalDays * 24 * 60 * 60 * 1000);

        const updated = {
            ...prev,
            quizType: item.quizType || prev.quizType,
            subject: item.subject || prev.subject,
            unit: item.unit || prev.unit,
            category: item.category || prev.category,
            question: item.question || prev.question,
            options: item.options || prev.options,
            answer: (item.answer !== undefined) ? item.answer : prev.answer,
            explanation: item.explanation || prev.explanation,
            lastChosen: item.chosen,
            isCorrect: isCorrect,
            wrongCount: wrongCount,
            correctCount: correctCount,
            streak: newStreak,
            lastAttemptAt: now.toISOString(),
            nextReviewAt: nextDate.toISOString(),
            isMastered: isMastered
        };

        records[item.id] = updated;
        saveRecords(records, user);

        return updated;
    }

    /**
     * 오늘 복습 대상 문제 목록 조회
     * 조건:
     * 1) 오답 이력이 있는 문제 (wrongCount > 0)
     * 2) 다음 복습 일시(nextReviewAt)가 현재 시각 이전이거나 오늘인 문제
     * 3) 아직 숙달되지 않은 문제 (또는 includeMastered = true인 경우)
     */
    function getDueItems(filter = {}) {
        const user = filter.user || (typeof userNickname !== 'undefined' ? userNickname : 'default');
        const records = loadRecords(user);
        const now = new Date();
        const dueList = [];

        Object.values(records).forEach(item => {
            // 오답 경험이 있는 항목만 복습 대상
            if (item.wrongCount <= 0) return;

            // 숙달 여부 필터
            if (item.isMastered && !filter.includeMastered) return;

            // 과목 필터
            if (filter.subject && filter.subject !== '전체' && item.subject !== filter.subject) return;

            // 퀴즈 유형 필터
            if (filter.quizType && filter.quizType !== '전체' && item.quizType !== filter.quizType) return;

            // 복습 예정일 체크 (미설정 상태이거나 현재 시점 이전이면 due)
            if (!item.nextReviewAt) {
                dueList.push(item);
                return;
            }

            const reviewDate = new Date(item.nextReviewAt);
            if (reviewDate <= now) {
                dueList.push(item);
            }
        });

        // 오래된 복습 예정일 순(또는 오답 횟수가 많은 순) 정렬
        return dueList.sort((a, b) => {
            if (b.wrongCount !== a.wrongCount) return b.wrongCount - a.wrongCount;
            return new Date(a.nextReviewAt || 0) - new Date(b.nextReviewAt || 0);
        });
    }

    /**
     * 복습 현황 요약 통계
     */
    function getReviewSummary(user) {
        const records = loadRecords(user);
        let totalTracked = 0;
        let totalWrongItems = 0;
        let dueCount = 0;
        let masteredCount = 0;
        const subjectStats = {};
        const now = new Date();

        Object.values(records).forEach(item => {
            totalTracked++;
            if (item.wrongCount > 0) totalWrongItems++;
            if (item.isMastered) masteredCount++;

            const subj = item.subject || '기타';
            if (!subjectStats[subj]) subjectStats[subj] = { total: 0, due: 0, wrong: 0 };
            subjectStats[subj].total++;
            if (item.wrongCount > 0) subjectStats[subj].wrong++;

            if (item.wrongCount > 0 && !item.isMastered) {
                if (!item.nextReviewAt || new Date(item.nextReviewAt) <= now) {
                    dueCount++;
                    subjectStats[subj].due++;
                }
            }
        });

        return {
            totalTracked,
            totalWrongItems,
            dueCount,
            masteredCount,
            subjectStats
        };
    }

    return {
        recordAttempt,
        getDueItems,
        getReviewSummary,
        calculateNextInterval,
        loadRecords,
        saveRecords
    };
})();

// Node.js 환경(TDD 테스트 러너)과 브라우저 전역 환경 호환
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UniversalReviewManager;
}
