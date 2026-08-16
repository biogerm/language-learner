const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const env = fs.readFileSync('.env.local', 'utf8');
const urlMatch = env.match(/VITE_SUPABASE_URL=(.*)/);
const keyMatch = env.match(/VITE_SUPABASE_PUBLISHABLE_KEY=(.*)/);
const supabase = createClient(urlMatch[1].trim(), keyMatch[1].trim());
(async () => {
  const { data, error } = await supabase.auth.signUp({
    email: 'test@test.com',
    password: 'password'
  });
  console.log('Signup result:', error ? error.message : 'Success');
})();
