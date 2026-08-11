import { createClient } from '@supabase/supabase-js';

const AUTH_URL = 'https://yqolkvmrfvumpwlxjimp.supabase.co';
const AUTH_KEY = 'sb_publishable_Y3waCN-Y0LA26BC80eUO-g_Njmuq1Hu';

const authClient = createClient(AUTH_URL, AUTH_KEY);

async function test() {
    const { data, error } = await authClient
        .from('users')
        .select('*')
        .limit(1);
        
    if (error) {
        console.error("Error fetching users:", error);
    } else {
        console.log("User record columns:", data && data[0] ? Object.keys(data[0]) : "No records found");
        console.log("Full record:", data && data[0] ? data[0] : "Empty");
    }
}

test();
