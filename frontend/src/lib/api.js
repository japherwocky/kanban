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
    share: (id, teamId) => apiFetch(`/api/boards/${id}/share`, {
      method: 'POST',
      body: JSON.stringify({ team_id: teamId }),
    }),
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
  organizations: {
    list: () => apiFetch('/api/organizations'),
    get: (id) => apiFetch(`/api/organizations/${id}`),
    create: (name) => apiFetch('/api/organizations', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
    update: (id, name) => apiFetch(`/api/organizations/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    }),
    members: {
      list: (orgId) => apiFetch(`/api/organizations/${orgId}/members`),
      add: (orgId, username) => apiFetch(`/api/organizations/${orgId}/members`, {
        method: 'POST',
        body: JSON.stringify({ username }),
      }),
      updateRole: (orgId, userId, role) => apiFetch(`/api/organizations/${orgId}/members/${userId}`, {
        method: 'PUT',
        body: JSON.stringify({ role }),
      }),
      remove: (orgId, userId) => apiFetch(`/api/organizations/${orgId}/members/${userId}`, {
        method: 'DELETE',
      }),
    },
    teams: {
      list: (orgId) => apiFetch(`/api/organizations/${orgId}/teams`),
      create: (orgId, name) => apiFetch(`/api/organizations/${orgId}/teams`, {
        method: 'POST',
        body: JSON.stringify({ name }),
      }),
    },
  },
  teams: {
    update: (id, name) => apiFetch(`/api/teams/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    }),
    delete: (id) => apiFetch(`/api/teams/${id}`, { method: 'DELETE' }),
    members: {
      list: (teamId) => apiFetch(`/api/teams/${teamId}/members`),
      add: (teamId, username) => apiFetch(`/api/teams/${teamId}/members`, {
        method: 'POST',
        body: JSON.stringify({ username }),
      }),
      updateRole: (teamId, userId, role) => apiFetch(`/api/teams/${teamId}/members/${userId}`, {
        method: 'PUT',
        body: JSON.stringify({ role }),
      }),
      remove: (teamId, userId) => apiFetch(`/api/teams/${teamId}/members/${userId}`, {
        method: 'DELETE',
      }),
    },
  },
};
