const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const html = fs.readFileSync('auth-helper.js', 'utf8');
const urlMatch = html.match(/SUPABASE_URL\s*=\s*['"]([^'"]+)['"]/);
const keyMatch = html.match(/SUPABASE_ANON_KEY\s*=\s*['"]([^'"]+)['"]/);

if (urlMatch && keyMatch) {
    const supabase = createClient(urlMatch[1], keyMatch[1]);
    supabase.from('user_tip_status').select('*').limit(1).then(console.log);
}