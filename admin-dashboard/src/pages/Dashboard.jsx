import { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, ShoppingBag, DollarSign, TrendingUp, MapPin, Settings, Database, UserCheck } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [overview, setOverview] = useState({});

  useEffect(() => {
    // Get basic stats
    axios.get('http://localhost:8000/admin/stats')
      .then(response => setStats(response.data))
      .catch(error => console.error('Error fetching stats:', error));

    // Get overview data
    const endpoints = [
      'all-service-categories', 'all-services', 'all-product-categories', 'all-products',
      'all-regions', 'all-districts', 'all-wards', 'all-providers', 'all-product-providers',
      'all-agents', 'all-commissions', 'all-payments'
    ];

    let overviewData = {};
    Promise.all(endpoints.map(ep =>
      axios.get(`http://localhost:8000/admin/${ep}`).then(res => {
        overviewData[ep] = res.data.data.length;
      }).catch(() => { overviewData[ep] = 0; })
    )).then(() => setOverview(overviewData));
  }, []);

  const statCards = [
    { title: 'Service Providers', value: stats.providers || 0, icon: Users, color: 'bg-blue-500' },
    { title: 'Product Sellers', value: stats.sellers || 0, icon: ShoppingBag, color: 'bg-green-500' },
    { title: 'Total Revenue', value: `Tsh ${stats.revenue?.toLocaleString() || 0}`, icon: DollarSign, color: 'bg-yellow-500' },
    { title: 'Active Regions', value: overview['all-regions'] || 0, icon: MapPin, color: 'bg-purple-500' },
    { title: 'Service Categories', value: overview['all-service-categories'] || 0, icon: Settings, color: 'bg-indigo-500' },
    { title: 'Product Categories', value: overview['all-product-categories'] || 0, icon: Database, color: 'bg-pink-500' },
    { title: 'Agents', value: overview['all-agents'] || 0, icon: UserCheck, color: 'bg-teal-500' },
    { title: 'Total Payments', value: overview['all-payments'] || 0, icon: TrendingUp, color: 'bg-orange-500' },
  ];

  const recentActivity = [
    { action: 'New provider registered', time: '2 minutes ago' },
    { action: 'Payment processed', time: '5 minutes ago' },
    { action: 'New category added', time: '10 minutes ago' },
    { action: 'Agent commission paid', time: '15 minutes ago' },
  ];

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className={`${card.color} rounded-full p-3`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{card.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{card.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100">
                <div>
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">System Health</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">USSD Service</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Online</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Payment Gateway</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Online</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Database</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">Healthy</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">SMS Service</span>
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs">Maintenance</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;