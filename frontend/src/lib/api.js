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
  beta: {
    signup: (email) => apiFetch('/api/beta-signup', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),
  },
  admin: {
    status: () => apiFetch('/api/admin/status'),
    users: {
      list: () => apiFetch('/api/admin/users'),
      create: (data) => apiFetch('/api/admin/users', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
      update: (userId, data) => apiFetch(`/api/admin/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
      delete: (userId) => apiFetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
      }),
      resetPassword: (userId, password) => apiFetch(`/api/admin/users/${userId}/reset-password`, {
        method: 'POST',
        body: JSON.stringify({ password }),
      }),
    },
    organizations: {
      list: () => apiFetch('/api/admin/organizations'),
      create: (data) => apiFetch('/api/admin/organizations', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
      update: (orgId, data) => apiFetch(`/api/admin/organizations/${orgId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
      delete: (orgId) => apiFetch(`/api/admin/organizations/${orgId}`, {
        method: 'DELETE',
      }),
    },
    teams: {
      list: () => apiFetch('/api/admin/teams'),
      create: (data) => apiFetch('/api/admin/teams', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
      update: (teamId, data) => apiFetch(`/api/admin/teams/${teamId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
      delete: (teamId) => apiFetch(`/api/admin/teams/${teamId}`, {
        method: 'DELETE',
      }),
      members: {
        list: (teamId) => apiFetch(`/api/admin/teams/${teamId}/members`),
        available: (teamId) => apiFetch(`/api/admin/teams/${teamId}/available-members`),
        add: (teamId, username) => apiFetch(`/api/admin/teams/${teamId}/members`, {
          method: 'POST',
          body: JSON.stringify({ username }),
        }),
        remove: (teamId, userId) => apiFetch(`/api/admin/teams/${teamId}/members/${userId}`, {
          method: 'DELETE',
        }),
      },
    },
    boards: {
      list: () => apiFetch('/api/admin/boards'),
      create: (data) => apiFetch('/api/admin/boards', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
      update: (boardId, data) => apiFetch(`/api/admin/boards/${boardId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
      delete: (boardId) => apiFetch(`/api/admin/boards/${boardId}`, {
        method: 'DELETE',
      }),
    },
  },
  boards: {
    list: () => apiFetch('/api/boards'),
    get: (id) => apiFetch(`/api/boards/${id}`),
    create: (name) => apiFetch('/api/boards', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
    delete: (id) => apiFetch(`/api/boards/${id}`, { method: 'DELETE' }),
    share: (id, teamId, isPublicToOrg = false) => apiFetch(`/api/boards/${id}/share`, {
      method: 'POST',
      body: JSON.stringify({ team_id: teamId, is_public_to_org: isPublicToOrg }),
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
  comments: {
    create: (cardId, content) => apiFetch('/api/comments', {
      method: 'POST',
      body: JSON.stringify({ card_id: cardId, content }),
    }),
    list: (cardId) => apiFetch(`/api/cards/${cardId}/comments`),
    update: (commentId, content) => apiFetch(`/api/comments/${commentId}`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    }),
    delete: (commentId) => apiFetch(`/api/comments/${commentId}`, { method: 'DELETE' }),
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
    invites: {
      list: (orgId) => apiFetch(`/api/organizations/${orgId}/invites`),
      create: (orgId, email) => apiFetch(`/api/organizations/${orgId}/invites`, {
        method: 'POST',
        body: JSON.stringify({ email }),
      }),
      revoke: (orgId, inviteId) => apiFetch(`/api/organizations/${orgId}/invites/${inviteId}`, {
        method: 'DELETE',
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
      remove: (teamId, userId) => apiFetch(`/api/teams/${teamId}/members/${userId}`, {
        method: 'DELETE',
      }),
    },
  },
  apiKeys: {
    list: () => apiFetch('/api/api-keys'),
    create: (name, expiresAt) => apiFetch('/api/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name, expires_at: expiresAt }),
    }),
    revoke: (id) => apiFetch(`/api/api-keys/${id}`, { method: 'DELETE' }),
    activate: (id) => apiFetch(`/api/api-keys/${id}/activate`, { method: 'POST' }),
  },
  invites: {
    get: (token) => apiFetch(`/api/invites/${token}`),
    accept: (token) => apiFetch(`/api/invites/${token}/accept`, { method: 'POST' }),
  },
};
