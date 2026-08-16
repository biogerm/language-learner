import { Client } from 'pg';
import * as dotenv from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
dotenv.config({ path: resolve(__dirname, '../.env.local') });

const dbPassword = process.env.SUPABASE_DB_PWD;
if (!dbPassword) {
    console.error('Missing SUPABASE_DB_PWD in .env.local');
    process.exit(1);
}

// Supabase postgres pooler connection string
const connectionString = `postgresql://postgres.qtyzqyzjqscdbjcfqwuz:${dbPassword}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres`;

const client = new Client({
    connectionString,
});

async function initDB() {
    try {
        await client.connect();
        console.log('Connected to Supabase PostgreSQL database.');

        // 1. Create courses table
        await client.query(`
            CREATE TABLE IF NOT EXISTS public.courses (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                r2_base_url TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
            );
        `);
        console.log('Created courses table.');

        // 2. Create fsrs_progress table
        await client.query(`
            CREATE TABLE IF NOT EXISTS public.fsrs_progress (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
                course_id TEXT REFERENCES public.courses(id) ON DELETE CASCADE,
                word_id TEXT NOT NULL,
                state INTEGER NOT NULL,
                due TIMESTAMP WITH TIME ZONE NOT NULL,
                stability DOUBLE PRECISION NOT NULL,
                difficulty DOUBLE PRECISION NOT NULL,
                elapsed_days INTEGER NOT NULL,
                scheduled_days INTEGER NOT NULL,
                reps INTEGER NOT NULL,
                lapses INTEGER NOT NULL,
                last_review TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
                UNIQUE(user_id, course_id, word_id)
            );
        `);
        console.log('Created fsrs_progress table.');

        // 3. Create updated_at trigger for offline sync conflict resolution
        // The trigger ensures updated_at is universally applied at the DB layer, 
        // defeating offline sync race conditions if client timestamps are skewed.
        await client.query(`
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = TIMEZONE('utc'::text, NOW());
                RETURN NEW;
            END;
            $$ language 'plpgsql';

            DROP TRIGGER IF EXISTS update_fsrs_progress_updated_at ON public.fsrs_progress;
            
            CREATE TRIGGER update_fsrs_progress_updated_at
                BEFORE UPDATE ON public.fsrs_progress
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        `);
        console.log('Created offline-sync conflict resolution trigger (updated_at).');

        // 4. Harden RLS Policies
        await client.query(`
            DROP POLICY IF EXISTS "Courses are viewable by everyone" ON public.courses;
            DROP POLICY IF EXISTS "Users can manage their own progress" ON public.fsrs_progress;
        `);

        await client.query(`
            ALTER TABLE public.courses ENABLE ROW LEVEL SECURITY;
            ALTER TABLE public.fsrs_progress ENABLE ROW LEVEL SECURITY;
            
            -- Courses are public to read, but modifications are implicitly denied
            CREATE POLICY "Courses are viewable by everyone" ON public.courses FOR SELECT USING (true);
            
            -- Progress: Strict separation. 
            -- USING enforces SELECT/UPDATE/DELETE. WITH CHECK enforces INSERT/UPDATE payloads.
            CREATE POLICY "Users can manage their own progress" ON public.fsrs_progress 
            FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
        `);
        console.log('Enabled Hardened Row Level Security (RLS) on tables.');
        
        // 5. Notify PostgREST to reload schema
        await client.query("NOTIFY pgrst, 'reload schema'");
        console.log('Reloaded PostgREST schema cache.');

        console.log('Database initialization complete.');
    } catch (err) {
        console.error('Error initializing database:', err);
    } finally {
        await client.end();
    }
}

initDB();
