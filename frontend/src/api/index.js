import axios from 'axios'

// Figure out the correct base URL
const isProduction = process.env.NODE_ENV === 'production';
const apiBaseURL = isProduction ? 
  (process.env.VUE_APP_API_URL || '') : 
  (process.env.VUE_APP_API_URL || 'http://localhost:8000');

// Create an axios instance
const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Set up axios default base URL as well for any direct axios usage
axios.defaults.baseURL = apiBaseURL;

// Log the baseURL for debugging
console.log('API base URL configured as:', apiBaseURL);

// Request interceptor
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // If we get a 401, clear token and redirect to login
      localStorage.removeItem('token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
