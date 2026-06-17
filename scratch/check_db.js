const { createClient } = require('@supabase/supabase-js');

const DB_URL = 'https://clzrbyplzjdrrscctcsl.supabase.co';
const DB_KEY = 'sb_publishable_SqGXeBJseIB_4hjHB6GZ8g_rF_tv11k';
const supabase = createClient(DB_URL, DB_KEY);

async function check() {
    const { data: users, error: err1 } = await supabase.from('users').select('*').like('name', '%조항준%');
    console.log("Users:", users);
    
    if (users && users.length > 0) {
        const myId = users[0].id;
        const { data: schedules, error: err2 } = await supabase
            .from('schedules')
            .select('id, schedule_date, memo, schedule_type, created_at')
            .eq('user_id', myId)
            .like('memo', '오늘의 업무%')
            .order('created_at', { ascending: false })
            .limit(10);
            
        console.log("Schedules:");
        for (const s of schedules) {
            console.log(s.id, s.schedule_date, s.created_at);
            const { data: tasks } = await supabase.from('schedule_tasks').select('*').eq('schedule_id', s.id);
            console.log("  Tasks:", tasks);
        }
    }
}
check();
