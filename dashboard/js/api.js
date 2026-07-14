/**
 * HSE Dashboard — Centralized API Client
 * 
 * All API calls go through this module.
 * Handles:
 * - Base URL configuration
 * - JWT token injection
 * - Token refresh on 401
 * - Error handling & retries
 * - Request/response logging
 */

const API_BASE_URL = localStorage.getItem('API_BASE_URL') || 'http://localhost:8000';

/**
 * Get access token from storage
 */
function getAccessToken() {
  return localStorage.getItem('hse_access_token');
}

/**
 * Get refresh token from storage
 */
function getRefreshToken() {
  return localStorage.getItem('hse_refresh_token');
}

/**
 * Set tokens in storage
 */
function setTokens(accessToken, refreshToken) {
  localStorage.setItem('hse_access_token', accessToken);
  if (refreshToken) {
    localStorage.setItem('hse_refresh_token', refreshToken);
  }
}

/**
 * Clear tokens from storage (logout)
 */
function clearTokens() {
  localStorage.removeItem('hse_access_token');
  localStorage.removeItem('hse_refresh_token');
  localStorage.removeItem('hse_user');
}

/**
 * Get current user from storage
 */
function getCurrentUser() {
  const user = localStorage.getItem('hse_user');
  return user ? JSON.parse(user) : null;
}

/**
 * Set current user in storage
 */
function setCurrentUser(user) {
  localStorage.setItem('hse_user', JSON.stringify(user));
}

/**
 * Refresh access token using refresh token
 */
async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }

  const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    // Refresh token expired or invalid
    clearTokens();
    window.dispatchEvent(new Event('auth:logout'));
    throw new Error('Session expired');
  }

  const data = await response.json();
  setTokens(data.access_token, data.refresh_token);
  return data.access_token;
}

/**
 * Make an authenticated API request with auto-refresh
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  let accessToken = getAccessToken();

  // Prepare headers
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authorization header if token exists
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  // Make request
  let response = await fetch(url, {
    ...options,
    headers,
  });

  // If 401, try to refresh token once
  if (response.status === 401 && accessToken) {
    try {
      const newToken = await refreshAccessToken();
      headers['Authorization'] = `Bearer ${newToken}`;
      response = await fetch(url, {
        ...options,
        headers,
      });
    } catch (refreshError) {
      // Refresh failed, user needs to login again
      clearTokens();
      window.dispatchEvent(new Event('auth:logout'));
      throw new Error('Session expired. Please login again.');
    }
  }

  // Handle non-OK responses
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch (e) {
      // Ignore JSON parse error
    }
    throw new Error(errorMessage);
  }

  // Return parsed JSON or text
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json();
  }
  return await response.text();
}

/**
 * GET request
 */
async function apiGet(endpoint, params = {}) {
  // Convert params to query string
  const queryString = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryString.append(key, value);
    }
  });

  const url = queryString.toString() ? `${endpoint}?${queryString.toString()}` : endpoint;
  return apiRequest(url, {
    method: 'GET',
  });
}

/**
 * POST request
 */
async function apiPost(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * PUT request
 */
async function apiPut(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * DELETE request
 */
async function apiDelete(endpoint) {
  return apiRequest(endpoint, {
    method: 'DELETE',
  });
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
  return !!getAccessToken();
}

/**
 * Get user role
 */
function getUserRole() {
  const user = getCurrentUser();
  return user?.role || null;
}

/**
 * Get user site access
 */
function getUserSiteAccess() {
  const user = getCurrentUser();
  return user?.site_access || [];
}

/**
 * Export API client
 */
window.API = {
  baseUrl: API_BASE_URL,
  get: apiGet,
  post: apiPost,
  put: apiPut,
  delete: apiDelete,
  request: apiRequest,
  isAuthenticated,
  getUserRole,
  getUserSiteAccess,
  getCurrentUser,
  setCurrentUser,
  clearTokens,
  refreshAccessToken,
};
