import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 1000,
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
export const signup = data => api.post('/signup', data);
export const login = data => api.post('/login', data);
export const logout = () => api.post('/logout', {});
export const upload = data => api.post('/upload', data);
export const createPost = data => api.post('/post', data);
export const postLike = data => api.post('/like', data);
export const postDislike = data => api.post('/dislike', data);
export const postReply = data => api.post('/reply', data);
export const getReplies = postId => api.get(`/replies/${postId}`);
export default api;
