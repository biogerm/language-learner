import { Client } from 'pg';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: 'postgresql://postgres.qtyzqyzjqscdbjcfqwuz:' + process.env.SUPABASE_DB_PWD + '@aws-1-eu-west-3.pooler.supabase.com:5432/postgres'
});

async function rollback() {
  await client.connect();
  const userRes = await client.query("SELECT id FROM auth.users WHERE email = 'test@example.com'");
  if (userRes.rows.length > 0) {
    const uid = userRes.rows[0].id;
    console.log('Rolling back all data for test user:', uid);
    await client.query('DELETE FROM fsrs_progress WHERE user_id = $1', [uid]);
    await client.query('DELETE FROM custom_dictionary WHERE user_id = $1', [uid]);
    await client.query('DELETE FROM learning_queue WHERE user_id = $1', [uid]);
    console.log('✅ Successfully rolled back all migrated data in Supabase (all tables empty).');
  }
  await client.end();
}
rollback().catch(console.error);
