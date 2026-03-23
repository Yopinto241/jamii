import { useState, useEffect } from 'react';
import axios from 'axios';

const Locations = () => {
  const [regions, setRegions] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [wards, setWards] = useState([]);
  const [showForm, setShowForm] = useState('');
  const [formData, setFormData] = useState({ name: '', region_id: '', district_id: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = () => {
    axios.get('http://localhost:8000/admin/all-regions').then(res => setRegions(res.data.data));
    axios.get('http://localhost:8000/admin/all-districts').then(res => setDistricts(res.data.data));
    axios.get('http://localhost:8000/admin/all-wards').then(res => setWards(res.data.data));
  };

  const handleSubmit = (e, type) => {
    e.preventDefault();
    const endpoint = type === 'region' ? '/admin/add-region' :
                     type === 'district' ? '/admin/add-district' : '/admin/add-ward';
    axios.post(`http://localhost:8000${endpoint}`, formData).then(() => {
      fetchData();
      setShowForm('');
      setFormData({ name: '', region_id: '', district_id: '' });
    });
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Location Management</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Regions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Regions</h2>
            <button onClick={() => setShowForm('region')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {regions.map(r => <div key={r[0]} className="p-2 bg-gray-50 rounded">{r[1]}</div>)}
          </div>
        </div>

        {/* Districts */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Districts</h2>
            <button onClick={() => setShowForm('district')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {districts.map(d => <div key={d[0]} className="p-2 bg-gray-50 rounded">{d[1]} ({d[2]})</div>)}
          </div>
        </div>

        {/* Wards */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Wards</h2>
            <button onClick={() => setShowForm('ward')} className="bg-blue-500 text-white px-3 py-1 rounded text-sm">Add</button>
          </div>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {wards.map(w => <div key={w[0]} className="p-2 bg-gray-50 rounded">{w[1]} ({w[2]})</div>)}
          </div>
        </div>
      </div>

      {/* Add Forms */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg w-96">
            <h3 className="text-lg font-bold mb-4">Add {showForm.charAt(0).toUpperCase() + showForm.slice(1)}</h3>
            <form onSubmit={(e) => handleSubmit(e, showForm)}>
              <input
                type="text"
                placeholder="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full border rounded px-3 py-2 mb-4"
                required
              />
              {showForm === 'district' && (
                <select
                  value={formData.region_id}
                  onChange={(e) => setFormData({ ...formData, region_id: e.target.value })}
                  className="w-full border rounded px-3 py-2 mb-4"
                  required
                >
                  <option value="">Select Region</option>
                  {regions.map(r => <option key={r[0]} value={r[0]}>{r[1]}</option>)}
                </select>
              )}
              {showForm === 'ward' && (
                <select
                  value={formData.district_id}
                  onChange={(e) => setFormData({ ...formData, district_id: e.target.value })}
                  className="w-full border rounded px-3 py-2 mb-4"
                  required
                >
                  <option value="">Select District</option>
                  {districts.map(d => <option key={d[0]} value={d[0]}>{d[1]}</option>)}
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

export default Locations;