<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import Modal from '../lib/Modal.svelte';

  let boards = $state([]);
  let boardsLoading = $state(false);
  let users = $state([]);
  let showCreateBoardModal = $state(false);
  let showEditBoardModal = $state(false);
  let selectedBoard = $state(null);
  let newBoardName = $state('');
  let newBoardOwnerId = $state('');
  let editBoardName = $state('');

  onMount(async () => {
    await Promise.all([loadBoards(), loadUsers()]);
  });

  async function loadBoards() {
    boardsLoading = true;
    try {
      boards = await api.admin.boards.list();
    } catch (e) {
      console.error('Failed to load boards:', e);
      alert('Failed to load boards: ' + e.message);
    } finally {
      boardsLoading = false;
    }
  }

  async function loadUsers() {
    try {
      users = await api.admin.users.list();
    } catch (e) {
      console.error('Failed to load users:', e);
    }
  }

  function getUsernameById(userId) {
    const user = users.find(u => u.id === userId);
    return user?.username || 'Unknown';
  }

  async function createBoard() {
    if (!newBoardName.trim() || !newBoardOwnerId) return;

    try {
      await api.admin.boards.create({
        name: newBoardName.trim(),
        owner_id: parseInt(newBoardOwnerId),
      });
      newBoardName = '';
      newBoardOwnerId = '';
      showCreateBoardModal = false;
      await loadBoards();
    } catch (e) {
      alert('Failed to create board: ' + e.message);
    }
  }

  function openEditBoard(board) {
    selectedBoard = board;
    editBoardName = board.name;
    showEditBoardModal = true;
  }

  async function updateBoard() {
    if (!selectedBoard) return;

    try {
      await api.admin.boards.update(selectedBoard.id, {
        name: editBoardName.trim(),
      });
      showEditBoardModal = false;
      selectedBoard = null;
      await loadBoards();
    } catch (e) {
      alert('Failed to update board: ' + e.message);
    }
  }

  async function deleteBoard(boardId) {
    if (!confirm('Are you sure you want to delete this board? This will delete all columns and cards. This action cannot be undone.')) return;

    try {
      await api.admin.boards.delete(boardId);
      boards = boards.filter(b => b.id !== boardId);
    } catch (e) {
      alert('Failed to delete board: ' + e.message);
    }
  }

  function getSharingInfo(board) {
    if (board.is_public_to_org) {
      return '<span class="badge public-badge">Public to Org</span>';
    }
    if (board.shared_team_name) {
      return `<span class="badge shared-badge">Shared: ${board.shared_team_name}</span>`;
    }
    return '<span class="badge private-badge">Private</span>';
  }

  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  }
</script>

<div class="tab-header">
  <h2>Boards</h2>
  <button class="create-btn" onclick={() => showCreateBoardModal = true}>New Board</button>
</div>

{#if boardsLoading}
  <div class="loading">Loading boards...</div>
{:else if boards.length === 0}
  <div class="empty-state">No boards found</div>
{:else}
  <div class="boards-grid">
    {#each boards as board (board.id)}
      <div class="board-card">
        <div class="board-info">
          <h3>{board.name}</h3>
          <p class="owner-badge">Owner: {board.owner_username}</p>
        </div>
        <div class="board-stats">
          <div class="stat">
            <span class="stat-value">{board.column_count}</span>
            <span class="stat-label">Columns</span>
          </div>
          <div class="stat">
            <span class="stat-value">{board.card_count}</span>
            <span class="stat-label">Cards</span>
          </div>
        </div>
        <div class="board-meta">
          <div class="sharing-info">
            {@html getSharingInfo(board)}
          </div>
          <div class="created-date">
            Created {formatDate(board.created_at)}
          </div>
        </div>
        <div class="board-actions">
          <button class="action-btn" onclick={() => openEditBoard(board)}>Edit</button>
          <button class="action-btn delete" onclick={() => deleteBoard(board.id)}>Delete</button>
        </div>
      </div>
    {/each}
  </div>
{/if}

{#if showCreateBoardModal}
  <Modal open={showCreateBoardModal} onClose={() => showCreateBoardModal = false} title="Create Board">
    {#snippet children()}
      <h2>Create New Board</h2>
      <form onsubmit={(e) => { e.preventDefault(); createBoard(); }}>
        <label>
          Name
          <input
            type="text"
            bind:value={newBoardName}
            placeholder="Enter board name"
            required
          />
        </label>
        <label>
          Owner
          <select bind:value={newBoardOwnerId} required>
            <option value="">Select owner...</option>
            {#each users as user}
              <option value={user.id}>{user.username}</option>
            {/each}
          </select>
        </label>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" onclick={() => showCreateBoardModal = false}>Cancel</button>
          <button type="submit" class="create-btn">Create Board</button>
        </div>
      </form>
    {/snippet}
  </Modal>
{/if}

{#if showEditBoardModal}
  <Modal open={showEditBoardModal} onClose={() => showEditBoardModal = false} title="Edit Board">
    {#snippet children()}
      <h2>Edit Board: {selectedBoard?.name}</h2>
      <form onsubmit={(e) => { e.preventDefault(); updateBoard(); }}>
        <label>
          Name
          <input
            type="text"
            bind:value={editBoardName}
            placeholder="Enter board name"
            required
          />
        </label>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" onclick={() => showEditBoardModal = false}>Cancel</button>
          <button type="submit" class="create-btn">Save Changes</button>
        </div>
      </form>
    {/snippet}
  </Modal>
{/if}

<style>
  .loading, .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: var(--color-muted-foreground);
  }

  .tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .tab-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0;
  }

  .create-btn {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
  }

  .create-btn:hover {
    opacity: 0.9;
  }

  .boards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1rem;
  }

  .board-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .board-info h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.25rem 0;
  }

  .board-info .owner-badge {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    margin: 0;
  }

  .board-stats {
    display: flex;
    gap: 1.5rem;
    margin: 1rem 0;
  }

  .stat {
    display: flex;
    flex-direction: column;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .stat-label {
    font-size: 0.75rem;
    color: var(--color-muted-foreground);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .board-meta {
    margin: 0.75rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .sharing-info {
    display: flex;
    gap: 0.5rem;
  }

  .badge {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 4px;
  }

  .public-badge {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
  }

  .shared-badge {
    background: var(--color-muted);
    color: var(--color-foreground);
  }

  .private-badge {
    background: var(--color-border);
    color: var(--color-muted-foreground);
  }

  .created-date {
    font-size: 0.75rem;
    color: var(--color-muted-foreground);
  }

  .board-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .action-btn {
    flex: 1;
    padding: 0.5rem;
    font-size: 0.875rem;
    background: var(--color-muted);
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    border-radius: 6px;
  }

  .action-btn:hover {
    background: var(--color-border);
  }

  .action-btn.delete {
    color: var(--color-destructive);
    border-color: var(--color-destructive);
  }

  .action-btn.delete:hover {
    background: var(--color-destructive);
    color: var(--color-destructive-foreground);
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-foreground);
  }

  select, input {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
    transition: border-color 0.15s ease;
    width: 100%;
  }

  select:focus, input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary);
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

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }
</style>
