import { Client } from 'pg';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`
});

async function run() {
  await client.connect();
  const uid = '441eb95c-a800-4c9d-b503-f8d9a7a8f55f';

  const userRes = await client.query('SELECT id, email, raw_app_meta_data, raw_user_meta_data FROM auth.users WHERE id = $1', [uid]);
  console.log('=== auth.users Metadata ===');
  console.log('raw_app_meta_data:', JSON.stringify(userRes.rows[0]?.raw_app_meta_data, null, 2));
  console.log('raw_user_meta_data:', JSON.stringify(userRes.rows[0]?.raw_user_meta_data, null, 2));

  const identRes = await client.query('SELECT id, user_id, provider, identity_data, created_at, last_sign_in_at FROM auth.identities WHERE user_id = $1', [uid]);
  console.log('\n=== auth.identities Provider Info ===');
  console.log(JSON.stringify(identRes.rows, null, 2));

  await client.end();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
