const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.SUPABASE_SERVICE_API_KEY);

async function run() {
  const { data: user, error: userErr } = await supabase.from('users').select('*').limit(1); // Wait, users table might be different. Let's just select fsrs_progress directly.
  
  const { data: fsrs, error } = await supabase.from('fsrs_progress').select('word_id, today_dictation_passed, today_flashcard_passed, updated_at').order('updated_at', { ascending: false }).limit(10);
  
  console.log("Latest FSRS in Supabase:");
  console.log(fsrs);
  
  const { data: lq, error: lqErr } = await supabase.from('learning_queue').select('base_form, updated_at, status').order('updated_at', { ascending: false }).limit(10);
  
  console.log("Latest Learning Queue in Supabase:");
  console.log(lq);
}
run().catch(console.error);
