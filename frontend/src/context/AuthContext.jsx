import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api'; // Assuming apiClient is set up for GET requests too
import { jwtDecode } from 'jwt-decode'; // Install jwt-decode: npm install jwt-decode

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // User object or null
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState(true); // For initial auth check

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      setToken(storedToken);
      // apiClient should automatically use the token from localStorage or its interceptors
      apiClient.get('/auth/users/me')
        .then(response => { // Assuming response.data contains the user object
          setUser(response.data);
        })
        .catch(error => {
          console.error("Failed to fetch user with stored token", error);
          localStorage.removeItem('authToken'); // Invalid token
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  // Login function updated to take credentials and totpCode
  const login = async (username, password, totpCode = null) => {
    setIsLoading(true);
    try {
      // apiClient.login now makes the actual API call
      const loginResponse = await apiClient.login(username, password, totpCode);
      const newToken = loginResponse.access_token;

      localStorage.setItem('authToken', newToken);
      setToken(newToken);

      // Fetch user details using the new token
      // apiClient.getCurrentUser now takes the token explicitly as per api.js design
      const userDataResponse = await apiClient.getCurrentUser(newToken);
      setUser(userDataResponse);
      setIsLoading(false);
      return userDataResponse; // Return user data on successful login
    } catch (error) {
      // Log out or clear token if any step fails to prevent inconsistent state
      localStorage.removeItem('authToken');
      setToken(null);
      setUser(null);
      setIsLoading(false);
      console.error("Login process failed", error);
      throw error; // Rethrow error to be caught by LoginPage
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  };

  const getTokenPayload = () => {
    if (token) {
      try {
        return jwtDecode(token);
      } catch (error) {
        console.error("Error decoding token:", error);
        return null;
      }
    }
    return null;
  };


  return (
    <AuthContext.Provider value={{ user, token, login, logout, getTokenPayload, isAuthenticated: !!token, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
