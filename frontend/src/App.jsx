import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import PasswordChangePage from './pages/PasswordChangePage';
import PasswordResetPage from './pages/PasswordResetPage';
import ClientDownloadPage from './pages/ClientDownloadPage';
import EmailVerificationConfirmPage from './pages/EmailVerificationConfirmPage';
import NotFoundPage from './pages/NotFoundPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AdminRoute from './components/auth/AdminRoute'; // Import AdminRoute
import UserListPage from './pages/admin/UserListPage'; // Import Admin User List Page
import { useAuth } from './context/AuthContext';

const Navbar = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-wotlk-stone p-3 shadow-lg border-b-4 border-wotlk-gold">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="font-cinzel text-2xl text-wotlk-gold hover:text-yellow-300 font-bold">
          AzerothCore Manager
        </Link>
        <div className="space-x-4 flex items-center">
          {isAuthenticated ? (
            <>
              <span className="text-wotlk-ice">Welcome, {user ? user.username : 'User'}!</span>
              <Link to="/dashboard" className="text-wotlk-text-light hover:text-wotlk-light-blue">Dashboard</Link>
              {user && user.gmlevel >= 3 && ( // Updated to check gmlevel
                <Link to="/admin/users" className="text-yellow-400 hover:text-yellow-300">Admin Panel</Link>
              )}
              <Link to="/change-password" className="text-wotlk-text-light hover:text-wotlk-light-blue">Change Password</Link>
              <button onClick={handleLogout} className="text-wotlk-text-light hover:text-wotlk-light-blue">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-wotlk-text-light hover:text-wotlk-light-blue">Login</Link>
              <Link to="/register" className="text-wotlk-text-light hover:text-wotlk-light-blue">Register</Link>
            </>
          )}
          <Link to="/downloads" className="text-wotlk-text-light hover:text-wotlk-light-blue">Client Downloads</Link>
        </div>
      </div>
    </nav>
  );
};

const MainLayout = ({ children }) => (
  <div className="min-h-screen bg-wotlk-dark-stone flex flex-col">
    <Navbar />
    <main className="flex-grow container mx-auto p-6">
      {children}
    </main>
    <footer className="bg-wotlk-stone text-center p-4 text-wotlk-text-light text-sm border-t-2 border-wotlk-gold">
      © World of Warcraft Account Manager - WotLK Edition
    </footer>
  </div>
);

// Simple HomePage component
const HomePage = () => (
  <div className="panel-parchment text-center">
    <h1 className="text-4xl mb-6">Welcome to the Realm!</h1>
    <p className="text-lg mb-4">Manage your AzerothCore account with ease.</p>
    <p className="mb-6">Please <Link to="/login" className="text-wotlk-blue hover:underline font-bold">Login</Link> or <Link to="/register" className="text-wotlk-blue hover:underline font-bold">Register</Link> to continue.</p>
  </div>
);

function App() {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/change-password" element={<PasswordChangePage />} />
          </Route>

          {/* Admin Routes */}
          <Route element={<AdminRoute />}>
            <Route path="/admin/users" element={<UserListPage />} />
            {/* Add other admin routes here */}
          </Route>

          {/* Protected Download Page */}
          <Route path="/downloads" element={
            <ProtectedRoute>
              <ClientDownloadPage />
            </ProtectedRoute>
          } />

          <Route path="/reset-password" element={<PasswordResetPage />} /> {/* Assuming public for now */}
          {/* <Route path="/download" element={<ClientDownloadPage />} /> REMOVED OLD PUBLIC ROUTE */}
          <Route path="/verify-email" element={<EmailVerificationConfirmPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}
export default App;
