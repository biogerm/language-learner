process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });
const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.SUPABASE_SERVICE_API_KEY);

async function run() {
  const { count } = await supabase.from('learning_queue').select('*', { count: 'exact', head: true }).eq('user_id', '441eb95c-a800-4c9d-b503-f8d9a7a8f55f');
  console.log("Total learning queue items for user:", count);
}
run().catch(console.error);
