
import React, { useState, useEffect } from 'react';
import { 
  Layout, 
  PageContainer, 
  Card, 
  LoadingSpinner,
  ErrorMessage 
} from '../../components/layout';
import { 
  DataPoint, 
  DataChart, 
  DataUploader 
} from '../../components/data';
import { Filter, Download, Upload } from 'lucide-react';

const DataExplorerPage = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({
    category: '',
    startDate: '',
    endDate: '',
    quality: ''
  });

  const categories = ['SENSOR', 'BEHAVIORAL', 'ENVIRONMENTAL', 'MARKET', 'AI_TRAINING'];
  const qualityLevels = ['HIGH', 'MEDIUM', 'LOW', 'UNVERIFIED'];

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      // In production, this would be an API call with filters
      const response = await fetch('/api/data?' + new URLSearchParams(filters));
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const handleDataSubmit = async (newData) => {
    try {
      // In production, this would be an API call
      await fetch('/api/data/submit', {
        method: 'POST',
        body: JSON.stringify(newData)
      });
      fetchData(); // Refresh data
    } catch (err) {
      setError(err.message);
    }
  };

  const handleExportData = () => {
    const csvContent = "data:text/csv;charset=utf-8," + 
      data.map(row => Object.values(row).join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "data_export.csv");
    document.body.appendChild(link);
    link.click();
  };

  return (
    <Layout>
      <PageContainer title="Data Explorer">
        {/* Filters */}
        <Card title="Filters">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Category
              </label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Start Date
              </label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                End Date
              </label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Quality
              </label>
              <select
                value={filters.quality}
                onChange={(e) => handleFilterChange('quality', e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="">All Quality Levels</option>
                {qualityLevels.map(quality => (
                  <option key={quality} value={quality}>{quality}</option>
                ))}
              </select>
            </div>
          </div>
        </Card>

        {/* Data Upload */}
        <div className="mt-6">
          <Card title="Submit New Data">
            <DataUploader 
              onSubmit={handleDataSubmit}
              categories={categories}
            />
          </Card>
        </div>

        {/* Data Visualization */}
        <div className="mt-6">
          <Card 
            title="Data Visualization"
            actions={
              <button
                onClick={handleExportData}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </button>
            }
          >
            {loading ? (
              <LoadingSpinner />
            ) : error ? (
              <ErrorMessage message={error} />
            ) : (
              <>
                <DataChart data={data} />
                <div className="mt-6 space-y-4">
                  {data.map(point => (
                    <DataPoint key={point.id} data={point} />
                  ))}
                </div>
              </>
            )}
          </Card>
        </div>
      </PageContainer>
    </Layout>
  );
};

export default DataExplorerPage;