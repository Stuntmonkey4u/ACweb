import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../services/api';

const ClientDownloadPage = () => {
  const [downloadInfo, setDownloadInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      setLoading(true);
      apiClient.getClientDownloadInfo(token)
        .then(data => {
          setDownloadInfo(data);
          setLoading(false);
        })
        .catch(err => {
          setError(err.data?.detail || err.message || 'Failed to load download information.');
          setLoading(false);
        });
    } else {
      setError("You must be logged in to view download links."); // Should be caught by ProtectedRoute ideally
      setLoading(false);
    }
  }, [token]);

  if (loading) {
    return (
      <div className="panel-parchment text-center p-10">
        <p className="text-xl text-wotlk-gold animate-pulse">Loading Download Information...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel-parchment text-center p-10">
        <h1 className="text-3xl font-cinzel text-wotlk-gold mb-4">Client Downloads</h1>
        <p className="text-red-500 bg-red-100 p-4 rounded border border-red-500">{error}</p>
      </div>
    );
  }

  if (!downloadInfo || (!downloadInfo.lan_download_url && !downloadInfo.public_download_url)) {
    return (
      <div className="panel-parchment text-center p-10">
        <h1 className="text-3xl font-cinzel text-wotlk-gold mb-4">Client Downloads</h1>
        <p className="text-lg text-wotlk-text-light">Client download links are not currently configured. Please contact an administrator.</p>
      </div>
    );
  }

  return (
    <div className="panel-parchment max-w-2xl mx-auto p-6 md:p-8">
      <h1 className="text-4xl font-cinzel text-wotlk-gold mb-8 text-center">World of Warcraft Client</h1>

      {downloadInfo.lan_available && downloadInfo.lan_download_url && (
        <div className="mb-8 p-6 bg-wotlk-parchment-dark rounded-lg shadow-lg border border-wotlk-blue">
          <h2 className="text-2xl font-cinzel text-wotlk-blue mb-3">LAN Download</h2>
          <p className="text-sm text-wotlk-text-light mb-4">
            Detected you might be on the local network. Use this link for potentially faster downloads.
          </p>
          <a
            href={downloadInfo.lan_download_url}
            className="btn-primary inline-block w-full md:w-auto text-center text-lg py-3 px-6"
            target="_blank" // Open in new tab
            rel="noopener noreferrer" // Security for new tab
          >
            Download from LAN ({new URL(downloadInfo.lan_download_url).pathname.split('/').pop() || 'Client.zip'})
          </a>
        </div>
      )}

      {downloadInfo.public_download_url && (
        <div className="mb-6 p-6 bg-wotlk-parchment-dark rounded-lg shadow-lg border border-wotlk-stone">
          <h2 className="text-2xl font-cinzel text-wotlk-text-dark mb-3">Public Download</h2>
          {!downloadInfo.lan_available && !downloadInfo.lan_download_url && (
             <p className="text-sm text-wotlk-text-light mb-4">
                If you are on the same local network as the server, a LAN download option might provide faster speeds if configured by the admin.
             </p>
          )}
          <a
            href={downloadInfo.public_download_url}
            className="btn-secondary inline-block w-full md:w-auto text-center text-lg py-3 px-6"
            target="_blank"
            rel="noopener noreferrer"
          >
            Download from Internet ({new URL(downloadInfo.public_download_url).pathname.split('/').pop() || 'Client.zip'})
          </a>
        </div>
      )}

      <div className="mt-8 text-center text-xs text-wotlk-text-light opacity-75">
        <p>Ensure you have enough disk space before downloading. Client versions must match the server.</p>
        <p>Contact server administrators for connection details (realmlist).</p>
      </div>
    </div>
  );
};

export default ClientDownloadPage;
