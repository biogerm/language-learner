import { createClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import { resolve } from 'path';

dotenv.config({ path: '.env.local' });

const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Missing Supabase credentials');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function testAuth() {
  console.log('Testing Supabase Auth...');
  
  const email = `test-${Date.now()}@testapp.com`;
  const password = 'test_password_placeholder';
  
  const serviceKey = process.env.SUPABASE_SERVICE_API_KEY;
  if (!serviceKey) throw new Error('Missing service key');
  
  const adminClient = createClient(supabaseUrl, serviceKey);
  
  console.log(`Attempting to create and confirm user with ${email}...`);
  const { data: adminData, error: adminError } = await adminClient.auth.admin.createUser({
    email,
    password,
    email_confirm: true,
  });
  
  if (adminError) {
    console.error('Admin create user error:', adminError.message);
  } else {
    console.log('User created and confirmed:', adminData.user.id);
  }
  
  console.log('Attempting to sign in with normal client...');
  const { data: signInData, error: signInError } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  
  if (signInError) {
    console.error('Sign in error:', signInError.message);
  } else {
    console.log('Sign in successful.');
  }

  const { data, error } = await supabase.auth.getSession();
  if (error) {
    console.error('Error getting session:', error.message);
    process.exit(1);
  }
  
  // If email confirmation is required, session might still be null.
  // We can also try sign in with an existing dummy user if sign up requires confirmation.
  console.log('Session retrieved successfully.');
  console.log('Session object is null?:', data.session === null);
  if (data.session) {
    console.log('User ID:', data.session.user.id);
  }
}

testAuth();
