// ui-helper.js
(function() {
    // 1. CSS 동적 삽입
    const style = document.createElement('style');
    style.textContent = `
        /* Toast Notification */
        .toast-container {
            position: fixed;
            bottom: 80px; /* 네비게이션 바 위쪽에 뜨도록 여백 확보 */
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
        
        /* Full Screen Spinner */
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

    // 2. DOM 요소 생성 (DOMContentLoaded 시점에 붙이기 위해 대기)
    window.addEventListener('DOMContentLoaded', () => {
        const toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);

        window.showToast = function(message, type = 'info') {
            const toast = document.createElement('div');
            
            // 에러나 성공 키워드를 분석해서 자동으로 색상 지정
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

        // 기본 alert() 함수를 가로채서 토스트 알림으로 둔갑시킵니다.
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

        // 모든 fetch 요청(Supabase 통신 포함)에 자동으로 로딩 스피너 적용
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

window.formatPhone = function(phone, ownerId) { if (!phone) return ''; if (window.currentUser && (window.currentUser.role === 'admin' || window.currentUser.id === ownerId)) return phone; if (phone.includes('-')) return phone.replace(/(?<=\d{2,3}-)\d{3,4}(?=-\d{4})/, '****'); if (phone.length >= 10) return phone.substring(0,3) + '-****-' + phone.substring(phone.length-4); return '***-****-****'; }; 
window.formatAddress = function(address, ownerId) { if (!address) return ''; if (window.currentUser && (window.currentUser.role === 'admin' || window.currentUser.id === ownerId)) return address; return address.replace(/\d+동|\d+호/g, '***'); };
