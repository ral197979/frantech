import { useEffect, useState } from 'react'
import axios from 'axios'

function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      const res = await axios.get('/dashboard/summary')
      setSummary(res.data)
    } catch (err) {
      setError('Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div className="alert alert-danger">{error}</div>

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      {summary && (
        <div className="dashboard-grid">
          <div className="card stat-card">
            <h3>Total Locations</h3>
            <p className="stat-value">{summary.total_locations}</p>
          </div>

          <div className="card stat-card">
            <h3>Active Issues</h3>
            <p className="stat-value">{summary.active_issues}</p>
          </div>

          <div className="card stat-card">
            <h3>Avg Compliance Score</h3>
            <p className="stat-value">{summary.compliance_score_avg.toFixed(1)}%</p>
          </div>

          <div className="card stat-card">
            <h3>Monthly Revenue</h3>
            <p className="stat-value">${summary.monthly_revenue.toFixed(2)}</p>
          </div>

          <div className="card stat-card">
            <h3>Monthly Expenses</h3>
            <p className="stat-value">${summary.monthly_expenses.toFixed(2)}</p>
          </div>

          <div className="card stat-card">
            <h3>Net Income</h3>
            <p className="stat-value">
              ${(summary.monthly_revenue - summary.monthly_expenses).toFixed(2)}
            </p>
          </div>
        </div>
      )}

      <div className="card">
        <h2>Flagged Locations</h2>
        {summary?.flagged_locations && summary.flagged_locations.length > 0 ? (
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
              {summary.flagged_locations.map((location) => (
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
          <p>No flagged locations</p>
        )}
      </div>
    </div>
  )
}

export default Dashboard
