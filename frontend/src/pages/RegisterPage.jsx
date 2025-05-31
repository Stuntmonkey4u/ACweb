import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../services/api';

const RegisterPage = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [captchaChallenge, setCaptchaChallenge] = useState({ id: '', question: '' });
  const [captchaSolution, setCaptchaSolution] = useState('');
  const [captchaLoadingError, setCaptchaLoadingError] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isCaptchaLoading, setIsCaptchaLoading] = useState(false);
  const navigate = useNavigate();

  const fetchCaptchaChallenge = async () => {
    setIsCaptchaLoading(true);
    setCaptchaLoadingError('');
    try {
      const response = await apiClient.generateCaptcha();
      setCaptchaChallenge({ id: response.id, question: response.question });
    } catch (err) {
      setCaptchaLoadingError('Failed to load CAPTCHA. Please try refreshing.');
      setCaptchaChallenge({ id: '', question: '' }); // Clear previous challenge
    } finally {
      setIsCaptchaLoading(false);
    }
  };

  useEffect(() => {
    fetchCaptchaChallenge();
  }, []);

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
    if (!/^[a-zA-Z0-9_]{3,16}$/.test(username)) {
        setError('Username must be 3-16 characters long and contain only letters, numbers, and underscores.');
        return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
        setError('Please enter a valid email address.');
        return;
    }
    if (!captchaChallenge.id || !captchaSolution) {
      setError('Please solve the CAPTCHA.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiClient.register({
        username,
        email,
        password,
        captcha_id: captchaChallenge.id,
        captcha_solution: captchaSolution,
      });
      const userEmail = response.email || email;
      setSuccessMessage(`Registration successful! If the server is online and email is configured, a verification email has been sent to ${userEmail}. Please check your inbox to verify your account.`);
      setUsername('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
      setCaptchaSolution('');
      fetchCaptchaChallenge(); // Fetch new captcha for potential next attempt
      setTimeout(() => {
        navigate('/login');
      }, 3000); // Increased delay for message reading
    } catch (err) {
      const errorDetail = err.data?.detail || err.message || 'Registration failed. Please try again.';
      setError(errorDetail);
      // If CAPTCHA was invalid, fetch a new one
      if (errorDetail.toLowerCase().includes("captcha")) {
        fetchCaptchaChallenge();
        setCaptchaSolution(''); // Clear solution field
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md">
        <h1 className="text-3xl text-center mb-6 font-cinzel text-wotlk-gold">Create Account</h1>

        {error && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{error}</div>}
        {captchaLoadingError && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{captchaLoadingError}</div>}
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
          <div className="mb-4"> {/* Adjusted margin */}
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

          {/* CAPTCHA Section */}
          <div className="mb-4 p-3 bg-wotlk-parchment-dark rounded">
            <label htmlFor="captcha" className="block text-sm font-bold mb-2 text-wotlk-blue">
              CAPTCHA: {captchaChallenge.question || "Loading..."}
            </label>
            <div className="flex items-center">
              <input
                type="text"
                id="captcha"
                className="input-themed mr-2 flex-grow"
                placeholder="Your answer"
                value={captchaSolution}
                onChange={(e) => setCaptchaSolution(e.target.value)}
                required
                disabled={isCaptchaLoading || !captchaChallenge.id}
              />
              <button
                type="button"
                onClick={fetchCaptchaChallenge}
                className="btn-secondary text-xs p-2"
                disabled={isCaptchaLoading}
              >
                {isCaptchaLoading ? '...' : 'Refresh'}
              </button>
            </div>
            {captchaLoadingError && <p className="text-red-500 text-xs mt-1">{captchaLoadingError}</p>}
          </div>

          <button
            type="submit"
            className="btn-primary w-full mt-4"
            disabled={isLoading || isCaptchaLoading || !captchaChallenge.id}
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
