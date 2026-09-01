process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });
const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.SUPABASE_SERVICE_API_KEY);

async function run() {
  const { data: lqs } = await supabase.from('learning_queue').select('*').eq('user_id', '441eb95c-a800-4c9d-b503-f8d9a7a8f55f');
  
  if (lqs) {
    const counts = {};
    for (const l of lqs) {
      const key = l.article_id + "_" + l.base_form;
      counts[key] = (counts[key] || 0) + 1;
    }
    const dupes = Object.entries(counts).filter(([k, c]) => c > 1);
    console.log("Duplicates in Supabase:", dupes);
  }
}
run().catch(console.error);
