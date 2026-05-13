export const SUPABASE_URL = 'https://yqolkvmrfvumpwlxjimp.supabase.co';
export const SUPABASE_ANON_KEY = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu';

export const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// 모든 환경(로컬 및 Vercel)에서 정상 데이터베이스를 사용하도록 데모 모드를 해제합니다.
export let DEMO_MODE = false;

export async function requireAuth() {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
        DEMO_MODE = false;
        return true;
    }
    if (DEMO_MODE) return false;
    
    window.location.href = 'login.html';
    return false;
}

// Auth state listener
supabase.auth.onAuthStateChange((event, session) => {
    if (DEMO_MODE) return;
    if (event === 'SIGNED_OUT') {
        window.location.href = 'login.html';
    }
});
