import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import {
  getAccessToken,
  setAccessToken,
  clearAccessToken,
  subscribe,
} from '../api/authStore';
import { logout as apiLogout, refresh as apiRefresh } from '../api/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getAccessToken());
  // True until the on-load refresh settles, so consumers can wait for auth.
  const [bootstrapping, setBootstrapping] = useState(true);

  useEffect(() => subscribe(setToken), []);

  // Mint a fresh access token from the refresh cookie so a reload stays signed
  // in. If it fails, the user is simply logged out.
  useEffect(() => {
    let active = true;
    apiRefresh()
      .then(newToken => {
        if (active && newToken) {
          setAccessToken(newToken);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (active) {
          setBootstrapping(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(newToken => {
    setAccessToken(newToken);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout(); // clears the refresh cookie server-side
    } catch (err) {
      console.error(err);
    }
    clearAccessToken();
  }, []);

  const value = { token, isLoggedIn: !!token, bootstrapping, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
