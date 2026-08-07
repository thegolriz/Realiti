import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { getAccessToken, setAccessToken, clearAccessToken, subscribe } from '../api/authStore';
import { logout as apiLogout, refresh as apiRefresh, getAccount } from '../api/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(getAccessToken());
  // True until the on-load refresh settles, so consumers can wait for auth.
  const [bootstrapping, setBootstrapping] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  // The signed-in user's own id, so a page can tell "this is me" apart from
  // "this is someone else". Null while logged out or still resolving.
  const [userId, setUserId] = useState(null);
  // False while we're still fetching the profile to learn the admin flag, so
  // an admin route can wait instead of bouncing a real admin mid-load.
  const [adminResolved, setAdminResolved] = useState(false);

  useEffect(() => subscribe(setToken), []);

  // Whenever the token changes, (re)load the profile to learn is_admin.
  useEffect(() => {
    if (!token) {
      setIsAdmin(false);
      setUserId(null);
      setAdminResolved(true);
      return;
    }
    let active = true;
    setAdminResolved(false);
    getAccount()
      .then(res => {
        if (active) {
          setIsAdmin(!!res.data.is_admin);
          setUserId(res.data.id ?? null);
        }
      })
      .catch(() => {
        if (active) {
          setIsAdmin(false);
          setUserId(null);
        }
      })
      .finally(() => {
        if (active) {
          setAdminResolved(true);
        }
      });
    return () => {
      active = false;
    };
  }, [token]);

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

  const value = {
    token,
    isLoggedIn: !!token,
    isAdmin,
    userId,
    adminResolved,
    bootstrapping,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
