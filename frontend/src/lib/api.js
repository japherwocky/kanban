const API_BASE = '';

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  boards: {
    list: () => apiFetch('/api/boards'),
    get: (id) => apiFetch(`/api/boards/${id}`),
    create: (name) => apiFetch('/api/boards', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
    delete: (id) => apiFetch(`/api/boards/${id}`, { method: 'DELETE' }),
  },
  columns: {
    create: (boardId, name, position) => apiFetch('/api/columns', {
      method: 'POST',
      body: JSON.stringify({ board_id: boardId, name, position }),
    }),
    delete: (id) => apiFetch(`/api/columns/${id}`, { method: 'DELETE' }),
  },
  cards: {
    create: (columnId, title, position) => apiFetch('/api/cards', {
      method: 'POST',
      body: JSON.stringify({ column_id: columnId, title, position }),
    }),
    update: (id, title, description, position, column) => apiFetch(`/api/cards/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title, description, position, column_id: column }),
    }),
    delete: (id) => apiFetch(`/api/cards/${id}`, { method: 'DELETE' }),
  },
};
