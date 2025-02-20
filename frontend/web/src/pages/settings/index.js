import React, { useState, useEffect } from 'react';
import { 
  Layout, 
  PageContainer, 
  Card, 
  LoadingSpinner,
  ErrorMessage,
  Modal 
} from '../../components/layout';
import { 
  Key, 
  Bell, 
  Shield, 
  User,
  Copy,
  RefreshCw
} from 'lucide-react';

const SettingsPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    profile: {
      name: '',
      email: '',
      organization: ''
    },
    apiKeys: [],
    notifications: {
      email: true,
      webhook: true,
      failureAlerts: true
    },
    security: {
      twoFactorEnabled: false,
      lastLogin: null,
      activeDevices: []
    }
  });

  const [isApiKeyModalOpen, setIsApiKeyModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      // In production, this would be an API call
      const response = await fetch('/api/settings');
      const result = await response.json();
      setSettings(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateApiKey = async () => {
    try {
      // In production, this would be an API call
      const response = await fetch('/api/settings/api-keys', {
        method: 'POST'
      });
      const newKey = await response.json();
      setSettings(prev => ({
        ...prev,
        apiKeys: [...prev.apiKeys, newKey]
      }));
      setIsApiKeyModalOpen(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRevokeApiKey = async (keyId) => {
    try {
      // In production, this would be an API call
      await fetch(`/api/settings/api-keys/${keyId}`, {
        method: 'DELETE'
      });
      setSettings(prev => ({
        ...prev,
        apiKeys: prev.apiKeys.filter(key => key.id !== keyId)
      }));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpdateProfile = async (profileData) => {
    try {
      // In production, this would be an API call
      await fetch('/api/settings/profile', {
        method: 'PUT',
        body: JSON.stringify(profileData)
      });
      setSettings(prev => ({
        ...prev,
        profile: profileData
      }));
      setIsProfileModalOpen(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleToggleNotification = async (type) => {
    try {
      const newValue = !settings.notifications[type];
      // In production, this would be an API call
      await fetch('/api/settings/notifications', {
        method: 'PUT',
        body: JSON.stringify({ [type]: newValue })
      });
      setSettings(prev => ({
        ...prev,
        notifications: {
          ...prev.notifications,
          [type]: newValue
        }
      }));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Layout>
      <PageContainer title="Settings">
        {loading ? (
          <LoadingSpinner />
        ) : error ? (
          <ErrorMessage message={error} />
        ) : (
          <div className="space-y-6">
            {/* Profile Settings */}
            <Card 
              title="Profile Settings"
              actions={
                <button
                  onClick={() => setIsProfileModalOpen(true)}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                >
                  Edit Profile
                </button>
              }
            >
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <User className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-lg font-medium">{settings.profile.name}</h3>
                    <p className="text-sm text-gray-500">{settings.profile.email}</p>
                    <p className="text-sm text-gray-500">{settings.profile.organization}</p>
                  </div>
                </div>
              </div>
            </Card>

            {/* API Keys */}
            <Card 
              title="API Keys"
              actions={
                <button
                  onClick={() => setIsApiKeyModalOpen(true)}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                >
                  Generate New Key
                </button>
              }
            >
              <div className="space-y-4">
                {settings.apiKeys.map(key => (
                  <div 
                    key={key.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <Key className="h-5 w-5 text-gray-400" />
                      <div>
                        <p className="font-mono text-sm">{key.prefix}...</p>
                        <p className="text-sm text-gray-500">
                          Created: {new Date(key.createdAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => navigator.clipboard.writeText(key.value)}
                        className="p-2 text-gray-400 hover:text-blue-600"
                      >
                        <Copy className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleRevokeApiKey(key.id)}
                        className="p-2 text-gray-400 hover:text-red-600"
                      >
                        <RefreshCw className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Notification Settings */}
            <Card title="Notification Settings">
              <div className="space-y-4">
                {Object.entries(settings.notifications).map(([key, value]) => (
                  <div 
                    key={key}
                    className="flex items-center justify-between py-2"
                  >
                    <div className="flex items-center space-x-2">
                      <Bell className="h-5 w-5 text-gray-400" />
                      <span className="capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={value}
                        onChange={() => handleToggleNotification(key)}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </Card>

            {/* Security Settings */}
            <Card title="Security Settings">
              <div className="space-y-4">
                <div className="flex items-center justify-between py-2">
                  <div className="flex items-center space-x-2">
                    <Shield className="h-5 w-5 text-gray-400" />
                    <span>Two-Factor Authentication</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={settings.security.twoFactorEnabled}
                      onChange={() => {/* Handle 2FA toggle */}}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                <div className="text-sm text-gray-500">
                  Last login: {settings.security.lastLogin ? new Date(settings.security.lastLogin).toLocaleString() : 'Never'}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Generate API Key Modal */}
        <Modal
          isOpen={isApiKeyModalOpen}
          onClose={() => setIsApiKeyModalOpen(false)}
          title="Generate New API Key"
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-500">
              Generate a new API key for accessing the OPiN API. Keep this key secure
              and never share it publicly.
            </p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setIsApiKeyModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateApiKey}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
              >
                Generate Key
              </button>
            </div>
          </div>
        </Modal>

        {/* Edit Profile Modal */}
        <Modal
          isOpen={isProfileModalOpen}
          onClose={() => setIsProfileModalOpen(false)}
          title="Edit Profile"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleUpdateProfile(settings.profile);
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                type="text"
                value={settings.profile.name}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  profile: { ...prev.profile, name: e.target.value }
                }))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Organization
              </label>
              <input
                type="text"
                value={settings.profile.organization}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  profile: { ...prev.profile, organization: e.target.value }
                }))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setIsProfileModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
              >
                Save Changes
              </button>
            </div>
          </form>
        </Modal>
      </PageContainer>
    </Layout>
  );
};

export default SettingsPage;