import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Camera } from 'lucide-react';

// DataPoint component for displaying individual data points
const DataPoint = ({ data }) => {
  const qualityColorMap = {
    high: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-red-100 text-red-800'
  };

  return (
    <div className="p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold">{data.category}</h3>
        <span className={`px-2 py-1 rounded text-sm ${qualityColorMap[data.quality]}`}>
          {data.quality}
        </span>
      </div>
      
      <div className="space-y-2">
        <p className="text-gray-600">
          {new Date(data.timestamp).toLocaleString()}
        </p>
        <p className="font-mono text-sm">
          {typeof data.value === 'object' 
            ? JSON.stringify(data.value, null, 2)
            : data.value}
        </p>
        {data.location && (
          <div className="text-sm text-gray-500">
            📍 {data.location.latitude}, {data.location.longitude}
          </div>
        )}
      </div>
    </div>
  );
};

// DataChart component for visualizing data trends
const DataChart = ({ data }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    // Process data for chart
    const processed = data.map(point => ({
      timestamp: new Date(point.timestamp).toLocaleString(),
      value: typeof point.value === 'number' ? point.value : 0
    }));
    setChartData(processed);
  }, [data]);

  return (
    <div className="w-full h-64 mt-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="value" 
            stroke="#3b82f6" 
            activeDot={{ r: 8 }} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

// DataUploader component for submitting new data
const DataUploader = ({ onSubmit, categories }) => {
  const [formData, setFormData] = useState({
    category: '',
    value: '',
    location: {
      latitude: '',
      longitude: ''
    }
  });

  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Validate form data
      if (!formData.category || !formData.value) {
        throw new Error('Please fill in all required fields');
      }

      // Parse value if it's a number
      const parsedValue = !isNaN(formData.value) 
        ? parseFloat(formData.value) 
        : formData.value;

      await onSubmit({
        ...formData,
        value: parsedValue,
        timestamp: new Date().toISOString()
      });

      // Reset form
      setFormData({
        category: '',
        value: '',
        location: {
          latitude: '',
          longitude: ''
        }
      });
      
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="p-4 border rounded-lg">
      {/* ... (previous JSX remains the same) */}
      
      <button
        type="submit"
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Submit Data
      </button>
    </div>
  );
};

// DataSubscriptionManager component for managing data subscriptions
const DataSubscriptionManager = ({ onSubscribe, onUnsubscribe, subscriptions }) => {
  const [newSubscription, setNewSubscription] = useState({
    category: '',
    notificationUrl: '',
    filters: {}
  });

  const handleSubscribe = async (e) => {
    e.preventDefault();
    try {
      await onSubscribe(newSubscription);
      setNewSubscription({
        category: '',
        notificationUrl: '',
        filters: {}
      });
    } catch (error) {
      console.error('Subscription error:', error);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Data Subscriptions</h2>
      
      {/* New Subscription Form */}
      <form onSubmit={handleSubscribe} className="p-4 border rounded-lg space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            Category
          </label>
          <select
            value={newSubscription.category}
            onChange={(e) => setNewSubscription({
              ...newSubscription,
              category: e.target.value
            })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="">Select category...</option>
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
            value={newSubscription.notificationUrl}
            onChange={(e) => setNewSubscription({
              ...newSubscription,
              notificationUrl: e.target.value
            })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="https://your-webhook-url.com"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
        >
          Create Subscription
        </button>
      </form>

      {/* Active Subscriptions List */}
      <div className="mt-4 space-y-2">
        <h3 className="text-lg font-medium">Active Subscriptions</h3>
        {subscriptions.map(sub => (
          <div
            key={sub.id}
            className="p-3 border rounded-lg flex justify-between items-center"
          >
            <div>
              <p className="font-medium">{sub.category}</p>
              <p className="text-sm text-gray-500">{sub.notificationUrl}</p>
            </div>
            <button
              onClick={() => onUnsubscribe(sub.id)}
              className="text-red-600 hover:text-red-800"
            >
              Unsubscribe
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// DataQualityIndicator component for visualizing data quality
const DataQualityIndicator = ({ quality, size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-2 h-2',
    medium: 'w-3 h-3',
    large: 'w-4 h-4'
  };

  const qualityColors = {
    high: 'bg-green-500',
    medium: 'bg-yellow-500',
    low: 'bg-red-500',
    unverified: 'bg-gray-500'
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`rounded-full ${sizeClasses[size]} ${qualityColors[quality]}`} />
      <span className="text-sm capitalize">{quality}</span>
    </div>
  );
};

// DataAnalytics component for displaying data insights
const DataAnalytics = ({ data }) => {
  const [analytics, setAnalytics] = useState({
    totalPoints: 0,
    qualityDistribution: {},
    categoryDistribution: {},
    timeSeriesData: []
  });

  useEffect(() => {
    // Calculate analytics from data
    const calculations = {
      totalPoints: data.length,
      qualityDistribution: data.reduce((acc, point) => {
        acc[point.quality] = (acc[point.quality] || 0) + 1;
        return acc;
      }, {}),
      categoryDistribution: data.reduce((acc, point) => {
        acc[point.category] = (acc[point.category] || 0) + 1;
        return acc;
      }, {}),
      timeSeriesData: data
        .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        .map(point => ({
          timestamp: new Date(point.timestamp).toLocaleString(),
          value: typeof point.value === 'number' ? point.value : 0
        }))
    };

    setAnalytics(calculations);
  }, [data]);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Total Points Card */}
        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <h3 className="text-lg font-medium text-gray-900">Total Data Points</h3>
          <p className="mt-2 text-3xl font-bold text-blue-600">
            {analytics.totalPoints}
          </p>
        </div>

        {/* Quality Distribution */}
        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <h3 className="text-lg font-medium text-gray-900">Quality Distribution</h3>
          <div className="mt-2 space-y-2">
            {Object.entries(analytics.qualityDistribution).map(([quality, count]) => (
              <div key={quality} className="flex justify-between items-center">
                <DataQualityIndicator quality={quality} />
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Category Distribution */}
        <div className="p-4 border rounded-lg bg-white shadow-sm">
          <h3 className="text-lg font-medium text-gray-900">Category Distribution</h3>
          <div className="mt-2 space-y-2">
            {Object.entries(analytics.categoryDistribution).map(([category, count]) => (
              <div key={category} className="flex justify-between items-center">
                <span className="capitalize">{category}</span>
                <span className="font-medium">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Time Series Chart */}
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Data Trend</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={analytics.timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#3b82f6" 
                activeDot={{ r: 8 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Export all components
export {
  DataPoint,
  DataChart,
  DataUploader,
  DataSubscriptionManager,
  DataQualityIndicator,
  DataAnalytics
};