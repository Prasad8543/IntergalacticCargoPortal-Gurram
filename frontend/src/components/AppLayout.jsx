import { Outlet } from 'react-router-dom';
import PageHeader from './PageHeader';

export default function AppLayout() {
  return (
    <div className="site-layout">
      <PageHeader />
      <main className="site-main">
        <div className="app-shell">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
