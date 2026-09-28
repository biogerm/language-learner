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

const client = new Client({ connectionString });

async function run() {
    try {
        await client.connect();
        await client.query(`
            ALTER TABLE public.custom_dictionary ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW());
            
            DROP TRIGGER IF EXISTS update_custom_dictionary_updated_at ON public.custom_dictionary;
            
            CREATE TRIGGER update_custom_dictionary_updated_at
                BEFORE UPDATE ON public.custom_dictionary
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
                
            NOTIFY pgrst, 'reload schema';
        `);
        console.log('Successfully added updated_at to custom_dictionary');
    } catch (err) {
        console.error(err);
    } finally {
        await client.end();
    }
}
run();
