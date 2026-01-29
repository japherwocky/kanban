<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { api } from '../lib/api.js';
  import Modal from '../lib/Modal.svelte';

  let apiKeys = $state([]);
  let loading = $state(true);
  let showCreateModal = $state(false);
  let newKeyName = $state('');
  let createLoading = $state(false);

  onMount(async () => {
    await loadApiKeys();
  });

  async function loadApiKeys() {
    loading = true;
    try {
      apiKeys = await api.apiKeys.list();
    } catch (e) {
      console.error('Failed to load API keys:', e);
    } finally {
      loading = false;
    }
  }

  async function createKey() {
    if (!newKeyName.trim()) return;
    createLoading = true;
    try {
      const result = await api.apiKeys.create(newKeyName.trim());
      navigate(`/settings/api-keys/created?key=${encodeURIComponent(result.key)}&name=${encodeURIComponent(newKeyName)}`);
    } catch (e) {
      alert('Failed to create API key: ' + e.message);
    } finally {
      createLoading = false;
    }
  }

  async function revokeKey(id) {
    if (!confirm('Are you sure you want to revoke this API key? Any agents using it will lose access.')) {
      return;
    }
    try {
      await api.apiKeys.revoke(id);
      await loadApiKeys();
    } catch (e) {
      alert('Failed to revoke API key: ' + e.message);
    }
  }

  async function activateKey(id) {
    try {
      await api.apiKeys.activate(id);
      await loadApiKeys();
    } catch (e) {
      alert('Failed to activate API key: ' + e.message);
    }
  }

  function formatDate(dateStr) {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
</script>

<div class="api-keys-page">
  <div class="page-header">
    <div>
      <h2>API Keys</h2>
      <p class="description">
        Generate API keys for agents and CI pipelines. Each key has full access to your account.
      </p>
    </div>
    <button class="create-btn" onclick={() => showCreateModal = true}>
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M8 3v10M3 8h10"/>
      </svg>
      Create New Key
    </button>
  </div>

  {#if loading}
    <div class="loading">Loading API keys...</div>
  {:else if apiKeys.length === 0}
    <div class="empty-state">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="8" y="8" width="32" height="32" rx="4"/>
          <path d="M16 16v6a4 4 0 004 4h4"/>
        </svg>
      </div>
      <h3>No API keys yet</h3>
      <p>Create your first API key to authenticate agents and CI pipelines.</p>
      <button class="create-btn" onclick={() => showCreateModal = true}>Create API Key</button>
    </div>
  {:else}
    <div class="keys-list">
      {#each apiKeys as key (key.id)}
        <div class="key-card" class:inactive={!key.is_active}>
          <div class="key-info">
            <div class="key-header">
              <h3 class="key-name">{key.name}</h3>
              <span class="key-prefix">{key.prefix}****</span>
            </div>
            <div class="key-meta">
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="7" cy="7" r="5"/>
                  <path d="M7 4v2l1.5 1.5"/>
                </svg>
                Created {formatDate(key.created_at)}
              </span>
              <span class="meta-item">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="7" cy="7" r="5"/>
                  <path d="M7 4v2l1.5 1.5"/>
                </svg>
                Last used {formatDate(key.last_used_at)}
              </span>
            </div>
          </div>
          <div class="key-actions">
            {#if key.is_active}
              <button class="action-btn revoke" onclick={() => revokeKey(key.id)}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="8" cy="8" r="5.5"/>
                  <path d="M8 5v3l1.5 1.5"/>
                  <path d="M4.5 4.5l2 2"/>
                  <path d="M11.5 4.5l-2 2"/>
                </svg>
                Revoke
              </button>
            {:else}
              <span class="inactive-badge">Revoked</span>
              <button class="action-btn activate" onclick={() => activateKey(key.id)}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M2 8l4 4 8-8"/>
                  <path d="M6 4v4h4"/>
                </svg>
                Reactivate
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if showCreateModal}
  <Modal open={showCreateModal} onClose={() => showCreateModal = false} title="Create API Key">
    {#snippet children()}
      <h2 id="modal-title">Create API Key</h2>
      <form onsubmit={(e) => { e.preventDefault(); createKey(); }}>
        <label for="key-name">Key name</label>
        <input
          id="key-name"
          bind:value={newKeyName}
          placeholder="e.g., Production Agent, CI Pipeline"
          required
          autofocus
        />
        <p class="form-hint">Give this key a descriptive name to identify its purpose later.</p>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" onclick={() => showCreateModal = false}>Cancel</button>
          <button type="submit" class="create-btn" disabled={createLoading}>
            {createLoading ? 'Creating...' : 'Create Key'}
          </button>
        </div>
      </form>
    {/snippet}
  </Modal>
{/if}

<style>
  .api-keys-page {
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .page-header h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.375rem 0;
  }

  .description {
    font-size: 0.9375rem;
    color: var(--color-muted-foreground);
    margin: 0;
    line-height: 1.5;
  }

  .create-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1rem;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
    border-radius: 8px;
    font-size: 0.9375rem;
    font-weight: 500;
    cursor: pointer;
    transition: opacity 0.15s ease;
    white-space: nowrap;
  }

  .create-btn:hover {
    opacity: 0.9;
  }

  .create-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .loading {
    text-align: center;
    padding: 3rem;
    color: var(--color-muted-foreground);
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
  }

  .empty-icon {
    display: inline-flex;
    padding: 1rem;
    background: var(--color-muted);
    border-radius: 12px;
    color: var(--color-muted-foreground);
    margin-bottom: 1.5rem;
  }

  .empty-state h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.5rem 0;
  }

  .empty-state p {
    font-size: 0.9375rem;
    color: var(--color-muted-foreground);
    margin: 0 0 1.5rem 0;
  }

  .keys-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .key-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    transition: all 0.15s ease;
  }

  .key-card:hover {
    border-color: var(--color-primary);
  }

  .key-card.inactive {
    opacity: 0.7;
  }

  .key-info {
    flex: 1;
    min-width: 0;
  }

  .key-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .key-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0;
  }

  .key-prefix {
    padding: 0.25rem 0.5rem;
    background: var(--color-muted);
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--color-muted-foreground);
  }

  .key-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.8125rem;
    color: var(--color-muted-foreground);
  }

  .key-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-left: 1rem;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.5rem 0.875rem;
    background: transparent;
    border: 1px solid var(--color-border);
    border-radius: 6px;
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .action-btn.revoke {
    color: var(--color-error);
    border-color: rgba(239, 68, 68, 0.3);
  }

  .action-btn.revoke:hover {
    background: rgba(239, 68, 68, 0.1);
    border-color: var(--color-error);
  }

  .action-btn.activate {
    color: var(--color-success);
    border-color: rgba(34, 197, 94, 0.3);
  }

  .action-btn.activate:hover {
    background: rgba(34, 197, 94, 0.1);
    border-color: var(--color-success);
  }

  .inactive-badge {
    padding: 0.375rem 0.625rem;
    background: rgba(239, 68, 68, 0.1);
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--color-error);
  }

  #modal-title {
    margin: 0 0 1.25rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
  }

  .form-hint {
    font-size: 0.8125rem;
    color: var(--color-muted-foreground);
    margin: -0.25rem 0 0 0;
    line-height: 1.4;
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .cancel-btn {
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    padding: 0.625rem 1rem;
    border-radius: 8px;
    font-size: 0.9375rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .cancel-btn:hover {
    background: var(--color-muted);
  }

  input {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
    transition: border-color 0.15s ease;
    width: 100%;
    box-sizing: border-box;
  }

  input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }

  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-foreground);
    margin-bottom: 0.375rem;
  }

  @media (max-width: 640px) {
    .page-header {
      flex-direction: column;
      align-items: stretch;
    }

    .key-card {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .key-actions {
      margin-left: 0;
      width: 100%;
    }

    .action-btn {
      flex: 1;
      justify-content: center;
    }
  }
</style>
