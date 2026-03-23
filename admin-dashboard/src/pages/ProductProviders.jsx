import { useState, useEffect } from 'react';
import axios from 'axios';

const ProductProviders = () => {
  const [productProviders, setProductProviders] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    category_id: '',
    product_id: '',
    region_id: '',
    district_id: '',
    ward_id: '',
    plan: 'normal'
  });
  const [categories, setCategories] = useState([]);
  const [products, setProducts] = useState([]);
  const [regions, setRegions] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [wards, setWards] = useState([]);

  useEffect(() => {
    fetchProductProviders();
    fetchCategories();
    fetchRegions();
  }, []);

  const fetchProductProviders = () => {
    axios.get('http://localhost:8000/admin/product-providers')
      .then(response => setProductProviders(response.data.product_providers))
      .catch(error => console.error('Error fetching product providers:', error));
  };

  const fetchCategories = () => {
    axios.get('http://localhost:8000/admin/product-categories')
      .then(response => setCategories(response.data.categories))
      .catch(error => console.error('Error fetching categories:', error));
  };

  const fetchRegions = () => {
    axios.get('http://localhost:8000/admin/regions')
      .then(response => setRegions(response.data.regions))
      .catch(error => console.error('Error fetching regions:', error));
  };

  const handleCategoryChange = (e) => {
    const categoryId = e.target.value;
    setFormData({ ...formData, category_id: categoryId, product_id: '' });
    if (categoryId) {
      axios.get(`http://localhost:8000/admin/products/${categoryId}`)
        .then(response => setProducts(response.data.products))
        .catch(error => console.error('Error fetching products:', error));
    } else {
      setProducts([]);
    }
  };

  const handleRegionChange = (e) => {
    const regionId = e.target.value;
    setFormData({ ...formData, region_id: regionId, district_id: '', ward_id: '' });
    if (regionId) {
      axios.get(`http://localhost:8000/admin/districts/${regionId}`)
        .then(response => setDistricts(response.data.districts))
        .catch(error => console.error('Error fetching districts:', error));
    } else {
      setDistricts([]);
    }
  };

  const handleDistrictChange = (e) => {
    const districtId = e.target.value;
    setFormData({ ...formData, district_id: districtId, ward_id: '' });
    if (districtId) {
      axios.get(`http://localhost:8000/admin/wards/${districtId}`)
        .then(response => setWards(response.data.wards))
        .catch(error => console.error('Error fetching wards:', error));
    } else {
      setWards([]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      name: formData.name,
      phone: formData.phone,
      product_id: formData.product_id,
      ward_id: formData.ward_id,
      plan: formData.plan
    };
    axios.post('http://localhost:8000/admin/product-providers', data)
      .then(() => {
        fetchProductProviders();
        setShowForm(false);
        setFormData({
          name: '',
          phone: '',
          category_id: '',
          product_id: '',
          region_id: '',
          district_id: '',
          ward_id: '',
          plan: 'normal'
        });
      })
      .catch(error => console.error('Error adding product provider:', error));
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this product provider?')) {
      axios.delete(`http://localhost:8000/admin/product-providers/${id}`)
        .then(() => fetchProductProviders())
        .catch(error => console.error('Error deleting product provider:', error));
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Product Providers</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          {showForm ? 'Cancel' : 'Add Product Provider'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Add New Product Provider</h2>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="border rounded px-3 py-2"
              required
            />
            <input
              type="text"
              placeholder="Phone"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="border rounded px-3 py-2"
              required
            />
            <select
              value={formData.category_id}
              onChange={handleCategoryChange}
              className="border rounded px-3 py-2"
              required
            >
              <option value="">Select Category</option>
              {categories.map(cat => (
                <option key={cat[0]} value={cat[0]}>{cat[1]}</option>
              ))}
            </select>
            <select
              value={formData.product_id}
              onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
              className="border rounded px-3 py-2"
              required
              disabled={!formData.category_id}
            >
              <option value="">Select Product</option>
              {products.map(prod => (
                <option key={prod[0]} value={prod[0]}>{prod[1]}</option>
              ))}
            </select>
            <select
              value={formData.region_id}
              onChange={handleRegionChange}
              className="border rounded px-3 py-2"
              required
            >
              <option value="">Select Region</option>
              {regions.map(reg => (
                <option key={reg[0]} value={reg[0]}>{reg[1]}</option>
              ))}
            </select>
            <select
              value={formData.district_id}
              onChange={handleDistrictChange}
              className="border rounded px-3 py-2"
              required
              disabled={!formData.region_id}
            >
              <option value="">Select District</option>
              {districts.map(dist => (
                <option key={dist[0]} value={dist[0]}>{dist[1]}</option>
              ))}
            </select>
            <select
              value={formData.ward_id}
              onChange={(e) => setFormData({ ...formData, ward_id: e.target.value })}
              className="border rounded px-3 py-2"
              required
              disabled={!formData.district_id}
            >
              <option value="">Select Ward</option>
              {wards.map(ward => (
                <option key={ward[0]} value={ward[0]}>{ward[1]}</option>
              ))}
            </select>
            <select
              value={formData.plan}
              onChange={(e) => setFormData({ ...formData, plan: e.target.value })}
              className="border rounded px-3 py-2"
            >
              <option value="normal">Normal</option>
              <option value="premium">Premium</option>
            </select>
            <button type="submit" className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded col-span-2">
              Add Product Provider
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {productProviders.map((provider, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{provider[1]}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{provider[2]}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{provider[3]}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button
                    onClick={() => handleDelete(provider[0])}
                    className="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-xs"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ProductProviders;