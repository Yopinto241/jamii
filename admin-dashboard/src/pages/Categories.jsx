import { useState, useEffect } from 'react';
import axios from 'axios';

const Categories = () => {
  const [serviceCategories, setServiceCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [productCategories, setProductCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [showForm, setShowForm] = useState('');
  const [formData, setFormData] = useState({ name: '', category_id: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = () => {
    axios.get('http://localhost:8000/admin/all-service-categories').then(res => setServiceCategories(res.data.data));
    axios.get('http://localhost:8000/admin/all-services').then(res => setServices(res.data.data));
    axios.get('http://localhost:8000/admin/all-product-categories').then(res => setProductCategories(res.data.data));
    axios.get('http://localhost:8000/admin/all-products').then(res => setProducts(res.data.data));
  };

  const handleSubmit = (e, type) => {
    e.preventDefault();
    const endpoint = type === 'service-category' ? '/admin/add-service-category' :
                     type === 'service' ? '/admin/add-service' :
                     type === 'product-category' ? '/admin/add-product-category' : '/admin/add-product';
    axios.post(`http://localhost:8000${endpoint}`, formData).then(() => {
      fetchData();
      setShowForm('');
      setFormData({ name: '', category_id: '' });
    });
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Categories & Services Management</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Service Categories & Services */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Service Categories</h2>
              <button onClick={() => setShowForm('service-category')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {serviceCategories.map(c => <div key={c[0]} className="p-2 bg-gray-50 rounded">{c[1]}</div>)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Services</h2>
              <button onClick={() => setShowForm('service')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {services.map(s => <div key={s[0]} className="p-2 bg-gray-50 rounded">{s[1]} ({s[2]})</div>)}
            </div>
          </div>
        </div>

        {/* Product Categories & Products */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Product Categories</h2>
              <button onClick={() => setShowForm('product-category')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {productCategories.map(c => <div key={c[0]} className="p-2 bg-gray-50 rounded">{c[1]}</div>)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Products</h2>
              <button onClick={() => setShowForm('product')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {products.map(p => <div key={p[0]} className="p-2 bg-gray-50 rounded">{p[1]} ({p[2]})</div>)}
            </div>
          </div>
        </div>
      </div>

      {/* Add Forms */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg w-96">
            <h3 className="text-lg font-bold mb-4">Add {showForm.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</h3>
            <form onSubmit={(e) => handleSubmit(e, showForm)}>
              <input
                type="text"
                placeholder="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full border rounded px-3 py-2 mb-4"
                required
              />
              {(showForm === 'service' || showForm === 'product') && (
                <select
                  value={formData.category_id}
                  onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                  className="w-full border rounded px-3 py-2 mb-4"
                  required
                >
                  <option value="">Select Category</option>
                  {(showForm === 'service' ? serviceCategories : productCategories).map(c =>
                    <option key={c[0]} value={c[0]}>{c[1]}</option>
                  )}
                </select>
              )}
              <div className="flex justify-end space-x-2">
                <button type="button" onClick={() => setShowForm('')} className="px-4 py-2 bg-gray-300 rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories;