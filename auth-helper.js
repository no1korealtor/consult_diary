// auth-helper.js
const AUTH_URL = 'https://yqolkvmrfvumpwlxjimp.supabase.co';
const AUTH_KEY = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu';
const DB_URL = 'https://clzrbyplzjdrrscctcsl.supabase.co';
const DB_KEY = 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k';

if (typeof window.supabase === 'undefined') {
    console.error('Supabase 라이브러리를 먼저 로드해야 합니다.');
}

// 인증용 클라이언트
const authClient = window.supabase.createClient(AUTH_URL, AUTH_KEY);
// 데이터베이스용 클라이언트
const supabaseClient = window.supabase.createClient(DB_URL, DB_KEY);

window.currentUser = null;

/**
 * 로그인 상태를 확인하고, 없으면 로그인 페이지로 이동합니다.
 * @returns {Promise<Object|null>} user 객체 반환
 */
async function requireAuth(bypassProfileCheck = false) {
    const { data: { user }, error } = await authClient.auth.getUser();
    
    if (error || !user) {
        alert('로그인이 필요하거나 세션이 만료되었습니다. 다시 로그인해 주세요.');
        location.href = 'login.html';
        return null;
    }
    
    // DB에서 해당 사용자의 role, 주소, 전화번호 정보 조회 (users 테이블은 authClient 프로젝트에 존재)
    const { data: profile, error: profileError } = await authClient
        .from('users')
        .select('role, office_address, phone, name')
        .eq('id', user.id)
        .single();

    // profile이 없거나, role이 NULL이거나 비어있으면 접근 차단
    if (profileError || !profile || !profile.role) {
        let debugMsg = "알 수 없는 오류";
        if (profileError) debugMsg = "DB 에러: " + JSON.stringify(profileError);
        else if (!profile) debugMsg = "users 테이블에 해당 id(" + user.id + ")의 정보가 없습니다.";
        else if (!profile.role) debugMsg = "role 값이 비어있습니다.";
        
        alert('가입승인 대기 중입니다. (010-9128-0586 조항준)');
        await authClient.auth.signOut();
        setTimeout(() => {
            location.href = 'login.html';
        }, 3500);
        return null;
    }

    // 데이터 DB(supabaseClient)에서 office_id를 추가로 가져옵니다.
    const { data: dataProfile } = await supabaseClient
        .from('users')
        .select('office_id')
        .eq('id', user.id)
        .single();

    // user 객체에 추가 정보를 함께 저장해둠 (나중에 권한 분리에 유용함)
    user.role = profile.role;
    user.office_address = profile.office_address;
    user.phone = profile.phone;
    user.name = profile.name || user.email;
    user.office_id = (dataProfile && dataProfile.office_id) ? dataProfile.office_id : user.id;
    window.currentUser = user;
    
    // 관리자인 경우 장부, 연락처 탭 표시
    if (user.role === 'admin') {
        const navMarket = document.getElementById('navMarket');
        if (navMarket) navMarket.style.display = 'flex';
        const navContacts = document.getElementById('navContacts');
        if (navContacts) navContacts.style.display = 'flex';

        setTimeout(() => {
            const nav = document.querySelector('.bottom-nav');
            if (nav && !document.getElementById('adminNavBtn')) {
                const adminBtn = document.createElement('a');
                adminBtn.href = 'admin-center.html';
                adminBtn.className = 'nav-item' + (location.pathname.includes('admin-') ? ' active' : '');
                adminBtn.id = 'adminNavBtn';
                adminBtn.innerHTML = '<span class="nav-icon">⚙️</span><span>관리자</span>';
                nav.appendChild(adminBtn);
            }
        }, 100);
    }
    
    return user;
}

/**
 * 로그아웃 수행
 */
async function logout() {
    await authClient.auth.signOut();
    location.href = 'login.html';
}

// 전역 변수로 할당 (기존 코드와의 호환성을 위해)
window.authClient = authClient;
window.supabaseClient = supabaseClient;

// ==========================================
// 글로벌 UI 헬퍼 (토스트 알림 및 로딩 스피너)
// ==========================================
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .toast-container {
            position: fixed;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
            width: 100%;
            align-items: center;
        }
        .toast-msg {
            background: rgba(30, 41, 59, 0.95);
            color: #f8fafc;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            max-width: 90vw;
            text-align: center;
            backdrop-filter: blur(4px);
            word-break: keep-all;
        }
        .toast-msg.show {
            opacity: 1;
            transform: translateY(0);
        }
        .toast-msg.error { background: rgba(239, 68, 68, 0.95); }
        .toast-msg.success { background: rgba(16, 185, 129, 0.95); }
        
        .spinner-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(2px);
            z-index: 9998;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            opacity: 0;
            visibility: hidden;
            transition: all 0.2s;
        }
        .spinner-overlay.show {
            opacity: 1;
            visibility: visible;
        }
        .spinner-circle {
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    `;
    document.head.appendChild(style);

    window.addEventListener('DOMContentLoaded', () => {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);

        window.showToast = function(message, type = 'info') {
            const toast = document.createElement('div');
            
            if (type === 'info') {
                if (String(message).includes('실패') || String(message).includes('에러') || String(message).includes('오류')) {
                    type = 'error';
                } else if (String(message).includes('성공') || String(message).includes('완료') || String(message).includes('되었습니다')) {
                    type = 'success';
                }
            }
            
            toast.className = `toast-msg ${type}`;
            toast.innerHTML = String(message).replace(/\n/g, '<br>');
            toastContainer.appendChild(toast);
            
            setTimeout(() => toast.classList.add('show'), 10);
            
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        };

        window.alert = function(message) {
            if (window.showToast) {
                window.showToast(message);
            } else {
                console.log("Alert intercepted:", message);
            }
        };

        const spinnerOverlay = document.createElement('div');
        spinnerOverlay.className = 'spinner-overlay';
        spinnerOverlay.innerHTML = '<div class="spinner-circle"></div>';
        document.body.appendChild(spinnerOverlay);

        window.showLoading = function() {
            spinnerOverlay.classList.add('show');
        };
        window.hideLoading = function() {
            spinnerOverlay.classList.remove('show');
        };

        const originalFetch = window.fetch;
        let activeRequests = 0;

        window.fetch = async function(...args) {
            activeRequests++;
            const loadingTimeout = setTimeout(() => {
                if (activeRequests > 0) window.showLoading();
            }, 100);
            
            try {
                return await originalFetch.apply(this, args);
            } finally {
                activeRequests--;
                if (activeRequests <= 0) {
                    activeRequests = 0;
                    clearTimeout(loadingTimeout);
                    window.hideLoading();
                }
            }
        };
    });
})();
