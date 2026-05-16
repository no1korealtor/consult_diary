const DB_URL = 'https://clzrbyplzjdrrscctcsl.supabase.co';
const DB_KEY = 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k';

async function fetchDeals() {
    const response = await fetch(`${DB_URL}/rest/v1/deals?select=id,contract_type,memo,building_id,created_at&order=created_at.desc&limit=15`, {
        headers: {
            'apikey': DB_KEY,
            'Authorization': `Bearer ${DB_KEY}`
        }
    });
    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
}
fetchDeals();