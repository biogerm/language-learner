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
    const res = await client.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';");
    console.log(res.rows);
    await client.end();
}
run();
