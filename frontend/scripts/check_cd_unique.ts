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
    
    // First remove duplicates if any exist
    await client.query(`
        DELETE FROM public.custom_dictionary a USING (
            SELECT MIN(ctid) as ctid, user_id, base_form
            FROM public.custom_dictionary
            GROUP BY user_id, base_form HAVING COUNT(*) > 1
        ) b
        WHERE a.user_id = b.user_id AND a.base_form = b.base_form AND a.ctid <> b.ctid;
    `);

    // Create unique constraint
    await client.query("ALTER TABLE public.custom_dictionary ADD CONSTRAINT custom_dictionary_user_base_form_key UNIQUE (user_id, base_form);").catch(e => console.log(e.message));
    
    await client.end();
}
run();
