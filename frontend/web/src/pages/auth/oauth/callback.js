
import React, { useEffect, useState } from 'react';
import { LoadingSpinner, ErrorMessage } from '../../../components/layout';

const OAuthCallbackPage = () => {
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [error, setError] = useState(null);

  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const provider = state ? JSON.parse(atob(state)).provider : null;

      if (!code || !provider) {
        throw new Error('Invalid OAuth callback');
      }

      const response = await fetch('/api/auth/oauth/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          code,
          provider
        })
      });

      if (!response.ok) {
        throw new Error('Authentication failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.token);
      
      setStatus('success');
      // Redirect to dashboard after short delay
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 1500);
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            {status === 'processing' && (
              <div>
                <LoadingSpinner />
                <h2 className="mt-4 text-xl font-medium text-gray-900">
                  Completing authentication...
                </h2>
                <p className="mt-2 text-sm text-gray-600">
                  Please wait while we process your login.
                </p>
              </div>
            )}

            {status === 'success' && (
              <div>
                <h2 className="text-xl font-medium text-gray-900">
                  Authentication successful
                </h2>
                <p className="mt-2 text-sm text-gray-600">
                  Redirecting to dashboard...
                </p>
              </div>
            )}

            {status === 'error' && (
              <div>
                <h2 className="text-xl font-medium text-gray-900">
                  Authentication failed
                </h2>
                {error && <ErrorMessage message={error} />}
                <div className="mt-4">
                  <a
                    href="/login"
                    className="text-sm font-medium text-blue-600 hover:text-blue-500"
                  >
                    Return to login
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OAuthCallbackPage;

# File: frontend/web/src/pages/auth/oauth/handlers.js

export const initiateOAuth = (provider) => {
  // Generate random state for security
  const state = btoa(JSON.stringify({
    provider,
    nonce: Math.random().toString(36).substring(2)
  }));

  // Store state in session storage for verification
  sessionStorage.setItem('oauthState', state);

  // Get provider config
  const config = getProviderConfig(provider);

  // Build OAuth URL
  const url = new URL(config.authorizationUrl);
  url.searchParams.append('client_id', config.clientId);
  url.searchParams.append('redirect_uri', config.redirectUri);
  url.searchParams.append('scope', config.scope);
  url.searchParams.append('state', state);
  url.searchParams.append('response_type', 'code');

  // Redirect to OAuth provider
  window.location.href = url.toString();
};

const getProviderConfig = (provider) => {
  const configs = {
    google: {
      authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
      clientId: process.env.GOOGLE_CLIENT_ID,
      redirectUri: `${window.location.origin}/auth/oauth/callback`,
      scope: 'openid email profile'
    },
    github: {
      authorizationUrl: 'https://github.com/login/oauth/authorize',
      clientId: process.env