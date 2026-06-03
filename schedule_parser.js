// schedule_parser.js
// ?쇱젙 愿??怨꾩궛 諛??뚯떛 濡쒖쭅??紐⑥븘?먮뒗 ?쒖닔 ?⑥닔 紐⑤뱢 (TDD ?곸슜 ???

/**
 * 紐⑺몴 ?좎쭨(dateString)? ?ㅻ뒛 ?좎쭨(today)瑜?鍮꾧탳?섏뿬 D-Day瑜?諛섑솚?⑸땲??
 * @param {string} dateString - "YYYY-MM-DD" ?뺥깭??紐⑺몴 ?좎쭨
 * @param {Date} today - 湲곗????섎뒗 ?ㅻ뒛 ?좎쭨 (湲곕낯媛? ?꾩옱 ?쒓컙)
 * @returns {string} "D-5", "D-Day", "D+3" ?깆쓽 寃곌낵 臾몄옄?? */
function getDDay(dateString, today = new Date()) {
    if (!dateString) return '';
    
    const targetDate = new Date(dateString);
    targetDate.setHours(0, 0, 0, 0);
    
    // today ?뚮씪誘명꽣瑜?洹몃?濡??섏젙?섎㈃ ?먮낯 媛앹껜媛 蹂寃쎈릺誘濡?蹂듭궗?댁꽌 ?ъ슜
    const currentDate = new Date(today);
    currentDate.setHours(0, 0, 0, 0);
    
    const diffTime = targetDate - currentDate;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays > 0) return `D-${diffDays}`;
    if (diffDays === 0) return `D-Day`;
    return `D+${Math.abs(diffDays)}`;
}

// 釉뚮씪?곗? 諛?Node.js ?섍꼍 紐⑤몢?먯꽌 ?ъ슜?????덈룄濡??대낫?닿린
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { getDDay, parseScheduleMemo };
}

/**
 * ?쇱젙 硫붾え ?띿뒪??rawMemo)瑜?遺꾩꽍?섏뿬 媛곸쥌 ?쒓렇瑜?異붿텧?섍퀬,
 * ?쒓렇媛 ?쒓굅???쒖닔??硫붾え ?띿뒪?몄? 異붿텧???곗씠?곕? 媛앹껜濡?諛섑솚?⑸땲??
 * @param {string} rawMemo - ?먮낯 硫붾え ?띿뒪?? * @param {string} [dbScheduleTime] - DB????λ맂 schedule_time (?좏깮)
 * @returns {object} ?뚯떛???쇱젙 ?곗씠??媛앹껜
 */
