// In-memory access token (never localStorage). Bridges the axios interceptors
// and React: interceptors call the setters, AuthContext subscribes.

let accessToken = null;
const listeners = new Set();

export function getAccessToken() {
  return accessToken;
}

export function setAccessToken(token) {
  accessToken = token;
  listeners.forEach(fn => fn(token));
}

export function clearAccessToken() {
  setAccessToken(null);
}

// Returns an unsubscribe function.
export function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
