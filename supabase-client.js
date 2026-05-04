export const SUPABASE_URL = 'https://yqolkvmrfvumpwlxjimp.supabase.co';
export const SUPABASE_ANON_KEY = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu';

export const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 현재 주소가 로컬환경(개발 중)인지 확인합니다.
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:';

// 로컬(개발 환경)에서는 정상 작동(false), 외부 배포 환경(Vercel)에서는 데모 모드(true)
export const DEMO_MODE = isLocal ? false : true;

export async function requireAuth() {
    if (DEMO_MODE) return;
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
        window.location.href = 'index.html';
    }
}

// Auth state listener
supabase.auth.onAuthStateChange((event, session) => {
    if (DEMO_MODE) return;
    if (event === 'SIGNED_OUT') {
        window.location.href = 'index.html';
    }
});
