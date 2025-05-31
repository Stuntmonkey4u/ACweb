import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../services/api';

const PasswordChangePage = () => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { token, user } = useAuth(); // Get token for the API call and user for username context

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (newPassword !== confirmNewPassword) {
      setError('New passwords do not match.');
      return;
    }
    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters long.');
      return;
    }

    setIsLoading(true);
    try {
      const payload = {
        current_password: currentPassword,
        new_password: newPassword,
      };
      // The /api/auth/users/me/change-password endpoint expects a JSON payload
      // and requires authentication (token).
      const response = await apiClient.post('/auth/users/me/change-password', payload, token);

      setSuccessMessage('Password changed successfully!');
      // Clear form
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');

    } catch (err) {
      setError(err.data?.detail || err.message || 'Password change failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md">
        <h1 className="text-3xl text-center mb-6 font-cinzel text-wotlk-gold">Change Your Password</h1>

        {error && <div className="bg-red-500 text-white p-3 rounded mb-4 text-sm">{error}</div>}
        {successMessage && <div className="bg-green-500 text-white p-3 rounded mb-4 text-sm">{successMessage}</div>}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="currentPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Current Password</label>
            <input
              type="password"
              id="currentPassword"
              className="input-themed"
              placeholder="Enter your current password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>
          <div className="mb-4">
            <label htmlFor="newPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">New Password</label>
            <input
              type="password"
              id="newPassword"
              className="input-themed"
              placeholder="Enter your new password (min. 6 chars)"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength="6"
              disabled={isLoading}
            />
          </div>
          <div className="mb-6">
            <label htmlFor="confirmNewPassword" className="block text-sm font-bold mb-2 text-wotlk-text-dark">Confirm New Password</label>
            <input
              type="password"
              id="confirmNewPassword"
              className="input-themed"
              placeholder="Confirm your new password"
              value={confirmNewPassword}
              onChange={(e) => setConfirmNewPassword(e.target.value)}
              required
              minLength="6"
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            className="btn-primary w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PasswordChangePage;
