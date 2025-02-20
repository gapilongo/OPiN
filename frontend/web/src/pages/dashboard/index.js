import React, { useState, useEffect } from 'react';
import { 
  Database, 
  TrendingUp, 
  Users, 
  AlertCircle 
} from 'lucide-react';

import {
  Layout,
  PageContainer,
  LoadingSpinner,
  ErrorMessage,
  StatsCard,
  Card
} from '../components/layout';

import {
  DataChart,
  DataQualityIndicator,
  DataAnalytics
} from '../components/data';

const DashboardPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    stats: {
      totalDataPoints: 0,
      activeSubscriptions: 0,
      dataQuality: 0,
      trend: 0
    },
    recentData: [],
    analytics: null
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // In production, this would be an API call
      const response = await fetch('/api/dashboard');
      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;

  return (
    <Layout>
      <PageContainer title="Dashboard">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Data Points"
            value={dashboardData.stats.totalDataPoints}
            change={dashboardData.stats.trend}
            icon={Database}
          />
          <StatsCard
            title="Active Subscriptions"
            value={dashboardData.stats.activeSubscriptions}
            icon={Users}
          />
          <StatsCard
            title="Data Quality Score"
            value={`${dashboardData.stats.dataQuality}%`}
            icon={AlertCircle}
          />
          <StatsCard
            title="24h Trend"
            value={`${dashboardData.stats.trend}%`}
            icon={TrendingUp}
          />
        </div>

        {/* Recent Data Chart */}
        <div className="mt-6">
          <Card title="Recent Data Trend">
            <DataChart data={dashboardData.recentData} />
          </Card>
        </div>

        {/* Analytics Section */}
        <div className="mt-6">
          <Card title="Data Analytics">
            <DataAnalytics data={dashboardData.recentData} />
          </Card>
        </div>

        {/* Recent Activity */}
        <div className="mt-6">
          <Card title="Recent Activity">
            <div className="space-y-4">
              {dashboardData.recentData.slice(0, 5).map((activity) => (
                <div 
                  key={activity.id}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <div className="flex items-center space-x-4">
                    <div className="rounded-full bg-blue-100 p-2">
                      <Database className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {activity.category}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <DataQualityIndicator quality={activity.quality} />
                </div>
              ))}
            </div>
          </Card>
        </div>
      </PageContainer>
    </Layout>
  );
};

export default DashboardPage;