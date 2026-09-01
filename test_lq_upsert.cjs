const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: 'frontend/.env.local' });

const supabase = createClient(process.env.VITE_SUPABASE_URL, process.env.VITE_SUPABASE_ANON_KEY);

async function run() {
  const { data: { user }, error: authErr } = await supabase.auth.signInWithPassword({
    email: 'qin.an@hm.com',
    password: 'password123' // I don't know the password
  });
}
