const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://qtyzqyzjqscdbjcfqwuz.supabase.co';
const supabaseKey = 'sb_publishable_zDiYzPQeKk7gS7NS45DFrw_Fg4ouuWO';

const supabase = createClient(supabaseUrl, supabaseKey);

async function check() {
  const { data, error } = await supabase.from('courses').select('*');
  if (error) console.error(error);
  else {
    data.forEach(d => {
      console.log(`Course: ${d.id}`);
      console.log(`  r2_json_url: ${d.r2_json_url}`);
    });
  }
}
check();
