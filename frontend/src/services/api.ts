const API_BASE = '/api';

function getHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function createAnonymousUser() {
  const res = await fetch(`${API_BASE}/auth/anonymous`, {
    method: 'POST',
    headers: getHeaders(),
  });
  return res.json();
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}/users/me`, {
    headers: getHeaders(),
  });
  return res.json();
}

export async function getLeaderboard() {
  const res = await fetch(`${API_BASE}/users/leaderboard`, {
    headers: getHeaders(),
  });
  return res.json();
}

export async function getRooms() {
  const res = await fetch(`${API_BASE}/lobby/rooms`, {
    headers: getHeaders(),
  });
  return res.json();
}

export function getGoogleLoginUrl(): string {
  const token = localStorage.getItem('token');
  return `${API_BASE}/auth/google${token ? `?state=${token}` : ''}`;
}
