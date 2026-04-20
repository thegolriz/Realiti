import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5001/api",
  timeout: 1000,
});
export const signup = (data) => api.post('/api/signup', data);
export const login = (data) => api.post('/api/login', data);
export const upload = (data, token) => api.post('/api/upload', data, {
  headers: { Authorization: `Bearer ${token}` }
});
export const createPost = (data, token) => api.post('/api/post', data, {
  headers: { Authorization: `Bearer ${token}` }
});
