import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../services/api'; // Ensure this path is correct

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }
    // Basic regex for username (alphanumeric + underscore, 3-16 chars)
    if (!/^[a-zA-Z0-9_]{3,16}$/.test(username)) {
        setError('Username must be 3-16 characters long and contain only letters, numbers, and underscores.');
        return;
    }
    // Basic email validation (very simple)
    if (!/\S+@\S+\.\S+/.test(email)) {
        setError('Please enter a valid email address.');
        return;
    }


    setIsLoading(true);
    try {
      const response = await apiClient.post('/auth/register', {
        username,
        email,
        password,
      });
      setSuccessMessage('Registration successful! You can now log in.');
      // Clear form
      setUsername('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      // Optionally redirect to login page after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      setError(err.data?.detail || err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md">
        <h1 className="text-3xl text-center mb-6 font-cinzel text-wotlk-gold">Create Account</h1>

        {error && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{error}</div>}
        {successMessage && <div className="bg-green-500 text-white p-3 rounded mb-4 text-sm">{successMessage}</div>}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Username</label>
            <input
              type="text"
              id="username"
              className="input-themed"
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength="3"
              maxLength="16"
              pattern="^[a-zA-Z0-9_]+$"
            />
          </div>
           <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Email</label>
            <input
              type="email"
              id="email"
              className="input-themed"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Password</label>
            <input
              type="password"
              id="password"
              className="input-themed"
              placeholder="Create a password (min. 6 chars)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength="6"
            />
          </div>
          <div className="mb-6">
            <label htmlFor="confirmPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Confirm Password</label>
            <input
              type="password"
              id="confirmPassword"
              className="input-themed"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength="6"
            />
          </div>
          <button
            type="submit"
            className="btn-primary w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Registering...' : 'Register Account'}
          </button>
        </form>
        <p className="text-center mt-4 text-sm text-wotlk-text-dark">
          Already have an account? <Link to="/login" className="text-wotlk-blue hover:underline font-bold">Login here</Link>.
        </p>
      </div>
    </div>
  );
};
export default RegisterPage;
