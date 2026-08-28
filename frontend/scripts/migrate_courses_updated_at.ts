import { Client } from 'pg';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: resolve(__dirname, '../.env.local') });

const client = new Client({ connectionString: `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${process.env.SUPABASE_DB_PWD}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres` });

async function run() {
    await client.connect();
    
    // Add updated_at column if it doesn't exist
    await client.query(`
        ALTER TABLE public.courses
        ADD COLUMN IF NOT EXISTS updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL;
    `);

    // Force an update to NOW() so that existing clients invalidate their cache
    await client.query(`
        UPDATE public.courses SET updated_at = timezone('utc'::text, now());
    `);
    
    console.log("Migration complete: added updated_at to courses.");
    await client.end();
}
run();
