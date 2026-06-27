import { useEffect, useState } from 'react';
import { fetchUsersPage } from '../api';
import { useAuth } from '../context/AuthContext';

const USERS_PAGE_PATH = '/api/v1/users/?page_size=10';

export default function UserManagementPage() {
  const { user, token } = useAuth();
  const isAdmin = user?.role === 'Admin';
  const [users, setUsers] = useState([]);
  const [nextPath, setNextPath] = useState(null);
  const [prevPath, setPrevPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadUsers(path) {
    setLoading(true);
    setError('');
    try {
      const page = await fetchUsersPage(token, path);
      setUsers(page.items);
      setNextPath(page.nextPath);
      setPrevPath(page.prevPath);
    } catch (err) {
      setError(err.message);
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (isAdmin) {
      loadUsers(USERS_PAGE_PATH);
    } else {
      setLoading(false);
    }
  }, [token, isAdmin]);

  if (!isAdmin) {
    return (
      <div className="card">
        <h1 className="title">User Management</h1>
        <p className="error-text">Clearance level inadequate.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h1 className="title">User Management</h1>
      <p className="subtitle page-subtitle">Registered portal accounts</p>

      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p className="empty-state">Loading users…</p>
      ) : users.length === 0 ? (
        <p className="empty-state">No users found.</p>
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Mobile</th>
                </tr>
              </thead>
              <tbody>
                {users.map((item) => (
                  <tr key={item.id}>
                    <td>{item.email}</td>
                    <td>
                      {[item.first_name, item.last_name].filter(Boolean).join(' ') || '—'}
                    </td>
                    <td>
                      <span
                        className={`badge ${
                          item.role === 'Admin' ? 'badge-admin' : 'badge-standard'
                        }`}
                      >
                        {item.role}
                      </span>
                    </td>
                    <td>{item.mobile || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              className="btn btn-secondary"
              type="button"
              disabled={!prevPath || loading}
              onClick={() => prevPath && loadUsers(prevPath)}
            >
              Previous
            </button>
            <button
              className="btn btn-secondary"
              type="button"
              disabled={!nextPath || loading}
              onClick={() => nextPath && loadUsers(nextPath)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
