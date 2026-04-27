import { useEffect, useState } from 'react'
import axios from 'axios'

function WorkOrders() {
  const [workOrders, setWorkOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchWorkOrders()
  }, [])

  const fetchWorkOrders = async () => {
    try {
      const res = await axios.get('/work-orders')
      setWorkOrders(res.data)
    } catch (err) {
      setError('Failed to load work orders')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="work-orders">
      <div className="page-header">
        <h1>Work Orders</h1>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card">
        {workOrders.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Description</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {workOrders.map((wo) => (
                <tr key={wo.id}>
                  <td>{wo.title}</td>
                  <td>{wo.description || '-'}</td>
                  <td>{wo.status}</td>
                  <td>{wo.priority}</td>
                  <td>{new Date(wo.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No work orders</p>
        )}
      </div>
    </div>
  )
}

export default WorkOrders
