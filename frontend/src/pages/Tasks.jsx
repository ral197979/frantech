import { useEffect, useState } from 'react'
import axios from 'axios'

function Tasks() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const res = await axios.get('/tasks')
      setTasks(res.data)
    } catch (err) {
      setError('Failed to load tasks')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading...</div>

  return (
    <div className="tasks">
      <div className="page-header">
        <h1>Tasks</h1>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="card">
        {tasks.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Status</th>
                <th>Due Date</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.id}>
                  <td>{task.title}</td>
                  <td>{task.status}</td>
                  <td>{task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}</td>
                  <td>{new Date(task.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No tasks</p>
        )}
      </div>
    </div>
  )
}

export default Tasks
