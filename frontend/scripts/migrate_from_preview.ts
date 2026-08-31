import { Client } from 'pg';
import * as dotenv from 'dotenv';
import { fsrsProgressToMigrate } from '../migration_preview/fsrs_progress_to_migrate.js';
import { customDictionaryToMigrate } from '../migration_preview/custom_dictionary_to_migrate.js';
import { excludedDictionaryToMigrate } from '../migration_preview/excluded_dictionary_to_migrate.js';

dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`
});

async function runMigration() {
  console.log('🚀 Starting Supabase Database Migration from Verified Previews...');
  await client.connect();

  // 1. Get test user id
  const userRes = await client.query("SELECT id, email FROM auth.users WHERE email = process.env.TEST_USER_EMAIL || 'test@example.com';");
  if (userRes.rows.length === 0) {
    throw new Error("Target user process.env.TEST_USER_EMAIL || 'test@example.com' not found in auth.users");
  }
  const userId = userRes.rows[0].id;
  console.log(`👤 Target User ID: ${userId} (${userRes.rows[0].email})`);

  await client.query('BEGIN');

  try {
    // 2. Clean existing user records
    console.log('🧹 Purging any existing records for user...');
    await client.query('DELETE FROM fsrs_progress WHERE user_id = $1;', [userId]);
    await client.query('DELETE FROM custom_dictionary WHERE user_id = $1;', [userId]);
    await client.query('DELETE FROM learning_queue WHERE user_id = $1;', [userId]);

    // 3. Migrate FSRS Progress (262 words)
    console.log(`📦 Migrating ${fsrsProgressToMigrate.length} FSRS progress records...`);
    const parseSafeDate = (d: any) => {
      if (!d) return null;
      const date = new Date(d);
      return isNaN(date.getTime()) ? null : date;
    };

    for (const item of fsrsProgressToMigrate) {
      await client.query(`
        INSERT INTO fsrs_progress (
          user_id, word_id, course_id, due, stability, difficulty,
          elapsed_days, scheduled_days, reps, lapses, state, last_review
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
        );
      `, [
        userId,
        item.word_id,
        item.course_id,
        parseSafeDate(item.due) || new Date(),
        item.stability || 0,
        item.difficulty || 0,
        item.elapsed_days || 0,
        item.scheduled_days || 0,
        item.reps || 0,
        item.lapses || 0,
        item.state ?? 0,
        parseSafeDate(item.last_review)
      ]);
    }

    // 4. Migrate Custom Dictionary (98 words / 96 unique)
    console.log(`📖 Migrating ${customDictionaryToMigrate.length} Custom Dictionary records...`);
    for (const item of customDictionaryToMigrate) {
      await client.query(`
        INSERT INTO custom_dictionary (
          user_id, base_form, word_in_sentence, en_translation,
          stage_id, article_id, sentence_id, course_id
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7, $8
        )
        ON CONFLICT (user_id, base_form) DO UPDATE SET
          word_in_sentence = EXCLUDED.word_in_sentence,
          en_translation = EXCLUDED.en_translation,
          stage_id = EXCLUDED.stage_id,
          article_id = EXCLUDED.article_id,
          sentence_id = EXCLUDED.sentence_id,
          course_id = EXCLUDED.course_id;
      `, [
        userId,
        item.base_form,
        item.word_in_sentence,
        item.en_translation,
        item.stage_id,
        item.article_id,
        item.sentence_id,
        item.course_id
      ]);
    }

    // 5. Ensure learning_queue is 0 records
    const lqCountRes = await client.query('SELECT count(*) FROM learning_queue WHERE user_id = $1;', [userId]);
    console.log(`✨ Learning Queue user records count: ${lqCountRes.rows[0].count} (Expected: 0)`);

    await client.query('COMMIT');
    console.log('✅ All transaction queries committed successfully!');

    // 6. Verify row counts
    const fsrsCount = await client.query('SELECT count(*) FROM fsrs_progress WHERE user_id = $1;', [userId]);
    const customCount = await client.query('SELECT count(*) FROM custom_dictionary WHERE user_id = $1;', [userId]);
    console.log('\n📊 === MIGRATION VERIFICATION ===');
    console.log(`- fsrs_progress rows: ${fsrsCount.rows[0].count} (Expected: 262)`);
    console.log(`- custom_dictionary rows: ${customCount.rows[0].count} (Expected: 98)`);
    console.log(`- learning_queue rows: ${lqCountRes.rows[0].count} (Expected: 0)`);

  } catch (err) {
    await client.query('ROLLBACK');
    console.error('❌ Migration failed! Rolled back transaction:', err);
    throw err;
  } finally {
    await client.end();
  }
}

runMigration().catch(console.error);
