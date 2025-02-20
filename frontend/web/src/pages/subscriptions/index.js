# File: frontend/web/src/pages/subscriptions/index.js

import React, { useState, useEffect } from 'react';
import { 
  Layout, 
  PageContainer, 
  Card, 
  LoadingSpinner,
  ErrorMessage,
  Modal 
} from '../../components/layout';
import { DataSubscriptionManager } from '../../components/data';
import { Bell, Trash2, Edit2 } from 'lucide-react';

const SubscriptionsPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedSubscription, setSelectedSubscription] = useState(null);

  const categories = ['SENSOR', 'BEHAVIORAL', 'ENVIRONMENTAL', 'MARKET', 'AI_TRAINING'];

  useEffect(() => {
    fetchSubscriptions();
  }, []);

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      // In production, this would be an API call
      const response = await fetch('/api/subscriptions');
      const result = await response.json();
      setSubscriptions(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (subscription) => {
    try {
      // In production, this would be an API call
      await fetch('/api/subscriptions', {
        method: 'POST',
        body: JSON.stringify(subscription)
      });
      await fetchSubscriptions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUnsubscribe = async (subscriptionId) => {
    try {
      // In production, this would be an API call
      await fetch(`/api/subscriptions/${subscriptionId}`, {
        method: 'DELETE'
      });
      await fetchSubscriptions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (subscription) => {
    setSelectedSubscription(subscription);
    setIsModalOpen(true);
  };

  const handleUpdate = async (updatedSubscription) => {
    try {
      // In production, this would be an API call
      await fetch(`/api/subscriptions/${updatedSubscription.id}`, {
        method: 'PUT',
        body: JSON.stringify(updatedSubscription)
      });
      await fetchSubscriptions();
      setIsModalOpen(false);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Layout>
      <PageContainer title="Subscription Management">
        {/* New Subscription */}
        <Card title="Create New Subscription">
          <DataSubscriptionManager
            onSubscribe={handleSubscribe}
            categories={categories}
          />
        </Card>

        {/* Active Subscriptions */}
        <div className="mt-6">
          <Card title="Active Subscriptions">
            {loading ? (
              <LoadingSpinner />
            ) : error ? (
              <ErrorMessage message={error} />
            ) : (
              <div className="space-y-4">
                {subscriptions.map(subscription => (
                  <div
                    key={subscription.id}
                    className="bg-white rounded-lg border p-4 flex items-center justify-between"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="rounded-full bg-blue-100 p-2">
                        <Bell className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-lg font-medium">
                          {subscription.category}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {subscription.notificationUrl}
                        </p>
                        <p className="text-sm text-gray-500">
                          Created: {new Date(subscription.createdAt).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(subscription)}
                        className="p-2 text-gray-400 hover:text-blue-600"
                      >
                        <Edit2 className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleUnsubscribe(subscription.id)}
                        className="p-2 text-gray-400 hover:text-red-600"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                ))}

                {subscriptions.length === 0 && (
                  <div className="text-center py-6 text-gray-500">
                    No active subscriptions
                  </div>
                )}
              </div>
            )}
          </Card>
        </div>

        {/* Edit Subscription Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Edit Subscription"
        >
          {selectedSubscription && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleUpdate(selectedSubscription);
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Category
                </label>
                <select
                  value={selectedSubscription.category}
                  onChange={(e) => setSelectedSubscription({
                    ...selectedSubscription,
                    category: e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Notification URL
                </label>
                <input
                  type="url"
                  value={selectedSubscription.notificationUrl}
                  onChange={(e) => setSelectedSubscription({
                    ...selectedSubscription,
                    notificationUrl: e.target.value
                  })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
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
          )}
        </Modal>
      </PageContainer>
    </Layout>
  );
};

export default SubscriptionsPage;