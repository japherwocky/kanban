<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import ThemeToggle from '../lib/ThemeToggle.svelte';
  import { api } from '../lib/api.js';
  import Modal from '../lib/Modal.svelte';

  let boards = $state([]);
  let boardsLoading = $state(false);
  let showCreateModal = $state(false);
  let newBoardName = $state('');
  let createLoading = $state(false);

  onMount(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      const currentPath = window.location.pathname;
      localStorage.setItem('redirectPath', currentPath);
      navigate('/login');
      return;
    }
    await loadBoards();
  });

  function logout() {
    localStorage.removeItem('token');
    navigate('/login');
  }

  async function loadBoards() {
    boardsLoading = true;
    try {
      boards = await api.boards.list();
    } catch (e) {
      console.error('Failed to load boards:', e);
    } finally {
      boardsLoading = false;
    }
  }

  async function createBoard() {
    if (!newBoardName.trim()) return;
    createLoading = true;
    try {
      const board = await api.boards.create(newBoardName.trim());
      boards = [...boards, board];
      newBoardName = '';
      showCreateModal = false;
    } catch (e) {
      alert('Failed to create board: ' + e.message);
    } finally {
      createLoading = false;
    }
  }

  async function deleteBoard(id, e) {
    e.stopPropagation();
    if (!confirm('Delete this board?')) return;
    try {
      await api.boards.delete(id);
      boards = boards.filter(b => b.id !== id);
    } catch (e) {
      alert('Failed to delete board: ' + e.message);
    }
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }
</script>

<div class="app">
  <header>
    <h1>Kanban Board</h1>
    <div class="header-actions">
      <ThemeToggle />
      <button class="logout-btn" onclick={logout}>Logout</button>
    </div>
  </header>

  {#if boardsLoading}
    <div class="loading">Loading boards...</div>
  {:else if boards.length === 0}
    <div class="empty-state">
      <p>No boards yet</p>
      <button class="create-btn" onclick={() => showCreateModal = true}>Create your first board</button>
    </div>
  {:else}
    <div class="boards-grid">
      {#each boards as board (board.id)}
        <div class="board-card">
          <button class="board-header" onclick={() => navigate(`/boards/${board.id}`)}>
            <h3>{board.name}</h3>
          </button>
          <button class="delete-btn" onclick={(e) => deleteBoard(board.id, e)} title="Delete board">×</button>
          <div class="board-meta">Created {formatDate(board.created_at)}</div>
        </div>
      {/each}
      <button class="board-card create-card" onclick={() => showCreateModal = true}>
        <span class="plus">+</span>
        <span>New Board</span>
      </button>
    </div>
  {/if}
</div>

{#if showCreateModal}
  <Modal open={showCreateModal} onClose={() => showCreateModal = false} title="Create New Board">
    {#snippet children()}
      <h2 id="modal-title">Create New Board</h2>
      <form onsubmit={(e) => { e.preventDefault(); createBoard(); }}>
        <input
          bind:value={newBoardName}
          placeholder="Board name"
          required
        />
        <div class="modal-actions">
          <button type="button" class="cancel-btn" onclick={() => showCreateModal = false}>Cancel</button>
          <button type="submit" class="create-btn" disabled={createLoading}>
            {createLoading ? 'Creating...' : 'Create Board'}
          </button>
        </div>
      </form>
    {/snippet}
  </Modal>
{/if}

<style>
  .app {
    padding: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
  }

  header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .logout-btn {
    padding: 0.5rem 1rem;
    background: var(--color-muted);
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
  }

  .logout-btn:hover {
    background: var(--color-border);
  }

  .loading {
    text-align: center;
    padding: 3rem;
    color: var(--color-muted-foreground);
  }

  .empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--color-muted-foreground);
  }

  .empty-state p {
    margin-bottom: 1.5rem;
    font-size: 1.125rem;
  }

  .boards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .board-card {
    display: flex;
    flex-direction: column;
    padding: 1.25rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: left;
    position: relative;
  }

  .board-card:hover {
    border-color: var(--color-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .board-header {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .board-header h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0;
  }

  .delete-btn {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    padding: 0.125rem 0.375rem;
    font-size: 1rem;
    line-height: 1;
    background: transparent;
    color: var(--color-muted-foreground);
    border: none;
    opacity: 0;
    transition: opacity 0.15s ease;
  }

  .board-card:hover .delete-btn {
    opacity: 1;
  }

  .delete-btn:hover {
    color: var(--color-destructive);
    background: transparent;
  }

  .board-meta {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
  }

  .create-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    min-height: 120px;
    border: 2px dashed var(--color-border);
    background: transparent;
    color: var(--color-muted-foreground);
  }

  .create-card:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: var(--color-card);
  }

  .create-card .plus {
    font-size: 2rem;
    font-weight: 300;
  }

  .create-btn {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
  }

  .create-btn:hover {
    opacity: 0.9;
  }

  .create-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  #modal-title {
    margin: 0 0 1.25rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
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
  }

  input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary);
  }

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }
</style>
