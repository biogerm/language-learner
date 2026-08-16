import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn('Supabase URL or Key is missing from environment variables.');
}

export const supabase = createClient(supabaseUrl || '', supabaseKey || '');

/**
 * Sign in using OAuth provider
 */
export const signInWithOAuth = async (provider: 'google' | 'github' | 'apple') => {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider,
  });
  if (error) {
    console.error('Error signing in with OAuth:', error.message);
    throw error;
  }
  return data;
};

/**
 * Sign out the current user
 */
export const signOut = async () => {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Error signing out:', error.message);
    throw error;
  }
};

/**
 * Get the current user session
 */
export const getSession = async () => {
  const { data, error } = await supabase.auth.getSession();
  if (error) {
    console.error('Error getting session:', error.message);
    throw error;
  }

  if (!data.session) {
    const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession();
    if (refreshError) {
      console.warn('Could not refresh session:', refreshError.message);
      return null;
    }
    return refreshData.session;
  }
  
  return data.session;
};

export const signInWithEmail = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });
  if (error) {
    console.error('Error signing in with Email:', error.message);
    throw error;
  }
  return data;
};
