const { createClient } = require('@supabase/supabase-js');

const supabase = createClient('https://clzrbyplzjdrrscctcsl.supabase.co', 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k');

async function check() {
    const { data, error } = await supabase
        .from('schedules')
        .select('*')
        .order('schedule_date', { ascending: false });
    
    if (error) {
        console.error(error);
        return;
    }
    
    console.log(`Total schedules: ${data.length}`);
    data.forEach(s => {
        if (s.memo && s.memo.includes('종합소득세')) {
            console.log('Found 1:', s);
        } else if (s.schedule_type && s.schedule_type.includes('종합소득세')) {
            console.log('Found 2:', s);
        } else if (s.schedule_date && s.schedule_date.startsWith('2026-06-01')) {
            console.log('June 1 schedule:', s);
        }
    });
}
check();
