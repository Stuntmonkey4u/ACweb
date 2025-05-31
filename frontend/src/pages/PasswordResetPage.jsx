import React, { useState, useEffect } from 'react';
import { apiClient } from '../services/api'; // Ensure this path is correct

const PasswordResetPage = () => {
  // States for the request part
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [captchaChallenge, setCaptchaChallenge] = useState({ id: '', question: '' });
  const [captchaSolution, setCaptchaSolution] = useState('');
  const [captchaLoadingError, setCaptchaLoadingError] = useState('');
  const [requestError, setRequestError] = useState('');
  const [requestSuccessMessage, setRequestSuccessMessage] = useState('');
  const [isRequestLoading, setIsRequestLoading] = useState(false);
  const [isCaptchaLoading, setIsCaptchaLoading] = useState(false);

  // States for the confirm part (can be expanded later)
  // const [resetToken, setResetToken] = useState('');
  // const [newPassword, setNewPassword] = useState('');
  // const [confirmNewPassword, setConfirmNewPassword] = useState('');
  // const [confirmError, setConfirmError] = useState('');
  // const [confirmSuccessMessage, setConfirmSuccessMessage] = useState('');
  // const [isConfirmLoading, setIsConfirmLoading] = useState(false);


  const fetchCaptchaChallenge = async () => {
    setIsCaptchaLoading(true);
    setCaptchaLoadingError('');
    try {
      const response = await apiClient.generateCaptcha();
      setCaptchaChallenge({ id: response.id, question: response.question });
    } catch (err) {
      setCaptchaLoadingError('Failed to load CAPTCHA. Please try refreshing.');
      setCaptchaChallenge({ id: '', question: '' });
    } finally {
      setIsCaptchaLoading(false);
    }
  };

  useEffect(() => {
    fetchCaptchaChallenge();
  }, []);

  const handleRequestSubmit = async (e) => {
    e.preventDefault();
    setRequestError('');
    setRequestSuccessMessage('');

    if (!usernameOrEmail) {
      setRequestError('Please enter your username or email.');
      return;
    }
    if (!captchaChallenge.id || !captchaSolution) {
      setRequestError('Please solve the CAPTCHA.');
      return;
    }

    setIsRequestLoading(true);
    try {
      const response = await apiClient.requestPasswordReset(
        usernameOrEmail,
        captchaChallenge.id,
        captchaSolution
      );
      setRequestSuccessMessage(response.message || 'Password reset request submitted. Check your email if an account exists (actual email sending TBD).');
      setUsernameOrEmail(''); // Clear field
      setCaptchaSolution('');
      fetchCaptchaChallenge(); // Fetch new captcha
    } catch (err) {
      const errorDetail = err.data?.detail || err.message || 'Failed to submit password reset request.';
      setRequestError(errorDetail);
      if (errorDetail.toLowerCase().includes("captcha")) {
        fetchCaptchaChallenge();
        setCaptchaSolution('');
      }
    } finally {
      setIsRequestLoading(false);
    }
  };


  // Placeholder for confirm submit logic
  // const handleConfirmSubmit = async (e) => { e.preventDefault(); /* ... */ }

  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md">
        <h1 className="text-3xl text-center mb-6 text-wotlk-gold">Reset Your Password</h1>

        {/* Form for requesting a password reset token/link */}
        <form onSubmit={handleRequestSubmit}>
          <h2 className="text-2xl text-center mb-4 text-wotlk-title">Request Reset</h2>
          {requestError && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{requestError}</div>}
          {captchaLoadingError && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{captchaLoadingError}</div>}
          {requestSuccessMessage && <div className="bg-green-500 text-white p-3 rounded mb-4 text-sm">{requestSuccessMessage}</div>}

          <p className="text-sm mb-4 text-center text-wotlk-text">
            Enter your username or email. If an account matches and CAPTCHA is valid,
            instructions may be provided (Note: actual email sending is TBD on backend).
          </p>
          <div className="mb-4">
            <label htmlFor="usernameOrEmail" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Username or Email</label>
            <input
              type="text"
              id="usernameOrEmail"
              className="input-themed"
              placeholder="Enter your username or email"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              disabled={isRequestLoading || isCaptchaLoading}
            />
          </div>

          {/* CAPTCHA Section */}
          <div className="mb-4 p-3 bg-wotlk-parchment-dark rounded">
            <label htmlFor="captchaRequest" className="block text-sm font-bold mb-2 text-wotlk-blue">
              CAPTCHA: {captchaChallenge.question || "Loading..."}
            </label>
            <div className="flex items-center">
              <input
                type="text"
                id="captchaRequest"
                className="input-themed mr-2 flex-grow"
                placeholder="Your answer"
                value={captchaSolution}
                onChange={(e) => setCaptchaSolution(e.target.value)}
                required
                disabled={isCaptchaLoading || !captchaChallenge.id || isRequestLoading}
              />
              <button
                type="button"
                onClick={fetchCaptchaChallenge}
                className="btn-secondary text-xs p-2"
                disabled={isCaptchaLoading || isRequestLoading}
              >
                {isCaptchaLoading ? '...' : 'Refresh'}
              </button>
            </div>
            {captchaLoadingError && <p className="text-red-500 text-xs mt-1">{captchaLoadingError}</p>}
          </div>

          <button type="submit" className="btn-primary w-full mt-4 mb-4" disabled={isRequestLoading || isCaptchaLoading || !captchaChallenge.id}>
            {isRequestLoading ? 'Submitting...' : 'Request Password Reset'}
          </button>
        </form>

        {/* Separator or link to token confirmation form */}
        <hr className="my-6 border-wotlk-stone-dark" />
        {/* Form for confirming password reset with a token - Placeholder, logic not fully implemented here */}
        <form> {/* onSubmit={handleConfirmSubmit} */}
          <h2 className="text-2xl text-center mb-4 text-wotlk-title">Confirm Reset</h2>
           {/* {confirmError && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{confirmError}</div>}
           {confirmSuccessMessage && <div className="bg-green-500 text-white p-3 rounded mb-4 text-sm">{confirmSuccessMessage}</div>} */}
          <p className="text-sm mb-4 text-center text-wotlk-text-light">
            (This part is a placeholder for when token-based reset is fully implemented.)
          </p>
           <div className="mb-4">
            <label htmlFor="usernameConfirm" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Username</label>
            <input type="text" id="usernameConfirm" className="input-themed" placeholder="Your username" disabled />
          </div>
          <div className="mb-4">
            <label htmlFor="resetToken" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Reset Token</label>
            <input type="text" id="resetToken" className="input-themed" placeholder="Enter the reset token" disabled />
          </div>
          <div className="mb-4">
            <label htmlFor="newPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">New Password</label>
            <input type="password" id="newPassword" className="input-themed" placeholder="Enter your new password" disabled />
          </div>
           <div className="mb-6">
            <label htmlFor="confirmNewPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Confirm New Password</label>
            <input type="password" id="confirmNewPassword" className="input-themed" placeholder="Confirm new password" disabled />
          </div>
          <button type="submit" className="btn-primary w-full" disabled>
            Set New Password (Placeholder)
          </button>
        </form>
      </div>
    </div>
  );
};

export default PasswordResetPage;
