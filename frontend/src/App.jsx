import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import axios from 'axios'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Locations from './pages/Locations'
import WorkOrders from './pages/WorkOrders'
import Tasks from './pages/Tasks'
import Financials from './pages/Financials'
import AuditLogs from './pages/AuditLogs'
import Navigation from './components/Navigation'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [])

  const logout = () => {
    setToken(null)
    localStorage.removeItem('token')
  }

  // Setup axios interceptor
  axios.defaults.baseURL = API_URL
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  if (!token) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login onLogin={setToken} />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    )
  }

  return (
    <Router>
      <div className="app">
        <Navigation onLogout={logout} />
        <main className="main-content">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/locations" element={<Locations />} />
            <Route path="/work-orders" element={<WorkOrders />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/financials" element={<Financials />} />
            <Route path="/audit-logs" element={<AuditLogs />} />
            <Route path="*" element={<Navigate to="/dashboard" />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
