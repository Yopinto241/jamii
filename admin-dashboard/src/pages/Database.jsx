import { useState, useEffect } from 'react';
import axios from 'axios';

const Database = () => {
  const [activeTab, setActiveTab] = useState('providers');
  const [data, setData] = useState({});

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = () => {
    const endpoints = [
      'all-service-categories', 'all-services', 'all-product-categories', 'all-products',
      'all-regions', 'all-districts', 'all-wards', 'all-providers', 'all-product-providers',
      'all-agents', 'all-commissions', 'all-payments'
    ];

    endpoints.forEach(endpoint => {
      axios.get(`http://localhost:8000/admin/${endpoint}`)
        .then(res => setData(prev => ({ ...prev, [endpoint]: res.data.data })))
        .catch(err => console.error(`Error fetching ${endpoint}:`, err));
    });
  };

  const tabs = [
    { key: 'all-service-categories', label: 'Service Categories' },
    { key: 'all-services', label: 'Services' },
    { key: 'all-product-categories', label: 'Product Categories' },
    { key: 'all-products', label: 'Products' },
    { key: 'all-regions', label: 'Regions' },
    { key: 'all-districts', label: 'Districts' },
    { key: 'all-wards', label: 'Wards' },
    { key: 'all-providers', label: 'Providers' },
    { key: 'all-product-providers', label: 'Product Providers' },
    { key: 'all-agents', label: 'Agents' },
    { key: 'all-commissions', label: 'Commissions' },
    { key: 'all-payments', label: 'Payments' },
  ];

  const renderTable = (tableData, headers) => (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              {headers.map((header, idx) => (
                <th key={idx} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tableData?.map((row, idx) => (
              <tr key={idx}>
                {row.map((cell, cellIdx) => (
                  <td key={cellIdx} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {cell instanceof Date ? cell.toLocaleDateString() : String(cell)}
                  </td>
                ))}
              </tr>
            )) || []}
          </tbody>
        </table>
      </div>
    </div>
  );

  const getHeaders = (tab) => {
    const headerMap = {
      'all-service-categories': ['ID', 'Name'],
      'all-services': ['ID', 'Name', 'Category'],
      'all-product-categories': ['ID', 'Name'],
      'all-products': ['ID', 'Name', 'Category'],
      'all-regions': ['ID', 'Name'],
      'all-districts': ['ID', 'Name', 'Region'],
      'all-wards': ['ID', 'Name', 'District'],
      'all-providers': ['ID', 'Name', 'Phone', 'Plan', 'Status', 'Expiry', 'Last Served', 'Service', 'Ward', 'District', 'Region'],
      'all-product-providers': ['ID', 'Name', 'Phone', 'Plan', 'Status', 'Expiry', 'Last Served', 'Product', 'Ward', 'District', 'Region'],
      'all-agents': ['ID', 'Name', 'Phone', 'Balance'],
      'all-commissions': ['ID', 'Amount', 'Type', 'Date', 'Agent'],
      'all-payments': ['ID', 'Phone', 'Amount', 'Type', 'Status', 'Date'],
    };
    return headerMap[tab] || [];
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Database Overview</h1>

      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {tabs.map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2 rounded ${
                activeTab === tab.key
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          {tabs.find(t => t.key === activeTab)?.label}
          {data[activeTab] && ` (${data[activeTab].length} records)`}
        </h2>
      </div>

      {renderTable(data[activeTab], getHeaders(activeTab))}

      <div className="mt-6 text-sm text-gray-600">
        <p><strong>Total Records:</strong> {Object.values(data).reduce((sum, arr) => sum + (arr?.length || 0), 0)}</p>
        <p><strong>Last Updated:</strong> {new Date().toLocaleString()}</p>
      </div>
    </div>
  );
};

export default Database;