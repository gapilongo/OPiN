import React from 'react';
import { useState } from 'react';
import { 
  Home, 
  Database, 
  Bell, 
  Settings, 
  LogOut,
  Menu,
  X
} from 'lucide-react';

// Sidebar Navigation Component
const Sidebar = ({ isOpen, onClose }) => {
  const navItems = [
    { icon: Home, label: 'Dashboard', href: '/' },
    { icon: Database, label: 'Data Explorer', href: '/explorer' },
    { icon: Bell, label: 'Subscriptions', href: '/subscriptions' },
    { icon: Settings, label: 'Settings', href: '/settings' }
  ];

  return (
    <div 
      className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r transform 
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        transition-transform duration-200 ease-in-out md:translate-x-0
      `}
    >
      <div className="flex h-full flex-col">
        {/* Logo/Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b">
          <span className="text-xl font-bold text-blue-600">OPiN</span>
          <button 
            onClick={onClose}
            className="md:hidden p-2 rounded-md hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map((item) => (
            <a
              key={item.label}
              href={item.href}
              className="flex items-center px-4 py-2 text-gray-600 rounded-md hover:bg-gray-100"
            >
              <item.icon className="w-5 h-5 mr-3" />
              {item.label}
            </a>
          ))}
        </nav>

        {/* Footer/Logout */}
        <div className="p-4 border-t">
          <button 
            onClick={() => {/* handle logout */}}
            className="flex items-center w-full px-4 py-2 text-gray-600 rounded-md hover:bg-gray-100"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

// Header Component
const Header = ({ onMenuClick }) => {
  return (
    <header className="bg-white border-b">
      <div className="flex items-center justify-between h-16 px-4">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-md hover:bg-gray-100"
        >
          <Menu size={20} />
        </button>

        <div className="flex-1 px-4 md:px-0">
          <h2 className="text-xl font-semibold text-gray-800">Dashboard</h2>
        </div>

        <div className="flex items-center space-x-4">
          {/* User Profile */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
              U
            </div>
            <span className="hidden md:block text-sm font-medium">User Name</span>
          </div>
        </div>
      </div>
    </header>
  );
};

// Main Layout Component
const Layout = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
      />
      
      <div className="md:ml-64">
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        
        <main className="p-4 md:p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

// Page Container Component
const PageContainer = ({ title, children }) => {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
      </div>
      {children}
    </div>
  );
};

// Loading Spinner Component
const LoadingSpinner = () => {
  return (
    <div className="flex items-center justify-center p-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
  );
};

// Error Message Component
const ErrorMessage = ({ message }) => {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <div className="flex">
          <div className="flex-shrink-0">
            <AlertCircle className="h-5 w-5 text-red-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              {message}
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  // Empty State Component
  const EmptyState = ({ title, description, actionLabel, onAction }) => {
    return (
      <div className="text-center py-12">
        <div className="rounded-full bg-blue-100 p-3 mx-auto w-fit">
          <Database className="h-6 w-6 text-blue-600" />
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900">{title}</h3>
        <p className="mt-2 text-sm text-gray-500">{description}</p>
        {actionLabel && onAction && (
          <button
            onClick={onAction}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            {actionLabel}
          </button>
        )}
      </div>
    );
  };
  
  // Card Component
  const Card = ({ title, children, actions }) => {
    return (
      <div className="bg-white rounded-lg border shadow-sm">
        <div className="px-4 py-5 sm:p-6">
          {title && (
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">{title}</h3>
              {actions && (
                <div className="flex space-x-2">
                  {actions}
                </div>
              )}
            </div>
          )}
          {children}
        </div>
      </div>
    );
  };
  
  // Stats Card Component
  const StatsCard = ({ title, value, change, icon: Icon }) => {
    const isPositive = change >= 0;
    
    return (
      <div className="bg-white rounded-lg border shadow-sm p-6">
        <div className="flex items-center">
          {Icon && (
            <div className="rounded-full bg-blue-100 p-3">
              <Icon className="h-6 w-6 text-blue-600" />
            </div>
          )}
          <div className="ml-4">
            <h3 className="text-sm font-medium text-gray-500">{title}</h3>
            <div className="mt-1 flex items-baseline">
              <p className="text-2xl font-semibold text-gray-900">{value}</p>
              {change !== undefined && (
                <p className={`ml-2 flex items-baseline text-sm font-semibold ${
                  isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {isPositive ? '+' : ''}{change}%
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  // Breadcrumbs Component
  const Breadcrumbs = ({ items }) => {
    return (
      <nav className="flex" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2">
          {items.map((item, index) => (
            <li key={item.label}>
              <div className="flex items-center">
                {index > 0 && (
                  <svg
                    className="h-5 w-5 text-gray-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
                <a
                  href={item.href}
                  className={`ml-2 text-sm font-medium ${
                    index === items.length - 1
                      ? 'text-gray-500'
                      : 'text-gray-900 hover:text-gray-700'
                  }`}
                >
                  {item.label}
                </a>
              </div>
            </li>
          ))}
        </ol>
      </nav>
    );
  };
  
  // Modal Component
  const Modal = ({ isOpen, onClose, title, children, actions }) => {
    if (!isOpen) return null;
  
    return (
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          {/* Background overlay */}
          <div
            className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            onClick={onClose}
          />
  
          {/* Modal panel */}
          <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <h3 className="text-lg font-medium text-gray-900">{title}</h3>
                  <div className="mt-4">{children}</div>
                </div>
              </div>
            </div>
            {actions && (
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                {actions}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };
  
  export {
    Layout,
    Sidebar,
    Header,
    PageContainer,
    LoadingSpinner,
    ErrorMessage,
    EmptyState,
    Card,
    StatsCard,
    Breadcrumbs,
    Modal
  };
  
  