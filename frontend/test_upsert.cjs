process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });
const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_PUBLISHABLE_KEY);

async function run() {
  const { data: { user }, error: authErr } = await supabase.auth.signInWithPassword({
    email: process.env.TEST_USER_EMAIL,
    password: process.env.TEST_USER_PASSWORD 
  });
  if (!user) return console.log("Login failed");
  
  const payload = {
    user_id: user.id,
    word_id: 'test_word',
    course_id: 'sfid',
    state: 0,
    due: new Date().toISOString(),
    stability: 0, difficulty: 0, elapsed_days: 0, scheduled_days: 0, reps: 0, lapses: 0, max_wrongs: 0, max_time: 0, reveal_count: 0
  };
  const { error } = await supabase.from('fsrs_progress').upsert(payload, { onConflict: 'user_id, course_id, word_id' });
  console.log("FSRS Upsert as User:", error ? error.message : "Success");
  
  const lq = { user_id: user.id, course_id: 'sfid', article_id: '1', base_form: 'x', status: 'learning' };
  const { error: e2 } = await supabase.from('learning_queue').upsert(lq, { onConflict: 'user_id, course_id, article_id, base_form' });
  console.log("LQ Upsert as User:", e2 ? e2.message : "Success");
}
run().catch(console.error);
