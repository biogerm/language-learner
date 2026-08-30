import { Client } from 'pg';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const client = new Client({
  connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`
});

async function upgradeFsrsSchema() {
  await client.connect();
  console.log('🔗 Connected to Supabase Postgres.');

  console.log('🛠️ Adding full FSRS mirror columns to public.fsrs_progress table...');
  await client.query(`
    ALTER TABLE public.fsrs_progress 
      ADD COLUMN IF NOT EXISTS today_dictation_passed BOOLEAN DEFAULT FALSE,
      ADD COLUMN IF NOT EXISTS today_flashcard_passed BOOLEAN DEFAULT FALSE,
      ADD COLUMN IF NOT EXISTS max_wrongs INTEGER DEFAULT 0,
      ADD COLUMN IF NOT EXISTS max_time DOUBLE PRECISION DEFAULT 0,
      ADD COLUMN IF NOT EXISTS gave_up BOOLEAN DEFAULT FALSE,
      ADD COLUMN IF NOT EXISTS reveal_count INTEGER DEFAULT 0,
      ADD COLUMN IF NOT EXISTS last_gate_pass_date TEXT;

    NOTIFY pgrst, 'reload schema';
  `);

  const cols = await client.query(`
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'fsrs_progress';
  `);

  console.log('✅ Updated columns in public.fsrs_progress:');
  console.table(cols.rows);

  await client.end();
  process.exit(0);
}

upgradeFsrsSchema().catch((err) => {
  console.error('❌ Schema upgrade failed:', err);
  process.exit(1);
});
