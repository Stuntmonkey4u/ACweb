import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Import useAuth

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoadingPage, setIsLoadingPage] = useState(false); // Renamed to avoid conflict if useAuth also has isLoading

  const navigate = useNavigate();
  const { login, isLoading: isAuthLoading } = useAuth(); // Get login function and auth loading state from context

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoadingPage(true);

    try {
      // The backend expects x-www-form-urlencoded for token endpoint
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await fetch('/api/auth/login/token', { // Using Vite proxy
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      login(data.access_token); // Use context's login method
      navigate('/dashboard');

    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoadingPage(false);
    }
  };

  // Disable form if auth context is still loading initial state or if page is submitting
  const formDisabled = isAuthLoading || isLoadingPage;

  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md">
        <h1 className="text-3xl text-center mb-6 font-cinzel text-wotlk-gold">Account Login</h1>
        {error && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Username</label>
            <input
              type="text"
              id="username"
              className="input-themed"
              placeholder="Enter your username"
              value={username}
              // AC usernames often uppercase, but allow user to type mixed, backend handles comparison
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={formDisabled}
            />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Password</label>
            <input
              type="password"
              id="password"
              className="input-themed"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={formDisabled}
            />
          </div>
          <button
            type="submit"
            className="btn-primary w-full"
            disabled={formDisabled}
          >
            {isLoadingPage ? 'Logging In...' : (isAuthLoading ? 'Verifying...' : 'Login')}
          </button>
        </form>
        <p className="text-center mt-4 text-sm text-wotlk-text-dark">
          Don't have an account? <Link to="/register" className="text-wotlk-blue hover:underline font-bold">Register here</Link>.
        </p>
      </div>
    </div>
  );
};
export default LoginPage;
