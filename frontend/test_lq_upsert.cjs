process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });
const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_PUBLISHABLE_KEY);

async function run() {
  const { data: { user } } = await supabase.auth.signInWithPassword({
    email: process.env.TEST_USER_EMAIL,
    password: process.env.TEST_USER_PASSWORD 
  });
  
  // 1. Insert a row
  const payload1 = {
    user_id: user.id,
    course_id: 'sfid',
    article_id: 'art_99',
    base_form: 'test_word',
    dictation_passed: false,
    status: 'learning'
  };
  await supabase.from('learning_queue').upsert(payload1, { onConflict: 'user_id, course_id, article_id, base_form' });
  
  // 2. Fetch it
  let { data: d1 } = await supabase.from('learning_queue').select('*').eq('article_id', 'art_99');
  console.log("After insert:", d1[0].dictation_passed);
  
  // 3. Upsert dictation_passed = true
  const payload2 = {
    user_id: user.id,
    course_id: 'sfid',
    article_id: 'art_99',
    base_form: 'test_word',
    dictation_passed: true,
    status: 'learning'
  };
  await supabase.from('learning_queue').upsert(payload2, { onConflict: 'user_id, course_id, article_id, base_form' });
  
  // 4. Fetch it
  let { data: d2 } = await supabase.from('learning_queue').select('*').eq('article_id', 'art_99');
  console.log("After update:", d2[0].dictation_passed);
  
  // 5. Cleanup
  await supabase.from('learning_queue').delete().eq('article_id', 'art_99');
}
run().catch(console.error);
