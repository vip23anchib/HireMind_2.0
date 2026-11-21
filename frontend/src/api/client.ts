import axios from 'axios';

/**
 * Extract Django CSRF cookie value
 */
function getCookie(name: string): string | null {
  let cookieValue: string | null = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export const apiClient = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach Django CSRF Token
apiClient.interceptors.request.use((config) => {
  const csrfToken = getCookie('csrftoken');
  if (csrfToken && config.headers) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  return config;
});

// Response interceptor for consistent error extraction
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred. Please try again.';
    if (error.response?.data) {
      const data = error.response.data;
      if (typeof data.message === 'string') {
        message = data.message;
      } else if (typeof data.detail === 'string') {
        message = data.detail;
      } else if (typeof data === 'object') {
        // Collect field validation errors
        const errList = Object.entries(data)
          .map(([field, errs]) => `${field}: ${Array.isArray(errs) ? errs.join(', ') : errs}`)
          .join(' | ');
        if (errList) message = errList;
      }
    }
    return Promise.reject(new Error(message));
  }
);
