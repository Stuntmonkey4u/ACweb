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
  }
  // Add other methods like put, delete as needed
};
