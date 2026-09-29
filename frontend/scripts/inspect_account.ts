import { Client } from 'pg';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });
if (!process.env.SUPABASE_DB_URL) throw new Error('Set SUPABASE_DB_URL in .env.local');


const client = new Client({
  connectionString: process.env.SUPABASE_DB_URL,
});

async function run() {
  await client.connect();
  const uid = '441eb95c-a800-4c9d-b503-f8d9a7a8f55f';
  
  const f = await client.query('SELECT count(*) AS count FROM public.fsrs_progress WHERE user_id = $1', [uid]);
  const c = await client.query('SELECT count(*) AS count FROM public.custom_dictionary WHERE user_id = $1', [uid]);
  const e = await client.query('SELECT count(*) AS count FROM public.excluded_dictionary WHERE user_id = $1', [uid]);
  const l = await client.query('SELECT count(*) AS count FROM public.learning_queue WHERE user_id = $1', [uid]);

<<<<<<< HEAD
  console.log('=== Current Cloud Data for test@example.com ===');
=======
  console.log('=== Current Cloud Data for biogerm@gmail.com ===');
>>>>>>> e8d1b08c0c4465b924ef4ee22117c918709a5460
  console.log('fsrs_progress:', f.rows[0].count);
  console.log('custom_dictionary:', c.rows[0].count);
  console.log('excluded_dictionary:', e.rows[0].count);
  console.log('learning_queue:', l.rows[0].count);

  await client.end();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
