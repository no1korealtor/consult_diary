const { createClient } = require('@supabase/supabase-js');

const AUTH_URL = 'https://yqolkvmrfvumpwlxjimp.supabase.co';
const AUTH_KEY = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu';

const authClient = createClient(AUTH_URL, AUTH_KEY);

async function test() {
    const { data, error } = await authClient
        .from('users')
        .select(`
            id, name, phone, office_address, role,
            user_groups ( group_id, status, group_role, groups ( name ) )
        `)
        .order('name');
        
    console.log("Error:", error);
    console.log("Data count:", data ? data.length : 0);
}

test();