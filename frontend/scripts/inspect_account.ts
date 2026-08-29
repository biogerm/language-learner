import { Client } from 'pg';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`
});

async function run() {
  await client.connect();
  const uid = '441eb95c-a800-4c9d-b503-f8d9a7a8f55f';
  
  const f = await client.query('SELECT count(*) AS count FROM public.fsrs_progress WHERE user_id = $1', [uid]);
  const c = await client.query('SELECT count(*) AS count FROM public.custom_dictionary WHERE user_id = $1', [uid]);
  const e = await client.query('SELECT count(*) AS count FROM public.excluded_dictionary WHERE user_id = $1', [uid]);
  const l = await client.query('SELECT count(*) AS count FROM public.learning_queue WHERE user_id = $1', [uid]);

  console.log('=== Current Cloud Data for biogerm@gmail.com ===');
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
