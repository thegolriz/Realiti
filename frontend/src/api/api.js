import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5001/api",
  timeout: 1000,
});
export const signup = (data) => api.post('/signup', data);
export const login = (data) => api.post('/login', data);
export const createPost = (data, token) => api.post('/post', data, {
  headers: { Authorization: `Bearer ${token}` }
});
