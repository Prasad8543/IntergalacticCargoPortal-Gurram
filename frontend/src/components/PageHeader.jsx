import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function navClassName({ isActive }) {
  return isActive ? 'site-nav-link site-nav-link-active' : 'site-nav-link';
}

function userInitials(user) {
  const first = user?.first_name?.trim()?.[0] || '';
  const last = user?.last_name?.trim()?.[0] || '';
  if (first || last) {
    return `${first}${last}`.toUpperCase();
  }
  return (user?.email?.slice(0, 2) || 'U').toUpperCase();
}

export default function PageHeader() {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'Admin';

  async function handleLogout() {
    await logout();
  }

  return (
    <header className="site-header">
      <div className="site-header-inner">
        <NavLink to="/dashboard" className="site-brand">
          <span className="brand-mark brand-mark-sm">ICP</span>
          <span className="site-brand-text">Intergalactic Cargo Portal</span>
        </NavLink>

        <nav className="site-nav" aria-label="Main navigation">
          <NavLink to="/dashboard" className={navClassName} end>
            Dashboard
          </NavLink>
          <NavLink to="/about" className={navClassName}>
            About Us
          </NavLink>
          <NavLink to="/users" className={navClassName}>
            User Management
          </NavLink>
        </nav>

        <div className="site-header-user">
          {isAdmin && <span className="badge badge-admin">Admin</span>}
          <span className="user-avatar" title={user.email}>
            {userInitials(user)}
          </span>
          <button
            className="logout-icon-btn"
            type="button"
            onClick={handleLogout}
            aria-label="Logout"
            title="Logout"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
