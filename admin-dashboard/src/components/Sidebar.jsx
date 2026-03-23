import { Link, useLocation } from 'react-router-dom';
import { BarChart3, Users, ShoppingBag, CreditCard, MapPin, Settings, Database } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: BarChart3, label: 'Dashboard' },
    { path: '/providers', icon: Users, label: 'Providers' },
    { path: '/product-providers', icon: ShoppingBag, label: 'Product Providers' },
    { path: '/payments', icon: CreditCard, label: 'Payments' },
    { path: '/locations', icon: MapPin, label: 'Locations' },
    { path: '/categories', icon: Settings, label: 'Categories' },
    { path: '/database', icon: Database, label: 'Database' },
  ];

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-800">Jamii Connect</h1>
        <p className="text-sm text-gray-600">Admin Dashboard</p>
      </div>
      <nav className="mt-6">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100 ${
                isActive ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-700' : ''
              }`}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;