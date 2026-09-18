const API = import.meta.env.VITE_API_URL || '/api';

export async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = localStorage.getItem('rafi_token');
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const res = await fetch(`${API}${path}`, { ...options, headers });
  const raw = await res.text();
  let data = null;
  try { data = raw ? JSON.parse(raw) : null; } catch { data = raw; }
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    if (typeof data === 'string' && data) message = data;
    else if (typeof data?.detail === 'string') message = data.detail;
    else if (Array.isArray(data?.detail)) message = data.detail.map(x => x.msg || JSON.stringify(x)).join(' · ');
    else if (data?.detail) message = JSON.stringify(data.detail);
    const err = new Error(message); err.status = res.status; throw err;
  }
  return data;
}

export async function login(email, password) {
  const data = await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
  localStorage.setItem('rafi_token', data.access_token);
  return data;
}
