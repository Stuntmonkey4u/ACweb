import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Adjusted path

const AdminRoute = ({ children }) => {
    const auth = useAuth();
    const location = useLocation();

    if (auth.isLoading) { // Wait for auth state to load
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="panel-parchment">
                    <p className="text-xl text-wotlk-gold">Loading authentication status...</p>
                </div>
            </div>
        );
    }

    if (!auth.isAuthenticated) {
        // Redirect them to the /login page, but save the current location they were
        // trying to go to when they were redirected. This allows us to send them
        // along to that page after they login, which is a nicer user experience
        // than dropping them off on the home page.
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    if (!auth.user || !auth.user.is_admin) {
        // Redirect them to the dashboard or a general "access denied" page.
        // Pass a message to the dashboard page via location state.
        return <Navigate to="/dashboard" state={{ message: "You do not have permission to access this page." }} replace />;
    }

    return children;
};

export default AdminRoute;
