import { Client } from 'pg';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });
if (!process.env.SUPABASE_DB_URL) throw new Error('Set SUPABASE_DB_URL in .env.local');

const client = new Client({
  connectionString: process.env.SUPABASE_DB_URL,
});

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: resolve(__dirname, '../.env.local') });

connectionString: process.env.SUPABASE_DB_URL,
});

async function run() {
    await client.connect();
    const res = await client.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';");
    console.log(res.rows);
    await client.end();
}
run();
