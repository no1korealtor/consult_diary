// schedule_parser.js
// 일정 관련 계산 및 파싱 로직을 모아두는 순수 함수 모듈 (TDD 적용 대상)

/**
 * 목표 날짜(dateString)와 오늘 날짜(today)를 비교하여 D-Day를 반환합니다.
 * @param {string} dateString - "YYYY-MM-DD" 형태의 목표 날짜
 * @param {Date} today - 기준이 되는 오늘 날짜 (기본값: 현재 시간)
 * @returns {string} "D-5", "D-Day", "D+3" 등의 결과 문자열
 */
function getDDay(dateString, today = new Date()) {
    if (!dateString) return '';
    
    const targetDate = new Date(dateString);
    targetDate.setHours(0, 0, 0, 0);
    
    // today 파라미터를 그대로 수정하면 원본 객체가 변경되므로 복사해서 사용
    const currentDate = new Date(today);
    currentDate.setHours(0, 0, 0, 0);
    
    const diffTime = targetDate - currentDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays > 0) return `D-${diffDays}`;
    if (diffDays === 0) return `D-Day`;
    return `D+${Math.abs(diffDays)}`;
}

// 브라우저 및 Node.js 환경 모두에서 사용할 수 있도록 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { getDDay };
}
