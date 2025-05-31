import React, { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

const UserListPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState({ text: '', type: '' }); // type: 'success' or 'error'
  const { token, user: adminUser } = useAuth(); // Get token and current admin user

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError('');
    setActionMessage({ text: '', type: '' });
    try {
      const data = await apiClient.adminListUsers(token);
      setUsers(data);
    } catch (err) {
      setError(err.data?.detail || err.message || 'Failed to fetch users.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      fetchUsers();
    }
  }, [fetchUsers, token]);

  const handleUserAction = async (actionFunc, userId, successMessage, failureMessage) => {
    setActionMessage({ text: '', type: '' });
    try {
      await actionFunc(userId, token);
      setActionMessage({ text: successMessage, type: 'success' });
      fetchUsers(); // Refresh list
    } catch (err) {
      setActionMessage({ text: `${failureMessage}: ${err.data?.detail || err.message}`, type: 'error' });
    }
  };

  const handleBanUser = (userId) => handleUserAction(apiClient.adminBanUser, userId, 'User banned successfully.', 'Failed to ban user');
  const handleUnbanUser = (userId) => handleUserAction(apiClient.adminUnbanUser, userId, 'User unbanned successfully.', 'Failed to unban user');
  const handlePromoteUser = (userId) => handleUserAction(apiClient.adminPromoteUser, userId, 'User promoted successfully.', 'Failed to promote user');
  const handleDemoteUser = (userId) => handleUserAction(apiClient.adminDemoteUser, userId, 'User demoted successfully.', 'Failed to demote user');

  if (loading) {
    return <div className="panel-parchment text-center p-10"><p className="text-wotlk-gold text-xl">Loading users...</p></div>;
  }

  if (error) {
    return <div className="panel-parchment text-center p-10"><p className="text-red-500">{error}</p></div>;
  }

  return (
    <div className="panel-parchment overflow-x-auto">
      <h1 className="text-3xl font-cinzel text-wotlk-gold mb-6 text-center">Admin - User Management</h1>

      {actionMessage.text && (
        <div className={`p-3 rounded mb-4 text-sm ${actionMessage.type === 'success' ? 'bg-green-700 text-white' : 'bg-red-700 text-white'}`}>
          {actionMessage.text}
        </div>
      )}

      <div className="overflow-x-auto bg-wotlk-parchment-dark shadow-md rounded-lg">
        <table className="min-w-full table-auto text-left text-wotlk-text-light">
          <thead className="bg-wotlk-stone text-wotlk-gold uppercase text-sm leading-normal">
            <tr>
              <th className="py-3 px-6">ID</th>
              <th className="py-3 px-6">Username</th>
              <th className="py-3 px-6">Email</th>
              <th className="py-3 px-6 text-center">Admin</th>
              <th className="py-3 px-6 text-center">Locked</th>
              <th className="py-3 px-6 text-center">Email Verified</th>
              <th className="py-3 px-6 text-center">Actions</th>
            </tr>
          </thead>
          <tbody className="text-sm font-light">
            {users.map((user) => (
              <tr key={user.id} className="border-b border-wotlk-stone hover:bg-wotlk-dark-gold transition-colors duration-150">
                <td className="py-3 px-6">{user.id}</td>
                <td className="py-3 px-6 font-medium">{user.username}</td>
                <td className="py-3 px-6">{user.email}</td>
                <td className="py-3 px-6 text-center">{user.is_admin ? <span className="text-green-400">Yes</span> : <span className="text-red-400">No</span>}</td>
                <td className="py-3 px-6 text-center">{user.locked ? <span className="text-red-400">Yes</span> : <span className="text-green-400">No</span>}</td>
                <td className="py-3 px-6 text-center">{user.email_verified ? <span className="text-green-400">Yes</span> : <span className="text-red-400">No</span>}</td>
                <td className="py-3 px-6 text-center">
                  <div className="flex item-center justify-center space-x-1 md:space-x-2"> {/* Adjusted spacing for smaller buttons */}
                    {user.locked ? (
                      <button
                        onClick={() => handleUnbanUser(user.id)}
                        className="btn-secondary text-green-400 hover:text-green-300 px-2 py-1 text-xs"
                      >
                        Unban
                      </button>
                    ) : (
                      <button
                        onClick={() => handleBanUser(user.id)}
                        className="btn-secondary text-red-400 hover:text-red-300 px-2 py-1 text-xs"
                        disabled={user.id === adminUser?.id || user.is_admin}
                        title={user.id === adminUser?.id ? "Cannot ban self" : (user.is_admin ? "Cannot ban other admins" : "")}
                      >
                        Ban
                      </button>
                    )}
                    {user.is_admin ? (
                      <button
                        onClick={() => handleDemoteUser(user.id)}
                        className="btn-secondary text-yellow-400 hover:text-yellow-300 px-2 py-1 text-xs"
                        disabled={user.id === adminUser?.id}
                        title={user.id === adminUser?.id ? "Cannot demote self" : ""}
                      >
                        Demote
                      </button>
                    ) : (
                      <button
                        onClick={() => handlePromoteUser(user.id)}
                        className="btn-secondary text-blue-400 hover:text-blue-300 px-2 py-1 text-xs"
                        disabled={user.id === adminUser?.id}
                        title={user.id === adminUser?.id ? "Cannot self-promote (already admin or not applicable)" : ""}
                      >
                        Promote
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {users.length === 0 && (
              <tr>
                <td colSpan="7" className="text-center py-4">No users found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserListPage;
