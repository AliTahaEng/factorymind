'use client';

import { useCallback } from 'react';
import { useAuthStore } from '@/store/auth';

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const storeLogin = useAuthStore((s) => s.login);
  const storeLogout = useAuthStore((s) => s.logout);
  const fetchMe = useAuthStore((s) => s.fetchMe);

  const login = useCallback(
    async (username: string, password: string) => {
      await storeLogin(username, password);
      await fetchMe();
    },
    [storeLogin, fetchMe]
  );

  const logout = useCallback(async () => {
    await storeLogout();
  }, [storeLogout]);

  return { user, isAuthenticated, isLoading, login, logout };
}
