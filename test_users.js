const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const html = fs.readFileSync('auth-helper.js', 'utf8');
const urlMatch = html.match(/AUTH_URL\s*=\s*['"]([^'"]+)['"]/);
const keyMatch = html.match(/AUTH_KEY\s*=\s*['"]([^'"]+)['"]/);

if (urlMatch && keyMatch) {
    const supabase = createClient(urlMatch[1], keyMatch[1]);
    supabase.from('users').select('id, name').then(res => {
        console.log(res);
    });
}