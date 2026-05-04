export const SUPABASE_URL = 'https://yqolkvmrfvumpwlxjimp.supabase.co';
export const SUPABASE_ANON_KEY = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu';

export const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 중앙 통제 스위치 (true로 두면 로그인 없이 모든 페이지 접근 가능)
export const DEMO_MODE = true;

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
