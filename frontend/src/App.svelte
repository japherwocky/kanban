<script>
  import { onMount } from 'svelte';
  import { theme } from './lib/theme.js';
  import ThemeToggle from './lib/ThemeToggle.svelte';
  import { api } from './lib/api.js';
  import BoardView from './lib/BoardView.svelte';

  let username = '';
  let password = '';
  let token = localStorage.getItem('token');
  let view = 'login';
  let boards = [];
  let boardsLoading = false;
  let showCreateModal = false;
  let newBoardName = '';
  let createLoading = false;
  let selectedBoard = null;

  onMount(() => {
    theme.init();
    if (token && view === 'login') {
      view = 'boards';
      loadBoards();
    }
  });

  async function login() {
    try {
      const res = await fetch('/api/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        view = 'boards';
        await loadBoards();
      } else {
        alert('Login failed');
      }
    } catch (e) {
      alert('Login failed: ' + e.message);
    }
  }

  function logout() {
    token = null;
    localStorage.removeItem('token');
    view = 'login';
    boards = [];
    selectedBoard = null;
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

  function selectBoard(board) {
    selectedBoard = board;
  }

  function goBack() {
    selectedBoard = null;
    loadBoards();
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }
</script>

<main>
  {#if !token}
    <div class="login">
      <h1>Kanban Board</h1>
      <form on:submit|preventDefault={login}>
        <input bind:value={username} placeholder="Username" required />
        <input type="password" bind:value={password} placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
    </div>
  {:else if selectedBoard}
    <BoardView board={selectedBoard} onBack={goBack} />
  {:else}
    <div class="app">
      <header>
        <h1>Kanban Board</h1>
        <div class="header-actions">
          <ThemeToggle />
          <button class="logout-btn" on:click={logout}>Logout</button>
        </div>
      </header>

      {#if boardsLoading}
        <div class="loading">Loading boards...</div>
      {:else if boards.length === 0}
        <div class="empty-state">
          <p>No boards yet</p>
          <button class="create-btn" on:click={() => showCreateModal = true}>Create your first board</button>
        </div>
      {:else}
        <div class="boards-grid">
          {#each boards as board (board.id)}
            <button class="board-card" on:click={() => selectBoard(board)}>
              <div class="board-header">
                <h3>{board.name}</h3>
                <button class="delete-btn" on:click={(e) => deleteBoard(board.id, e)} title="Delete board">×</button>
              </div>
              <div class="board-meta">Created {formatDate(board.created_at)}</div>
            </button>
          {/each}
          <button class="board-card create-card" on:click={() => showCreateModal = true}>
            <span class="plus">+</span>
            <span>New Board</span>
          </button>
        </div>
      {/if}
    </div>

    {#if showCreateModal}
      <div class="modal-overlay" on:click={() => showCreateModal = false}>
        <div class="modal" on:click|stopPropagation>
          <h2>Create New Board</h2>
          <form on:submit|preventDefault={createBoard}>
            <input
              bind:value={newBoardName}
              placeholder="Board name"
              required
              autofocus
            />
            <div class="modal-actions">
              <button type="button" class="cancel-btn" on:click={() => showCreateModal = false}>Cancel</button>
              <button type="submit" class="create-btn" disabled={createLoading}>
                {createLoading ? 'Creating...' : 'Create Board'}
              </button>
            </div>
          </form>
        </div>
      </div>
    {/if}
  {/if}
</main>

<style>
  main {
    min-height: 100vh;
  }

  .login {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 1rem;
    padding: 1rem;
  }

  .login h1 {
    font-size: 1.875rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .login form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
    max-width: 320px;
  }

  input {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
    transition: border-color 0.15s ease;
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

  .login button[type="submit"] {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
  }

  .login button[type="submit"]:hover {
    opacity: 0.9;
  }

  .app {
    padding: 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .board-view {
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

  .back-btn {
    padding: 0.5rem 1rem;
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    margin-right: 1rem;
  }

  .back-btn:hover {
    background: var(--color-muted);
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
  }

  .board-card:hover {
    border-color: var(--color-primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .board-header {
    display: flex;
    justify-content: space-between;
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
    padding: 0.25rem 0.5rem;
    font-size: 1.25rem;
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

  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    z-index: 50;
  }

  .modal {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.5rem;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }

  .modal h2 {
    margin: 0 0 1.25rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
  }

  .modal form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
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
</style>
