import { useEffect, useState } from 'react'
import axios from 'axios'

function Locations() {
  const [locations, setLocations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({ name: '', address: '', manager_name: '' })
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    fetchLocations()
  }, [])

  const fetchLocations = async () => {
    try {
      const res = await axios.get('/locations')
      setLocations(res.data)
    } catch (err) {
      setError('Failed to load locations')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await axios.post('/locations', formData)
      setFormData({ name: '', address: '', manager_name: '' })
      setShowForm(false)
      fetchLocations()
    } catch (err) {
      setError('Failed to create location')
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="locations">
      <div className="page-header">
        <h1>Locations</h1>
        <div className="actions">
          <button
            className="btn btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : 'Add Location'}
          </button>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {showForm && (
        <div className="card">
          <h2>Create Location</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>Address</label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              />
            </div>
            <div className="form-group">
              <label>Manager Name</label>
              <input
                type="text"
                value={formData.manager_name}
                onChange={(e) => setFormData({ ...formData, manager_name: e.target.value })}
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Create
            </button>
          </form>
        </div>
      )}

      <div className="card">
        <h2>Locations List</h2>
        {locations.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Address</th>
                <th>Manager</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {locations.map((location) => (
                <tr key={location.id}>
                  <td>{location.name}</td>
                  <td>{location.address || '-'}</td>
                  <td>{location.manager_name || '-'}</td>
                  <td>{location.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No locations yet</p>
        )}
      </div>
    </div>
  )
}

export default Locations
