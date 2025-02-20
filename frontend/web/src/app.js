

import React from 'react';
import { AuthProvider, ProtectedRoute } from './hooks/useAuth';

// Pages
import DashboardPage from './pages/dashboard';
import DataExplorerPage from './pages/explorer';
import SubscriptionsPage from './pages/subscriptions';
import SettingsPage from './pages/settings';
import LoginPage from './pages/auth/login';
import RegisterPage from './pages/auth/register';
import ForgotPasswordPage from './pages/auth/forgot-password';
import ResetPasswordPage from './pages/auth/reset-password';
import VerifyEmailPage from './pages/auth/verify-email';
import OAuthCallbackPage from './pages/auth/oauth/callback';

const App = () => {
  // Simple router based on window.location.pathname
  const renderRoute = () => {
    const path = window.location.pathname;

    // Public routes
    if (path === '/login') return <LoginPage />;
    if (path === '/register') return <RegisterPage />;
    if (path === '/forgot-password') return <ForgotPasswordPage />;
    if (path === '/reset-password') return <ResetPasswordPage />;
    if (path === '/verify-email') return <VerifyEmailPage />;
    if (path === '/auth/oauth/callback') return <OAuthCallbackPage />;

    // Protected routes
    if (path === '/') return (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    );
    
    if (path === '/explorer') return (
      <ProtectedRoute>
        <DataExplorerPage />
      </ProtectedRoute>
    );
    
    if (path === '/subscriptions') return (
      <ProtectedRoute>
        <SubscriptionsPage />
      </ProtectedRoute>
    );
    
    if (path === '/settings') return (
      <ProtectedRoute>
        <SettingsPage />
      </ProtectedRoute>
    );

    // 404 Page
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            404 - Page Not Found
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            The page you're looking for doesn't exist.{' '}
            <a href="/" className="font-medium text-blue-600 hover:text-blue-500">
              Go back home
            </a>
          </p>
        </div>
      </div>
    );
  };

  return (
    <AuthProvider>
      {renderRoute()}
    </AuthProvider>
  );
};

export default App;





