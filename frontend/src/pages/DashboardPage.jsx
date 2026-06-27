import { useEffect, useRef, useState } from 'react';
import {
  buildCargoPagePath,
  displayWeight,
  fetchCargoPage,
  fetchCargoStats,
  formatUploadedAt,
  sortCargoForDisplay,
  uploadManifest,
} from '../api';
import { useAuth } from '../context/AuthContext';

function parsePageNumber(path) {
  try {
    const url = new URL(path, window.location.origin);
    return Number(url.searchParams.get('page')) || 1;
  } catch {
    return 1;
  }
}

export default function DashboardPage() {
  const { user, token } = useAuth();
  const [cargo, setCargo] = useState([]);
  const [stats, setStats] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const fileInputRef = useRef(null);
  const isAdmin = user?.role === 'Admin';

  async function loadDashboard(path) {
    setLoading(true);
    setError('');
    try {
      const [pageData, statsData] = await Promise.all([
        fetchCargoPage(token, path),
        fetchCargoStats(token, search),
      ]);
      setCargo(sortCargoForDisplay(pageData.items));
      setPage(parsePageNumber(path));
      setPageSize(pageData.pageSize);
      setTotalCount(pageData.totalCount);
      setStats(statsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      loadDashboard(buildCargoPagePath(search));
    }, 300);

    return () => window.clearTimeout(timer);
  }, [token, search]);

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setMessage('');
    setError('');

    try {
      const data = await uploadManifest(token, file);
      setMessage(data.message);
      await loadDashboard(buildCargoPagePath(search));
    } catch (err) {
      setError(err.message);
    } finally {
      event.target.value = '';
    }
  }

  const emptyMessage = search.trim()
    ? 'No cargo matches your search.'
    : 'No cargo records yet.';

  const rangeStart = totalCount ? (page - 1) * pageSize + 1 : 0;
  const rangeEnd = totalCount ? Math.min(page * pageSize, totalCount) : cargo.length;
  const totalPages = totalCount ? Math.ceil(totalCount / pageSize) : 0;
  const pageNumbers = totalPages
    ? Array.from({ length: totalPages }, (_, index) => index + 1)
    : [];
  const weightUnit = isAdmin ? 'KG' : 'LBS';
  const totalWeightDisplay = stats
    ? isAdmin
      ? `${stats.total_weight_kg.toLocaleString()} KG`
      : `${Math.round(stats.total_weight_kg * 2.20462).toLocaleString()} LBS`
    : '—';

  return (
    <div className="dashboard">
      <div className="stat-grid">
        <article className="stat-card">
          <span className="stat-label">Total cargo</span>
          <strong className="stat-value">{stats?.total_cargo ?? '—'}</strong>
          <span className="stat-meta">Active manifests</span>
        </article>
        <article className="stat-card">
          <span className="stat-label">Destinations</span>
          <strong className="stat-value">{stats?.destinations ?? '—'}</strong>
          <span className="stat-meta">Active routes</span>
        </article>
        <article className="stat-card">
          <span className="stat-label">Total weight</span>
          <strong className="stat-value stat-value-accent">{totalWeightDisplay}</strong>
          <span className="stat-meta">Across all routes</span>
        </article>
        <article className="stat-card">
          <span className="stat-label">Sector-7</span>
          <strong className="stat-value stat-value-warn">{stats?.sector7_count ?? '—'}</strong>
          <span className="stat-meta">Adjusted records</span>
        </article>
      </div>

      <div className="card manifest-card">
        <div className="manifest-header">
          <div className="manifest-title-wrap">
            <h2 className="manifest-title">Cargo manifest</h2>
            <span className="manifest-unit">Weights in {weightUnit}</span>
          </div>
          <div className="manifest-actions">
            <input
              className="search-input manifest-search"
              type="search"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search cargo, destination…"
              aria-label="Search cargo"
            />
            {isAdmin && (
              <>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt"
                  hidden
                  onChange={handleUpload}
                />
                <button
                  className="btn btn-primary"
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Upload manifest
                </button>
              </>
            )}
          </div>
        </div>

        {message && <p className="success-text">{message}</p>}
        {error && <p className="error-text">{error}</p>}

        {loading ? (
          <p className="empty-state">Loading cargo manifest…</p>
        ) : cargo.length === 0 ? (
          <p className="empty-state">{emptyMessage}</p>
        ) : (
          <>
            <div className="table-wrap">
              <table className="manifest-table">
                <thead>
                  <tr>
                    <th>Cargo ID</th>
                    <th>Destination</th>
                    <th>Weight</th>
                    <th>Uploaded</th>
                  </tr>
                </thead>
                <tbody>
                  {cargo.map((item) => {
                    const isEarth = item.destination.includes('Earth');
                    return (
                      <tr key={item.id} className={isEarth ? 'earth-row' : undefined}>
                        <td>{item.cargo_id}</td>
                        <td>
                          {isEarth ? (
                            <span className="earth-badge">🌍 {item.destination}</span>
                          ) : (
                            item.destination
                          )}
                        </td>
                        <td className="weight-cell">{displayWeight(item.weight_kg, user.role)}</td>
                        <td>{formatUploadedAt(item.created_at)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="table-footer">
              <span className="table-range">
                Showing {rangeStart}-{rangeEnd} of {totalCount} records
              </span>
              <div className="pagination">
                <button
                  className="btn btn-secondary pagination-nav"
                  type="button"
                  disabled={page <= 1 || loading}
                  onClick={() => loadDashboard(buildCargoPagePath(search, page - 1))}
                >
                  Previous
                </button>
                {pageNumbers.map((pageNum) => (
                  <button
                    key={pageNum}
                    className={`btn btn-page ${pageNum === page ? 'btn-page-active' : 'btn-secondary'}`}
                    type="button"
                    disabled={loading}
                    aria-current={pageNum === page ? 'page' : undefined}
                    onClick={() => loadDashboard(buildCargoPagePath(search, pageNum))}
                  >
                    {pageNum}
                  </button>
                ))}
                <button
                  className="btn btn-secondary pagination-nav"
                  type="button"
                  disabled={page >= totalPages || loading}
                  onClick={() => loadDashboard(buildCargoPagePath(search, page + 1))}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
