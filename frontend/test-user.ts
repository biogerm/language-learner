import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.VITE_SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_SERVICE_API_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

async function main() {
  const { data, error } = await supabase.auth.admin.createUser({
    email: 'test@example.com',
    password: process.env.TEST_USER_PASSWORD || 'test-password',
    email_confirm: true
  });
  if (error) console.error(error);
  else console.log("Created user:", data.user.id);
}
main();
