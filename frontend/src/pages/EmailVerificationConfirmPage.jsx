import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { apiClient } from '../services/api'; // Ensure this path is correct

const EmailVerificationConfirmPage = () => {
  const [searchParams] = useSearchParams();
  const [message, setMessage] = useState('Verifying your email, please wait...');
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      setMessage('Verification token not found. Please check the link or contact support.');
      setIsError(true);
      return;
    }

    const verifyToken = async () => {
      try {
        // Assuming your api service is updated to include verifyEmail
        await apiClient.post('/auth/verify-email', { token });
        setMessage('Your email has been successfully verified! You can now log in.');
        setIsError(false);
      } catch (error) {
        const errorDetail = error.data?.detail || 'Email verification failed. The link may be invalid or expired.';
        setMessage(errorDetail + ' Please try registering again or contact support if issues persist.');
        setIsError(true);
      }
    };

    verifyToken();
  }, [searchParams]);

  return (
    <div className="flex justify-center items-center py-10">
      <div className="panel-parchment w-full max-w-md text-center">
        <h1 className="text-2xl font-cinzel text-wotlk-gold mb-6">Email Verification</h1>
        <p className={`text-lg ${isError ? 'text-red-500' : 'text-green-500'}`}>
          {message}
        </p>
        {isError ? (
          <p className="mt-4">
            <Link to="/register" className="text-wotlk-blue hover:underline">Register again</Link> or <Link to="/login" className="text-wotlk-blue hover:underline">try logging in</Link>.
          </p>
        ) : (
          <p className="mt-4">
            <Link to="/login" className="btn-primary">Proceed to Login</Link>
          </p>
        )}
      </div>
    </div>
  );
};

export default EmailVerificationConfirmPage;
