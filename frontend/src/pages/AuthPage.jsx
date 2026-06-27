import { useState } from 'react';
import { loginUser, signupUser } from '../api';
import { useAuth } from '../context/AuthContext';

const emptySignupForm = {
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirmPassword: '',
  mobile: '',
};

export default function AuthPage() {
  const { login } = useAuth();
  const [mode, setMode] = useState('login');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupForm, setSignupForm] = useState(emptySignupForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function handleSignupChange(field) {
    return (event) => {
      setSignupForm((current) => ({ ...current, [field]: event.target.value }));
    };
  }

  function switchMode(nextMode) {
    setMode(nextMode);
    setError('');
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const data = await loginUser(loginEmail, loginPassword);
        login({ user: data.user, token: data.access });
        return;
      }

      if (signupForm.password !== signupForm.confirmPassword) {
        setError('Passwords do not match.');
        return;
      }

      const data = await signupUser({
        first_name: signupForm.first_name.trim(),
        last_name: signupForm.last_name.trim(),
        email: signupForm.email.trim(),
        password: signupForm.password,
        mobile: signupForm.mobile.trim(),
      });
      login({ user: data.user, token: data.access });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-layout">
      <aside className="auth-hero" aria-hidden="true">
        <div className="auth-hero-stars" />
        <div className="auth-hero-planet" />
        <div className="auth-hero-content">
          <span className="auth-badge">
            <span className="auth-badge-dot" />
            Secure access portal
          </span>
          <h1 className="auth-hero-title">Intergalactic Cargo Portal</h1>
          <div className="auth-hero-copy">
            <p>
              The Intergalactic Cargo Portal is your central hub for tracking and managing
              cargo shipments across all active routes and destinations. Whether you&apos;re
              overseeing manifest uploads or simply checking the status of outbound freight,
              everything you need is in one place — organized, secure, and always up to date.
            </p>
            <p>
              Access is role-based. Admins can upload and manage manifests directly. Standard
              users get a clean, real-time view of all active cargo — no clutter, no confusion.
            </p>
            <p className="auth-hero-tagline">
              Built for the teams keeping the supply chain moving.
            </p>
          </div>
        </div>
      </aside>

      <main className="auth-panel">
        <div className="auth-panel-inner">
          <div className="auth-panel-brand">
            <span className="auth-star-icon" aria-hidden="true">
              ✦
            </span>
            ICP Command
          </div>

          <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'login'}
              className={mode === 'login' ? 'active' : ''}
              onClick={() => switchMode('login')}
            >
              Login
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'signup'}
              className={mode === 'signup' ? 'active' : ''}
              onClick={() => switchMode('signup')}
            >
              Sign up
            </button>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            {mode === 'login' ? (
              <>
                <label className="auth-field">
                  Email
                  <input
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    required
                    placeholder="commander@nebula-corp.com"
                    autoComplete="email"
                  />
                </label>
                <label className="auth-field">
                  Password
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    required
                    minLength={8}
                    autoComplete="current-password"
                  />
                </label>
              </>
            ) : (
              <>
                <div className="auth-form-row">
                  <label className="auth-field">
                    First Name
                    <input
                      type="text"
                      value={signupForm.first_name}
                      onChange={handleSignupChange('first_name')}
                      placeholder="Jane"
                      autoComplete="given-name"
                    />
                  </label>
                  <label className="auth-field">
                    Last Name
                    <input
                      type="text"
                      value={signupForm.last_name}
                      onChange={handleSignupChange('last_name')}
                      placeholder="Gurram"
                      autoComplete="family-name"
                    />
                  </label>
                </div>
                <label className="auth-field">
                  Email
                  <input
                    type="email"
                    value={signupForm.email}
                    onChange={handleSignupChange('email')}
                    required
                    placeholder="commander@nebula-corp.com"
                    autoComplete="email"
                  />
                </label>
                <label className="auth-field">
                  Password
                  <input
                    type="password"
                    value={signupForm.password}
                    onChange={handleSignupChange('password')}
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                </label>
                <label className="auth-field">
                  Re-enter Password
                  <input
                    type="password"
                    value={signupForm.confirmPassword}
                    onChange={handleSignupChange('confirmPassword')}
                    required
                    minLength={8}
                    autoComplete="new-password"
                  />
                </label>
                <label className="auth-field">
                  Mobile
                  <input
                    type="tel"
                    value={signupForm.mobile}
                    onChange={handleSignupChange('mobile')}
                    placeholder="+1 555 0100"
                    autoComplete="tel"
                  />
                </label>
              </>
            )}

            {error && <p className="error-text">{error}</p>}

            <button className="btn btn-access" type="submit" disabled={loading}>
              {loading ? 'Please wait…' : mode === 'login' ? 'Access portal' : 'Create account'}
            </button>
          </form>

          {mode === 'signup' && (
            <p className="auth-hint">
              @nebula-corp.com addresses are provisioned as Admin automatically.
            </p>
          )}

          <p className="auth-legal">
            By continuing you agree to the{' '}
            <a href="#terms">Terms of Service</a> and <a href="#privacy">Privacy Policy</a>.
          </p>
        </div>
      </main>
    </div>
  );
}
