import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const DashboardPage = () => {
  const { user, getTokenPayload, isLoading } = useAuth(); // Get user and isLoading from context

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
          <p><strong>Account ID:</strong> {user.id}</p>
          {/* Add more fields from user object if available, e.g., user.expansion */}
          {tokenPayload && tokenPayload.exp && <p><strong>Session Expires:</strong> {new Date(tokenPayload.exp * 1000).toLocaleString()}</p>}
        </div>

        <div className="bg-wotlk-parchment-dark p-4 rounded shadow">
          <h2 className="text-xl font-cinzel text-wotlk-blue mb-3">Quick Actions</h2>
          <ul className="space-y-2">
            <li><Link to="/change-password" className="text-wotlk-blue hover:underline">Change Your Password</Link></li>
            {/* Add more actions like "View Characters" (future), "Setup 2FA" (future) */}
          </ul>
        </div>
      </div>
      {/* Placeholder for future content like character list, activity log etc. */}
    </div>
  );
};
export default DashboardPage;
