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
async function requireAuth() {
    const { data: { user }, error } = await authClient.auth.getUser();
    
    if (error || !user) {
        alert('로그인이 필요하거나 세션이 만료되었습니다. 다시 로그인해 주세요.');
        location.href = 'login.html';
        return null;
    }
    
    // DB에서 해당 사용자의 role 정보 조회
    const { data: profile, error: profileError } = await supabaseClient
        .from('users')
        .select('role')
        .eq('id', user.id)
        .single();

    // profile이 없거나, role이 NULL이거나 비어있으면 접근 차단
    // (즉, role에 'broker', 'admin' 등 어떤 값이라도 들어있으면 무조건 허용)
    if (profileError || !profile || !profile.role) {
        alert('전문가 승인이 필요합니다. 관리자 승인 후 이용 가능합니다.');
        await authClient.auth.signOut();
        location.href = 'login.html';
        return null;
    }
    
    // user 객체에 role 정보를 함께 저장해둠 (나중에 권한 분리에 유용함)
    user.role = profile.role;
    window.currentUser = user;
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
