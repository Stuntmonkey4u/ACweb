import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Import useAuth

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [totpCode, setTotpCode] = useState('');
  const [error, setError] = useState('');
  const [isLoadingPage, setIsLoadingPage] = useState(false);
  const [showTotpField, setShowTotpField] = useState(false); // To dynamically show TOTP field

  const navigate = useNavigate();
  const { login, isLoading: isAuthLoading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoadingPage(true);

    try {
      await login(username, password, totpCode); // Use context's login method
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err.data?.detail || err.message || 'Login failed.';
      setError(errorMessage);
      // Check if error indicates TOTP is required or invalid
      if (errorMessage.toLowerCase().includes("totp code required")) {
        setShowTotpField(true);
        setError("TOTP code required. Please enter it below."); // More specific error
      } else if (errorMessage.toLowerCase().includes("invalid totp code")) {
        setShowTotpField(true);
        setError("Invalid TOTP code. Please try again."); // More specific error
      } else {
        setShowTotpField(false); // Hide if other error
      }
    } finally {
      setIsLoadingPage(false);
    }
  };

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
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={formDisabled}
            />
          </div>
          <div className="mb-4">
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
          {/* Always show TOTP field for simplicity, backend handles if not needed or if user doesn't have 2FA */}
          <div className="mb-6">
            <label htmlFor="totpCode" className="block text-sm font-bold mb-2 text-wotlk-text-dark">
              2FA Code (if enabled)
            </label>
            <input
              type="text"
              id="totpCode"
              className="input-themed"
              placeholder="Enter 6-digit code"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              maxLength="6"
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
