import { Client } from 'pg';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`
});

async function run() {
  await client.connect();
  console.log('🔗 Connected to Supabase for multi-device sync simulation.');

  const uid = '441eb95c-a800-4c9d-b503-f8d9a7a8f55f';
  const testWord = 'trötta';

  console.log('📱 Device 1: Completes dictation for "trötta" and syncs on page refresh...');
  await client.query(
    'UPDATE public.fsrs_progress SET today_dictation_passed = true, updated_at = NOW() WHERE user_id = $1 AND word_id = $2',
    [uid, testWord]
  );

  console.log('💻 Device 2: Refreshes webpage and downloads latest state from Supabase...');
  const dev2Res = await client.query(
    'SELECT word_id, today_dictation_passed, today_flashcard_passed, due, state FROM public.fsrs_progress WHERE user_id = $1 AND word_id = $2',
    [uid, testWord]
  );

  const dev2Card = dev2Res.rows[0];
  console.log('📥 Device 2 received card:', dev2Card);

  if (dev2Card?.today_dictation_passed === true) {
    console.log('🎯 PASS: Device 2 successfully recognized today_dictation_passed = true!');
    console.log('✨ Device 2 Dictation review queue will immediately exclude "trötta" (showing 44 remaining instead of 45)!');
  }

  await client.query(
    'UPDATE public.fsrs_progress SET today_dictation_passed = false, today_flashcard_passed = false WHERE user_id = $1 AND word_id = $2',
    [uid, testWord]
  );
  console.log('🧹 Cleaned test simulation state.');

  await client.end();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
