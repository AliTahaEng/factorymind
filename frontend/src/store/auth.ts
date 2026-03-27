import { create } from 'zustand';
import { login as apiLogin, logout as apiLogout, getMe } from '@/lib/api';
import type { User } from '@/types/api';

const TOKEN_KEY = 'factorymind_token';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchMe: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null,
  isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem(TOKEN_KEY) : false,
  isLoading: false,

  login: async (username, password) => {
    set({ isLoading: true });
    try {
      const auth = await apiLogin(username, password);
      if (typeof window !== 'undefined') {
        localStorage.setItem(TOKEN_KEY, auth.access_token);
      }
      set({ token: auth.access_token, isAuthenticated: true, isLoading: false });
    } catch (err) {
      set({ isLoading: false });
      throw err;
    }
  },

  logout: async () => {
    try {
      await apiLogout();
    } catch {
      // ignore logout errors
    }
    if (typeof window !== 'undefined') {
      localStorage.removeItem(TOKEN_KEY);
    }
    set({ user: null, token: null, isAuthenticated: false });
  },

  fetchMe: async () => {
    set({ isLoading: true });
    try {
      const user = await getMe();
      set({ user, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },
}));
