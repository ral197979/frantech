import { useEffect, useState } from 'react'
import axios from 'axios'

function AuditLogs() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isValid, setIsValid] = useState(null)

  useEffect(() => {
    fetchAuditLogs()
    verifyChain()
  }, [])

  const fetchAuditLogs = async () => {
    try {
      const res = await axios.get('/audit-logs')
      setLogs(res.data)
    } catch (err) {
      setError('Failed to load audit logs')
    } finally {
      setLoading(false)
    }
  }

  const verifyChain = async () => {
    try {
      const res = await axios.get('/audit-logs/verify')
      setIsValid(res.data.valid)
    } catch (err) {
      setIsValid(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="audit-logs">
      <div className="page-header">
        <h1>Audit Logs</h1>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card">
        <h3>Chain Integrity Status</h3>
        <p>
          {isValid === null ? 'Checking...' : isValid ? (
            <span style={{ color: '#28a745' }}>✓ Chain is valid and tamper-proof</span>
          ) : (
            <span style={{ color: '#dc3545' }}>✗ Chain integrity compromised</span>
          )}
        </p>
      </div>

      <div className="card">
        <h2>Audit Log Entries</h2>
        {logs.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Entity</th>
                <th>User ID</th>
                <th>Hash</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.timestamp).toLocaleString()}</td>
                  <td>{log.action}</td>
                  <td>{log.entity_type}</td>
                  <td>{log.user_id ? log.user_id.substring(0, 8) : '-'}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                    {log.hash.substring(0, 16)}...
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No audit logs</p>
        )}
      </div>
    </div>
  )
}

export default AuditLogs
