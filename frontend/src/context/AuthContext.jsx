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
      // Optional: Validate token with backend or decode to get user info quickly
      // For now, we'll fetch user details if token exists
      apiClient.get('/auth/users/me', storedToken)
        .then(userData => {
          setUser(userData);
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

  const login = (newToken) => {
    localStorage.setItem('authToken', newToken);
    setToken(newToken);
    // Fetch user details upon login
    setIsLoading(true);
    apiClient.get('/auth/users/me', newToken)
      .then(userData => {
        setUser(userData);
      })
      .catch(error => {
        console.error("Failed to fetch user after login", error);
        // Handle this case, maybe logout?
        logout();
      })
      .finally(() => setIsLoading(false));
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
