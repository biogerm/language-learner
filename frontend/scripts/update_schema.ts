import { Client } from 'pg';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });
if (!process.env.SUPABASE_DB_URL) throw new Error('Set SUPABASE_DB_URL in .env.local');

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: resolve(__dirname, '../.env.local') });

const dbPassword = process.env.SUPABASE_DB_PWD;
if (!dbPassword) {
    console.error('Missing SUPABASE_DB_PWD in .env.local');
    process.exit(1);
}

const client = new Client({
  connectionString: process.env.SUPABASE_DB_URL,
    connectionString,
});

async function updateSchema() {
    try {
        await client.connect();
        console.log('Connected to Supabase PostgreSQL database.');
        
        await client.query(`
            ALTER TABLE public.courses ADD COLUMN IF NOT EXISTS r2_json_url TEXT;
            NOTIFY pgrst, 'reload schema';
        `);
        console.log('Successfully added r2_json_url column and reloaded PostgREST cache.');
    } catch (err) {
        console.error('Error updating database:', err);
    } finally {
        await client.end();
    }
}

updateSchema();
