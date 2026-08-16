import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_PUBLISHABLE_KEY;
const serviceKey = process.env.SUPABASE_SERVICE_API_KEY;

if (!supabaseUrl || !supabaseKey || !serviceKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

// 1. Anonymous client
const anonClient = createClient(supabaseUrl, supabaseKey);

// 2. Admin client to create an authenticated user
const adminClient = createClient(supabaseUrl, serviceKey);

async function runTest() {
  console.log('--- V-F01: Cloud Data & RLS Security Check ---');
  let success = true;

  // Anonymous fetch
  console.log('1. Attempting anonymous read of fsrs_progress...');
  const { data: anonReadData, error: anonReadError } = await anonClient
    .from('fsrs_progress')
    .select('*')
    .limit(1);

  if (anonReadError) {
    console.log(`Anonymous read correctly rejected or returned error: ${anonReadError.message}`);
  } else if (anonReadData && anonReadData.length > 0) {
    console.error('FAIL: Anonymous read succeeded and returned data! RLS not enforcing read.');
    success = false;
  } else {
    console.log('Anonymous read returned empty array. Valid if RLS is enabled and policies apply.');
  }

  console.log('2. Attempting anonymous write to fsrs_progress...');
  const { error: anonWriteError } = await anonClient
    .from('fsrs_progress')
    .insert({ user_id: '00000000-0000-0000-0000-000000000000', course_id: 'test', word_id: 'test_word' });

  if (anonWriteError) {
    console.log(`Anonymous write correctly rejected: ${anonWriteError.message}`);
  } else {
    console.error('FAIL: Anonymous write succeeded! RLS not enforcing write.');
    success = false;
  }

  // Authenticated fetch
  const email = `test-${Date.now()}@testapp.com`;
  const password = 'test_password_placeholder';
  
  await adminClient.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  });

  const authClient = createClient(supabaseUrl, supabaseKey);
  await authClient.auth.signInWithPassword({ email, password });
  
  const { data: sessionData } = await authClient.auth.getSession();
  const userId = sessionData.session?.user.id;
  if (!userId) {
     console.error('FAIL: Could not authenticate user');
     return;
  }

  console.log(`3. Attempting authenticated write as user ${userId}...`);
  const { error: authWriteError } = await authClient
    .from('fsrs_progress')
    .insert({ 
      user_id: userId, 
      course_id: 'sfid', 
      word_id: 'test_word', 
      state: 0, 
      reps: 0,
      due: new Date().toISOString(),
      stability: 0,
      difficulty: 0,
      elapsed_days: 0,
      scheduled_days: 0,
      lapses: 0,
      last_review: new Date().toISOString()
    });

  if (authWriteError) {
    console.error(`FAIL: Authenticated write failed: ${authWriteError.message}`);
    success = false;
  } else {
    console.log('Authenticated write succeeded.');
  }

  console.log('4. Attempting authenticated read...');
  const { data: authReadData, error: authReadError } = await authClient
    .from('fsrs_progress')
    .select('*')
    .eq('user_id', userId);

  if (authReadError) {
    console.error(`FAIL: Authenticated read failed: ${authReadError.message}`);
    success = false;
  } else if (authReadData && authReadData.length > 0) {
    console.log(`Authenticated read succeeded and returned ${authReadData.length} row(s).`);
  } else {
    console.error('FAIL: Authenticated read returned no data despite successful write.');
    success = false;
  }

  console.log(`--- V-F01 Result: ${success ? 'PASS' : 'FAIL'} ---`);
  process.exit(success ? 0 : 1);
}

runTest();
