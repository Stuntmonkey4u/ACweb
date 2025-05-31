import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { apiClient } from '../services/api'; // Import apiClient

const DashboardPage = () => {
  const { user, token, getTokenPayload, isLoading } = useAuth(); // Get user, token, and isLoading

  // State for 2FA management
  const [is2FAEnabledLocally, setIs2FAEnabledLocally] = useState(false); // TODO: Replace with actual status from backend
  const [qrCodeUri, setQrCodeUri] = useState('');
  const [secretKey, setSecretKey] = useState(''); // For backup
  const [totpCode, setTotpCode] = useState('');
  const [twoFaMessage, setTwoFaMessage] = useState({ text: '', type: '' }); // type: 'success' or 'error'
  const [isProcessing2FA, setIsProcessing2FA] = useState(false);

  // TODO: In a real app, fetch current 2FA status (user.is2FAEnabled) from /users/me or a dedicated /2fa/status endpoint
  // useEffect(() => {
  //   if (user && user.is2FAEnabled) { // Assuming user object from context might have this
  //     setIs2FAEnabledLocally(true);
  //   }
  // }, [user]);

  const handleSetup2FA = async () => {
    setIsProcessing2FA(true);
    setTwoFaMessage({ text: '', type: '' });
    try {
      const response = await apiClient.setup2FA(token); // Pass the auth token
      setQrCodeUri(response.qr_code_data_uri);
      setSecretKey(response.secret_key);
      setTwoFaMessage({ text: 'Scan the QR code and save your secret key. Then enter the code to enable.', type: 'success' });
    } catch (error) {
      setTwoFaMessage({ text: error.data?.detail || error.message || 'Failed to start 2FA setup.', type: 'error' });
    } finally {
      setIsProcessing2FA(false);
    }
  };

  const handleEnable2FA = async () => {
    if (!totpCode) {
      setTwoFaMessage({ text: 'Please enter the 6-digit code from your authenticator app.', type: 'error' });
      return;
    }
    setIsProcessing2FA(true);
    setTwoFaMessage({ text: '', type: '' });
    try {
      await apiClient.enable2FA(totpCode, token); // Pass the auth token
      setIs2FAEnabledLocally(true);
      setQrCodeUri(''); // Clear setup details
      setSecretKey('');
      setTotpCode('');
      setTwoFaMessage({ text: '2FA has been successfully enabled!', type: 'success' });
    } catch (error) {
      setTwoFaMessage({ text: error.data?.detail || error.message || 'Failed to enable 2FA. Invalid code or server error.', type: 'error' });
    } finally {
      setIsProcessing2FA(false);
    }
  };

  const handleDisable2FA = async () => {
    if (!totpCode) {
      setTwoFaMessage({ text: 'Please enter the 6-digit code from your authenticator app to disable 2FA.', type: 'error' });
      return;
    }
    setIsProcessing2FA(true);
    setTwoFaMessage({ text: '', type: '' });
    try {
      await apiClient.disable2FA(totpCode, token); // Pass the auth token
      setIs2FAEnabledLocally(false);
      setTotpCode('');
      setTwoFaMessage({ text: '2FA has been successfully disabled.', type: 'success' });
    } catch (error) {
      setTwoFaMessage({ text: error.data?.detail || error.message || 'Failed to disable 2FA. Invalid code or server error.', type: 'error' });
    } finally {
      setIsProcessing2FA(false);
    }
  };

  const handleCancelSetup = () => {
    setQrCodeUri('');
    setSecretKey('');
    setTotpCode('');
    setTwoFaMessage({ text: '', type: '' });
  };


  if (isLoading) {
    return <div className="panel-parchment text-center p-10"><p>Loading user data...</p></div>;
  }

  if (!user) {
    // This case might happen if initial token validation fails or if navigated here somehow without auth
    // ProtectedRoute should typically prevent this, but good to have a fallback.
    return <div className="panel-parchment text-center p-10"><p>Could not load user data. Please <Link to="/login" className="text-wotlk-blue hover:underline">login again</Link>.</p></div>;
  }

  const tokenPayload = getTokenPayload();

  return (
    <div className="panel-parchment">
      <h1 className="text-3xl mb-6 text-wotlk-gold">Welcome, {user.username}!</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-wotlk-parchment-dark p-4 rounded shadow">
          <h2 className="text-xl font-cinzel text-wotlk-blue mb-3">Account Information</h2>
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p>
            <strong>Email Status:</strong>
            {user.email_verified ? (
              <span className="text-green-500"> Verified</span>
            ) : (
              <span className="text-red-500"> Not Verified</span>
            )}
          </p>
          <p><strong>Account ID:</strong> {user.id}</p>
          {/* Add more fields from user object if available, e.g., user.expansion */}
          {tokenPayload && tokenPayload.exp && <p><strong>Session Expires:</strong> {new Date(tokenPayload.exp * 1000).toLocaleString()}</p>}

          {!user.email_verified && (
            <div className="mt-4">
              <p className="text-sm text-yellow-600">Your email address is not yet verified.</p>
              {/* <button className="btn-secondary mt-2 text-xs">Resend verification email</button>
                  Resend functionality to be implemented later.
              */}
            </div>
          )}
        </div>

        <div className="bg-wotlk-parchment-dark p-4 rounded shadow">
          <h2 className="text-xl font-cinzel text-wotlk-blue mb-3">Quick Actions</h2>
          <ul className="space-y-2">
            <li><Link to="/change-password" className="text-wotlk-blue hover:underline">Change Your Password</Link></li>
            {/* 2FA actions will be in their own panel below */}
          </ul>
        </div>
      </div>

      {/* 2FA Management Section */}
      <div className="bg-wotlk-parchment-dark p-4 rounded shadow mt-6">
        <h2 className="text-xl font-cinzel text-wotlk-blue mb-3">Two-Factor Authentication (2FA)</h2>
        {twoFaMessage.text && (
          <div className={`p-3 rounded mb-4 text-sm ${twoFaMessage.type === 'success' ? 'bg-green-500' : 'bg-red-500'} text-white`}>
            {twoFaMessage.text}
          </div>
        )}

        {!is2FAEnabledLocally && !qrCodeUri && (
          <div>
            <p className="mb-2 text-wotlk-text">Enhance your account security by enabling 2FA.</p>
            <button onClick={handleSetup2FA} className="btn-primary" disabled={isProcessing2FA}>
              {isProcessing2FA ? 'Setting up...' : 'Setup 2FA'}
            </button>
          </div>
        )}

        {qrCodeUri && !is2FAEnabledLocally && (
          <div className="space-y-4">
            <p className="text-wotlk-text-dark font-bold">Step 1: Scan QR Code with your Authenticator App</p>
            <img src={qrCodeUri} alt="2FA QR Code" className="mx-auto border-4 border-wotlk-gold rounded" />
            <p className="text-wotlk-text-dark font-bold mt-2">Step 2: Save this Secret Key securely!</p>
            <p className="text-sm text-red-500 bg-gray-800 p-2 rounded inline-block">
              If you lose access to your authenticator, this key is needed to recover your 2FA.
            </p>
            <p className="font-mono bg-gray-700 p-2 rounded text-wotlk-text-light break-all">{secretKey}</p>

            <p className="text-wotlk-text-dark font-bold mt-4">Step 3: Enter Code from App to Enable</p>
            <input
              type="text"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              placeholder="Enter 6-digit code"
              className="input-themed w-full md:w-1/2"
              maxLength="6"
            />
            <button onClick={handleEnable2FA} className="btn-primary" disabled={isProcessing2FA || !totpCode}>
              {isProcessing2FA ? 'Enabling...' : 'Enable 2FA'}
            </button>
            <button onClick={handleCancelSetup} className="btn-secondary ml-2" disabled={isProcessing2FA}>
              Cancel
            </button>
          </div>
        )}

        {is2FAEnabledLocally && (
          <div>
            <p className="text-green-500 mb-2">2FA is currently ACTIVE on your account.</p>
            <p className="text-wotlk-text-dark">Enter code from your authenticator app to disable 2FA:</p>
            <input
              type="text"
              value={totpCode}
              onChange={(e) => setTotpCode(e.target.value)}
              placeholder="Enter 6-digit code"
              className="input-themed w-full md:w-1/2 mt-2"
              maxLength="6"
            />
            <button onClick={handleDisable2FA} className="btn-danger mt-2" disabled={isProcessing2FA || !totpCode}>
              {isProcessing2FA ? 'Disabling...' : 'Disable 2FA'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
