import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5001/api',
  timeout: 1000,
});
export const signup = data => api.post('/signup', data);
export const login = data => api.post('/login', data);
export const upload = (data, token) =>
  api.post('/upload', data, {
    headers: { Authorization: `Bearer ${token}` },
  });
export const createPost = (data, token) =>
  api.post('/post', data, {
    headers: { Authorization: `Bearer ${token}` },
  });
export const postLike = (data, token) =>
  api.post('/like', data, {
    headers: { Authorization: `Bearer ${token}` },
  });
export const postDislike = (data, token) =>
  api.post('/dislike', data, {
    headers: { Authorization: `Bearer ${token}` },
  });
export const postReply = (data, token) =>
  api.post('/reply', data, {
    headers: { Authorization: `Bearer ${token}` },
  });
export const getReplies = postId => api.get(`/replies/${postId}`);
export default api;
