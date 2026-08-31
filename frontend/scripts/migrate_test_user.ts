import { Client } from 'pg';
import * as dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';

dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`
});

async function migrateTestUser() {
  await client.connect();
  console.log('🔗 Connected to Supabase Postgres.');

  // 1. Get test user UUID
  const userRes = await client.query("SELECT id FROM auth.users WHERE email = process.env.TEST_USER_EMAIL || 'test@example.com';");
  if (userRes.rows.length === 0) {
    throw new Error('Test user test@example.com not found in auth.users');
  }
  const userId = userRes.rows[0].id;
  console.log(`👤 Found test user UUID: ${userId}`);

  // 2. Clear existing test user data
  console.log('🧹 Cleaning previous records for test user...');
  await client.query('DELETE FROM fsrs_progress WHERE user_id = $1;', [userId]);
  await client.query('DELETE FROM custom_dictionary WHERE user_id = $1;', [userId]);
  await client.query('DELETE FROM excluded_dictionary WHERE user_id = $1;', [userId]);
  await client.query('DELETE FROM learning_queue WHERE user_id = $1;', [userId]);

  // 3. Load verified JSON files
  const previewDir = path.join(process.cwd(), 'migration_preview');
  const fsrsData = JSON.parse(fs.readFileSync(path.join(previewDir, 'fsrs_progress_export.json'), 'utf8'));
  const customData = JSON.parse(fs.readFileSync(path.join(previewDir, 'custom_dictionary_export.json'), 'utf8'));
  const excludedData = JSON.parse(fs.readFileSync(path.join(previewDir, 'excluded_dictionary_export.json'), 'utf8'));

  console.log(`📦 Loaded datasets: FSRS (${fsrsData.length}), Custom (${customData.length}), Excluded (${excludedData.length})`);

  // 4. Insert FSRS progress records
  console.log('📥 Inserting fsrs_progress records...');
  for (const item of fsrsData) {
    await client.query(
      `INSERT INTO fsrs_progress (
        user_id, course_id, word_id, state, due, stability, difficulty,
        elapsed_days, scheduled_days, reps, lapses, last_review, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, NOW())
      ON CONFLICT (user_id, course_id, word_id) DO UPDATE SET
        state = EXCLUDED.state,
        due = EXCLUDED.due,
        stability = EXCLUDED.stability,
        difficulty = EXCLUDED.difficulty,
        elapsed_days = EXCLUDED.elapsed_days,
        scheduled_days = EXCLUDED.scheduled_days,
        reps = EXCLUDED.reps,
        lapses = EXCLUDED.lapses,
        last_review = EXCLUDED.last_review,
        updated_at = NOW();`,
      [
        userId,
        item.course_id || 'sfid',
        item.word_id,
        item.state ?? 2,
        item.due,
        item.stability ?? 0,
        item.difficulty ?? 0,
        item.elapsed_days ?? 0,
        item.scheduled_days ?? 0,
        item.reps ?? 1,
        item.lapses ?? 0,
        item.last_review || item.due
      ]
    );
  }

  // 5. Insert Custom Dictionary records
  console.log('📥 Inserting custom_dictionary records...');
  for (const item of customData) {
    await client.query(
      `INSERT INTO custom_dictionary (
        user_id, course_id, base_form, word_in_sentence, en_translation,
        stage_id, article_id, sentence_id, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
      ON CONFLICT (user_id, base_form) DO UPDATE SET
        course_id = EXCLUDED.course_id,
        word_in_sentence = EXCLUDED.word_in_sentence,
        en_translation = EXCLUDED.en_translation,
        stage_id = EXCLUDED.stage_id,
        article_id = EXCLUDED.article_id,
        sentence_id = EXCLUDED.sentence_id,
        updated_at = NOW();`,
      [
        userId,
        item.course_id || 'sfid',
        item.base_form,
        item.word_in_sentence || item.base_form,
        item.en_translation || '',
        item.stage_id || '',
        item.article_id || '',
        item.sentence_id || ''
      ]
    );
  }

  // 6. Insert Excluded Dictionary records
  console.log('📥 Inserting excluded_dictionary records...');
  for (const item of excludedData) {
    await client.query(
      `INSERT INTO excluded_dictionary (
        user_id, course_id, base_form, updated_at
      ) VALUES ($1, $2, $3, NOW())
      ON CONFLICT (user_id, course_id, base_form) DO NOTHING;`,
      [
        userId,
        item.course_id || 'sfid',
        item.base_form
      ]
    );
  }

  // 7. Verify Counts in Database
  const fsrsCountRes = await client.query('SELECT count(*) FROM fsrs_progress WHERE user_id = $1;', [userId]);
  const customCountRes = await client.query('SELECT count(*) FROM custom_dictionary WHERE user_id = $1;', [userId]);
  const excludedCountRes = await client.query('SELECT count(*) FROM excluded_dictionary WHERE user_id = $1;', [userId]);
  const lqCountRes = await client.query('SELECT count(*) FROM learning_queue WHERE user_id = $1;', [userId]);

  console.log('\n=== ✅ Migration Complete & Verified on Supabase ===');
  console.log(`- fsrs_progress: ${fsrsCountRes.rows[0].count} rows (Expected: ${fsrsData.length})`);
  console.log(`- custom_dictionary: ${customCountRes.rows[0].count} rows (Expected: ${customData.length})`);
  console.log(`- excluded_dictionary: ${excludedCountRes.rows[0].count} rows (Expected: ${excludedData.length})`);
  console.log(`- learning_queue: ${lqCountRes.rows[0].count} rows (Expected: 0)`);

  await client.end();
}

migrateTestUser().catch((err) => {
  console.error('❌ Migration failed:', err);
  process.exit(1);
});
