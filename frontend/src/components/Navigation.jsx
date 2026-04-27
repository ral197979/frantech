import { Link, useNavigate } from 'react-router-dom'
import './Navigation.css'

function Navigation({ onLogout }) {
  const navigate = useNavigate()

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h2>Frantech</h2>
      </div>
      <ul className="navbar-menu">
        <li>
          <Link to="/dashboard" className="nav-link">
            Dashboard
          </Link>
        </li>
        <li>
          <Link to="/locations" className="nav-link">
            Locations
          </Link>
        </li>
        <li>
          <Link to="/work-orders" className="nav-link">
            Work Orders
          </Link>
        </li>
        <li>
          <Link to="/tasks" className="nav-link">
            Tasks
          </Link>
        </li>
        <li>
          <Link to="/financials" className="nav-link">
            Financials
          </Link>
        </li>
        <li>
          <Link to="/audit-logs" className="nav-link">
            Audit Logs
          </Link>
        </li>
      </ul>
      <button className="btn-logout" onClick={handleLogout}>
        Logout
      </button>
    </nav>
  )
}

export default Navigation
