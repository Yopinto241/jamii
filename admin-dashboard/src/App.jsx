import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Providers from './pages/Providers';
import ProductProviders from './pages/ProductProviders';
import Payments from './pages/Payments';
import Locations from './pages/Locations';
import Categories from './pages/Categories';
import Database from './pages/Database';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/providers" element={<Providers />} />
            <Route path="/product-providers" element={<ProductProviders />} />
            <Route path="/payments" element={<Payments />} />
            <Route path="/locations" element={<Locations />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/database" element={<Database />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;