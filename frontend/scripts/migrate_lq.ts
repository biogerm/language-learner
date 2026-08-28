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
    
    // Create learning_queue table
    await client.query(`
        CREATE TABLE IF NOT EXISTS public.learning_queue (
            id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id uuid REFERENCES auth.users NOT NULL,
            course_id text NOT NULL,
            article_id text NOT NULL,
            base_form text NOT NULL,
            dictation_passed boolean DEFAULT false,
            flashcard_passed boolean DEFAULT false,
            status text DEFAULT 'active',
            updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
            CONSTRAINT learning_queue_user_course_article_base_key UNIQUE (user_id, course_id, article_id, base_form)
        );
    `);

    // Add RLS
    await client.query(`ALTER TABLE public.learning_queue ENABLE ROW LEVEL SECURITY;`);
    
    await client.query(`
        DROP POLICY IF EXISTS "Users can read own learning queue" ON public.learning_queue;
        CREATE POLICY "Users can read own learning queue" ON public.learning_queue
            FOR SELECT USING (auth.uid() = user_id);
    `);
    
    await client.query(`
        DROP POLICY IF EXISTS "Users can insert own learning queue" ON public.learning_queue;
        CREATE POLICY "Users can insert own learning queue" ON public.learning_queue
            FOR INSERT WITH CHECK (auth.uid() = user_id);
    `);
    
    await client.query(`
        DROP POLICY IF EXISTS "Users can update own learning queue" ON public.learning_queue;
        CREATE POLICY "Users can update own learning queue" ON public.learning_queue
            FOR UPDATE USING (auth.uid() = user_id);
    `);

    // Add trigger for updated_at
    await client.query(`
        DROP TRIGGER IF EXISTS update_learning_queue_updated_at ON public.learning_queue;
        CREATE TRIGGER update_learning_queue_updated_at
            BEFORE UPDATE ON public.learning_queue
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    `);
    
    console.log("Migration complete.");
    await client.end();
}
run();
