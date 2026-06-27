const API_BASE = import.meta.env.VITE_API_URL || '';

function extractErrorMessage(data) {
  if (!data) return 'Request failed';
  if (typeof data.error === 'string') return data.error;
  if (data.error?.message) {
    const message = data.error.message;
    if (typeof message === 'string') return message;
    if (message?.string) return message.string;
  }
  if (data.error?.password) {
    const field = data.error.password;
    const first = Array.isArray(field) ? field[0] : field;
    if (typeof first === 'string') return first;
    if (first?.message) return first.message;
  }
  if (data.detail) return String(data.detail);
  return 'Request failed';
}

export async function apiRequest(path, { method = 'GET', body, token, formData } = {}) {
  const headers = {};
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let payload = body;
  if (formData) {
    payload = formData;
  } else if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    payload = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: payload,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(extractErrorMessage(data));
  }
  return data;
}

function resolvePaginationPath(link) {
  if (!link || link === 'null' || link === 'None') {
    return null;
  }
  if (link.startsWith('/')) {
    return link;
  }
  try {
    const url = new URL(link, window.location.origin);
    return url.pathname + url.search;
  } catch {
    return null;
  }
}

export function buildCargoPagePath(search = '', page = 1) {
  const params = new URLSearchParams({ page_size: '10' });
  if (page > 1) {
    params.set('page', String(page));
  }
  const query = search.trim();
  if (query) {
    params.set('search', query);
  }
  return `/api/v1/cargo/?${params.toString()}`;
}

export const CARGO_PAGE_PATH = buildCargoPagePath();

export async function fetchCargoPage(token, path = CARGO_PAGE_PATH) {
  const headers = { Authorization: `Bearer ${token}` };
  const response = await fetch(`${API_BASE}${path}`, { headers });
  const data = await response.json().catch(() => []);

  if (!response.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return {
    items: Array.isArray(data) ? data : [],
    nextPath: resolvePaginationPath(response.headers.get('Next')),
    prevPath: resolvePaginationPath(response.headers.get('Prev')),
    pageSize: Number(response.headers.get('Page-Size')) || 10,
    totalCount: Number(response.headers.get('Total-Count')) || 0,
  };
}

export async function fetchCargoStats(token, search = '') {
  const params = new URLSearchParams();
  const query = search.trim();
  if (query) {
    params.set('search', query);
  }
  const suffix = params.toString() ? `?${params.toString()}` : '';
  return apiRequest(`/api/v1/cargo/stats/${suffix}`, { token });
}

export function formatUploadedAt(value) {
  return new Date(value).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  });
}

export function sortCargoForDisplay(cargo) {
  const nonEarth = cargo
    .filter((item) => !item.destination.includes('Earth'))
    .sort((a, b) => b.weight_kg - a.weight_kg);
  const earth = cargo
    .filter((item) => item.destination.includes('Earth'))
    .sort((a, b) => b.weight_kg - a.weight_kg);
  return [...nonEarth, ...earth];
}

export function displayWeight(weightKg, role) {
  if (role === 'Admin') {
    return `${weightKg} KG`;
  }
  const lbs = Math.round(weightKg * 2.20462 * 100) / 100;
  return `${lbs} LBS`;
}

export async function logoutUser(token) {
  return apiRequest('/api/v1/logout/', {
    method: 'POST',
    token,
  });
}

export async function loginUser(email, password) {
  return apiRequest('/api/v1/login/', {
    method: 'POST',
    body: { email, password },
  });
}

export async function signupUser(payload) {
  return apiRequest('/api/v1/signup/', {
    method: 'POST',
    body: payload,
  });
}

export async function fetchUsersPage(token, path = '/api/v1/users/?page_size=10') {
  const headers = { Authorization: `Bearer ${token}` };
  const response = await fetch(`${API_BASE}${path}`, { headers });
  const data = await response.json().catch(() => []);

  if (!response.ok) {
    throw new Error(extractErrorMessage(data));
  }

  return {
    items: Array.isArray(data) ? data : [],
    nextPath: resolvePaginationPath(response.headers.get('Next')),
    prevPath: resolvePaginationPath(response.headers.get('Prev')),
    pageSize: Number(response.headers.get('Page-Size')) || 10,
  };
}

export async function uploadManifest(token, file) {
  const formData = new FormData();
  formData.append('manifest', file);
  return apiRequest('/api/v1/upload/', {
    method: 'POST',
    token,
    formData,
  });
}
