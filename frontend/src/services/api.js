// Basic API service wrapper
const BASE_URL = '/api'; // Using Vite's proxy

export const apiClient = {
  post: async (endpoint, data, token = null) => {
    const headers = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(\`\${BASE_URL}\${endpoint}\`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(data),
      });

      const responseData = await response.json();

      if (!response.ok) {
        // Throw an error object that includes status and message
        const error = new Error(responseData.detail || 'API request failed');
        error.status = response.status;
        error.data = responseData; // Contains full error details from backend
        throw error;
      }
      return responseData;
    } catch (error) {
      // If it's already our custom error, rethrow it
      if (error.status) throw error;
      // Else, wrap it or handle as a network error
      console.error('API call error:', error);
      throw new Error('Network error or API is unreachable.');
    }
  },

  get: async (endpoint, token = null) => {
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(\`\${BASE_URL}\${endpoint}\`, {
        method: 'GET',
        headers: headers,
      });
      const responseData = await response.json();
      if (!response.ok) {
        const error = new Error(responseData.detail || 'API request failed');
        error.status = response.status;
        error.data = responseData;
        throw error;
      }
      return responseData;
    } catch (error) {
      if (error.status) throw error;
      console.error('API call error:', error);
      throw new Error('Network error or API is unreachable.');
    }
  },
  // Add other methods like put, delete as needed

  // Specific function for email verification (doesn't need auth token)
  verifyEmail: async (token) => {
    // Uses the existing post method, but token is part of the payload, not header
    return apiClient.post('/auth/verify-email', { token });
  },

  // --- Auth ---
  login: async (username, password, totpCode = null) => {
    // Note: The generic 'post' method needs to be aware of not sending a token for login.
    // Or, login should be a special case not using the generic 'post' if 'post' always tries to attach auth token.
    // For now, assuming 'post' doesn't add Auth header if token is null.
    // The backend /login/token endpoint does not require an Authorization header.
    return apiClient.post('/auth/login/token', { username, password, totp_code: totpCode });
  },

  register: async (userData) => {
    // userData should include: username, email, password, captcha_id, captcha_solution
    return apiClient.post('/auth/register', userData);
  },

  requestPasswordReset: async (usernameOrEmail, captchaId, captchaSolution) => {
    return apiClient.post('/auth/password-reset/request', {
      username: usernameOrEmail,
      captcha_id: captchaId,
      captcha_solution: captchaSolution,
    });
  },

  // --- CAPTCHA ---
  generateCaptcha: async () => {
    return apiClient.get('/auth/captcha/generate'); // No token needed
  },

  // --- 2FA ---
  setup2FA: async (authToken) => {
    // Requires authentication, so pass the token
    return apiClient.post('/auth/2fa/setup', {}, authToken);
  },

  enable2FA: async (totpCode, authToken) => {
    return apiClient.post('/auth/2fa/enable', { totp_code: totpCode }, authToken);
  },

  disable2FA: async (totpCode, authToken) => {
    return apiClient.post('/auth/2fa/disable', { totp_code: totpCode }, authToken);
  },

  // --- User ---
  // Example: Fetch current user (get method needs to handle token)
  getCurrentUser: async (authToken) => {
    return apiClient.get('/auth/users/me', authToken);
  },

  // --- Admin ---
  adminListUsers: async (authToken) => {
    return apiClient.get('/admin/users', authToken);
  },
  adminBanUser: async (userId, authToken) => {
    return apiClient.post(`/admin/users/${userId}/ban`, {}, authToken);
  },
  adminUnbanUser: async (userId, authToken) => {
    return apiClient.post(`/admin/users/${userId}/unban`, {}, authToken);
  },
  adminPromoteUser: async (userId, authToken) => {
    return apiClient.post(`/admin/users/${userId}/promote`, {}, authToken);
  },
  adminDemoteUser: async (userId, authToken) => {
    return apiClient.post(`/admin/users/${userId}/demote`, {}, authToken);
  },

  // --- Downloads ---
  getClientDownloadInfo: async (authToken) => {
    return apiClient.get('/downloads/client-info', authToken);
  }
};