function parseScheduleMemo(rawMemo, dbScheduleTime = null, currentUserId = null) {
    if (!rawMemo) rawMemo = "";
    
    let isDone = false;
    if (rawMemo.includes("[DONE]")) {
        isDone = true;
        rawMemo = rawMemo.replace(/\[DONE\]/g, "");
    }
    
    if (currentUserId) {
        const personalDoneTag = `[DONE:${currentUserId}]`;
        if (rawMemo.includes(personalDoneTag)) {
            isDone = true;
        }
    }
    // Always strip all personal done tags from the clean memo so they don't show up in the UI
    rawMemo = rawMemo.replace(/\[DONE:[a-zA-Z0-9-]+\]/g, "");

    let settledDate = null;
    if (rawMemo.includes("[SETTLED_DATE]")) {
        const m = rawMemo.match(/\[SETTLED_DATE\](.*?)\[\/SETTLED_DATE\]/);
        if (m) { settledDate = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }

    let isContractCanceled = false;
    if (rawMemo.includes("계약해제")) {
        isContractCanceled = true;
    }

    let isPrivate = false;
    if (rawMemo.includes("[PRIVATE]")) {
        isPrivate = true;
        rawMemo = rawMemo.replace(/\[PRIVATE\]/g, "");
    }

    let isProposal = false;
    if (rawMemo.includes("[PROPOSAL]")) {
        isProposal = true;
        rawMemo = rawMemo.replace(/\[PROPOSAL\]/g, "");
    }

    let isPendingAdmin = false;
    if (rawMemo.includes("[PENDING_ADMIN]")) {
        isPendingAdmin = true;
        rawMemo = rawMemo.replace(/\[PENDING_ADMIN\]/g, "");
    }

    let cancelReason = "";
    if (rawMemo.includes("[CANCELED_REASON]")) {
        const m = rawMemo.match(/\[CANCELED_REASON\](.*?)\[\/CANCELED_REASON\]/);
        if (m) {
            cancelReason = m[1];
            rawMemo = rawMemo.replace(m[0], "");
        }
    }

    let isCanceled = false;
    if (rawMemo.includes("[CANCELED]") || cancelReason !== "") {
        isCanceled = true;
        rawMemo = rawMemo.replace(/\[CANCELED\]/g, "");
    }

    if (rawMemo.includes("[HIDDEN:")) {
        rawMemo = rawMemo.replace(/\[HIDDEN:[^\]]+\]/g, "");
    }

    let linkUrl = null, linkName = "愿??留곹겕";
    if (rawMemo.includes("[URL]")) {
        const m = rawMemo.match(/\[URL\](.*?)\[\/URL\]/);
        if (m) { 
            let urlData = m[1];
            if (urlData.includes("|")) {
                const parts = urlData.split("|");
                linkUrl = parts[0];
                linkName = parts[1];
            } else {
                linkUrl = urlData;
            }
            rawMemo = rawMemo.replace(m[0], ""); 
        }
    }

    let startDate = null;
    if (rawMemo.includes("[START]")) {
        const m = rawMemo.match(/\[START\](.*?)\[\/START\]/);
        if (m) { startDate = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }

    let time = dbScheduleTime ? dbScheduleTime.substring(0, 5) : null;
    if (!time && rawMemo.includes("[TIME]")) {
        const m = rawMemo.match(/\[TIME\](.*?)\[\/TIME\]/);
        if (m) { time = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    } else if (rawMemo.includes("[TIME]")) {
        const m = rawMemo.match(/\[TIME\](.*?)\[\/TIME\]/);
        if (m) { rawMemo = rawMemo.replace(m[0], ""); }
    }

    let location = null;
    if (rawMemo.includes("[LOC]")) {
        const m = rawMemo.match(/\[LOC\](.*?)\[\/LOC\]/);
        if (m) { location = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }

    let attendance = null;
    if (rawMemo.includes("[ATT]")) {
        const m = rawMemo.match(/\[ATT\](.*?)\[\/ATT\]/);
        if (m) { attendance = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }

    let deadline = null;
    if (rawMemo.includes("[DEADLINE]")) {
        const m = rawMemo.match(/\[DEADLINE\](.*?)\[\/DEADLINE\]/);
        if (m) { deadline = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }

    let minAttendance = null;
    if (rawMemo.includes("[MIN_ATT]")) {
        const m = rawMemo.match(/\[MIN_ATT\](.*?)\[\/MIN_ATT\]/);
        if (m) { minAttendance = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }

    let taskJangumTime = null;
    let taskUtil = false;
    if (rawMemo.includes("[TASK:잔금시간]")) {
        const m = rawMemo.match(/\[TASK:잔금시간\]\s*(.*?)(?=\n|$)/);
        if (m) { taskJangumTime = m[1]; rawMemo = rawMemo.replace(m[0], ""); }
    }
    if (rawMemo.includes("[TASK:공과금정산]")) {
        const m = rawMemo.match(/\[TASK:공과금정산\]\s*(.*?)(?=\n|$)/);
        if (m) { taskUtil = true; rawMemo = rawMemo.replace(m[0], ""); }
    }

    return {
        cleanMemo: rawMemo.trim(),
        isDone,
        settledDate,
        isContractCanceled,
        isPrivate,
        isProposal,
        isPendingAdmin,
        isCanceled,
        cancelReason,
        linkUrl,
        linkName,
        startDate,
        time,
        location,
        attendance,
        deadline,
        minAttendance,
        taskJangumTime,
        taskUtil
    };
}


