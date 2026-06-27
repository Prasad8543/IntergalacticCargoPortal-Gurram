import { createContext, useContext, useMemo, useState } from 'react';
import { logoutUser } from '../api';

const AuthContext = createContext(null);
const STORAGE_KEY = 'cargo_portal_auth';

function readStoredAuth() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return { user: null, token: null };
  try {
    return JSON.parse(raw);
  } catch {
    return { user: null, token: null };
  }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(readStoredAuth);

  const value = useMemo(
    () => ({
      user: auth.user,
      token: auth.token,
      login(authPayload) {
        setAuth(authPayload);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(authPayload));
      },
      async logout() {
        const token = auth.token;
        if (token) {
          try {
            await logoutUser(token);
          } catch {
            // Clear local session even if the server call fails.
          }
        }
        setAuth({ user: null, token: null });
        localStorage.removeItem(STORAGE_KEY);
      },
    }),
    [auth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
