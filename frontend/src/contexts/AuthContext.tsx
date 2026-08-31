import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../services/supabase';
import type { Session } from '@supabase/supabase-js';

interface AuthContextType {
  session: Session | null;
  loading: boolean;
  isTester: boolean;
}

const AuthContext = createContext<AuthContextType>({ session: null, loading: true, isTester: false });

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const testUserEmail = import.meta.env.VITE_TEST_USER_EMAIL;
  const isTester = Boolean(
    session?.user?.app_metadata?.is_tester === true ||
    session?.user?.app_metadata?.role === 'tester' ||
    session?.user?.app_metadata?.role === 'admin' ||
    (testUserEmail && session?.user?.email === testUserEmail)
  );

  return (
    <AuthContext.Provider value={{ session, loading, isTester }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
