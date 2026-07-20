import axios from 'axios';
import { getAccessToken, setAccessToken, clearAccessToken } from './authStore';

const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 1000,
  withCredentials: true, // send the httpOnly refresh cookie
});

function getCookie(name) {
  const match = document.cookie.match(new RegExp(`(^|; )${name}=([^;]+)`));
  return match ? decodeURIComponent(match[2]) : null;
}

// skipAuth keeps the access header off /refresh so it can't shadow the cookie.
api.interceptors.request.use(config => {
  if (config.skipAuth) {
    return config;
  }
  const token = getAccessToken();
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function requestRefresh() {
  return api
    .post(
      '/refresh',
      {},
      {
        skipAuth: true,
        headers: { 'X-CSRF-TOKEN': getCookie('csrf_refresh_token') },
      }
    )
    .then(res => res.data.access_token);
}

// Shared in-flight refresh so concurrent 401s trigger a single /refresh.
let refreshPromise = null;

api.interceptors.response.use(
  response => response,
  async error => {
    const original = error.config;
    const status = error.response?.status;

    const isAuthError = status === 401 || status === 422;
    const isRefreshCall = original?.url?.includes('/refresh');
    if (!isAuthError || original?._retry || isRefreshCall) {
      return Promise.reject(error);
    }
    original._retry = true;

    try {
      refreshPromise = refreshPromise || requestRefresh();
      const newToken = await refreshPromise;
      refreshPromise = null;
      setAccessToken(newToken);
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch (refreshError) {
      // Refresh failed: user is logged out. Retry once with no auth so public
      // requests still succeed; protected ones fail for the caller to handle.
      refreshPromise = null;
      clearAccessToken();
      if (typeof original.headers?.delete === 'function') {
        original.headers.delete('Authorization');
      } else if (original.headers) {
        delete original.headers.Authorization;
      }
      return api(original);
    }
  }
);

export const signup = data => api.post('/signup', data);
export const login = data => api.post('/login', data);
export const logout = () => api.post('/logout', {});
export const refresh = requestRefresh;
export const upload = data => api.post('/upload', data);
export const createPost = data => api.post('/post', data);
export const postLike = data => api.post('/like', data);
export const postDislike = data => api.post('/dislike', data);
export const postReply = data => api.post('/reply', data);
export const getReplies = postId => api.get(`/replies/${postId}`);
export default api;
