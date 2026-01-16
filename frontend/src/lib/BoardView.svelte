<script>
  import { onMount } from 'svelte';
  import { api } from './api.js';
  import Modal from './Modal.svelte';
  import ShareModal from './ShareModal.svelte';
  import Comments from './Comments.svelte';

  let { board, onBack, availableTeams = [], onShare } = $props();

  let columns = $state([]);
  let loading = $state(false);
  let showCreateCardModal = $state(false);
  let selectedColumnId = $state(null);
  let newCardTitle = $state('');
  let createLoading = $state(false);
  let draggedCard = $state(null);
  let showEditCardModal = $state(false);
  let editingCard = $state(null);
  let editTitle = $state('');
  let editDescription = $state('');
  let editLoading = $state(false);
  let showCreateColumnModal = $state(false);
  let newColumnName = $state('');
  let createColumnLoading = $state(false);
  let showShareModal = $state(false);

  // Get current user's id from token
  let currentUserId = $state(null);
  try {
    const token = localStorage.getItem('token');
    if (token) {
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      currentUserId = tokenData.sub;
    }
  } catch (e) {
    console.error('Failed to decode token:', e);
  }

  function isBoardOwner() {
    return board?.owner_id && String(board.owner_id) === String(currentUserId);
  }

  async function loadBoard() {
    loading = true;
    try {
      const data = await api.boards.get(board.id);
      columns = data.columns || [];
    } catch (e) {
      console.error('Failed to load board:', e);
    } finally {
      loading = false;
    }
  }

  async function createCard() {
    if (!newCardTitle.trim() || !selectedColumnId) return;
    createLoading = true;
    try {
      const card = await api.cards.create(selectedColumnId, newCardTitle.trim(), 0);
      columns = columns.map(col => {
        if (col.id === selectedColumnId) {
          return { ...col, cards: [card, ...col.cards] };
        }
        return col;
      });
      newCardTitle = '';
      showCreateCardModal = false;
    } catch (e) {
      alert('Failed to create card: ' + e.message);
    } finally {
      createLoading = false;
    }
  }

  async function deleteCard(columnId, cardId, e) {
    e.stopPropagation();
    if (!confirm('Delete this card?')) return;
    try {
      await api.cards.delete(cardId);
      columns = columns.map(col => {
        if (col.id === columnId) {
          return { ...col, cards: col.cards.filter(c => c.id !== cardId) };
        }
        return col;
      });
    } catch (e) {
      alert('Failed to delete card: ' + e.message);
    }
  }

  function openCreateCard(columnId) {
    selectedColumnId = columnId;
    newCardTitle = '';
    showCreateCardModal = true;
  }

  function openEditCard(card) {
    editingCard = card;
    editTitle = card.title || '';
    editDescription = card.description || '';
    showEditCardModal = true;
  }

  async function saveCard() {
    if (!editTitle.trim() || !editingCard) return;
    editLoading = true;
    try {
      await api.cards.update(editingCard.id, editTitle.trim(), editDescription.trim() || null, null, null);
      columns = columns.map(col => ({
        ...col,
        cards: col.cards.map(c =>
          c.id === editingCard.id
            ? { ...c, title: editTitle.trim(), description: editDescription.trim() }
            : c
        )
      }));
      showEditCardModal = false;
      editingCard = null;
    } catch (e) {
      alert('Failed to update card: ' + e.message);
    } finally {
      editLoading = false;
    }
  }

  function handleCommentsUpdate(cardId, updatedComments) {
    // Update the comments in the local state
    columns = columns.map(col => ({
      ...col,
      cards: col.cards.map(card =>
        card.id === cardId
          ? { ...card, comments: updatedComments }
          : card
      )
    }));
    
    // Also update the editing card if it's the same card
    if (editingCard && editingCard.id === cardId) {
      editingCard = { ...editingCard, comments: updatedComments };
    }
  }

  async function createColumn() {
    if (!newColumnName.trim()) return;
    createColumnLoading = true;
    try {
      const column = await api.columns.create(board.id, newColumnName.trim(), columns.length);
      columns = [...columns, { ...column, cards: [] }];
      newColumnName = '';
      showCreateColumnModal = false;
    } catch (e) {
      alert('Failed to create column: ' + e.message);
    } finally {
      createColumnLoading = false;
    }
  }

  async function deleteColumn(columnId, columnName) {
    if (!confirm(`Delete column "${columnName}" and all its cards?`)) return;
    try {
      await api.columns.delete(columnId);
      columns = columns.filter(col => col.id !== columnId);
    } catch (e) {
      alert('Failed to delete column: ' + e.message);
    }
  }

  function handleDndConsider(columnId, e) {
    const { items } = e.detail;
    columns = columns.map(col => {
      if (col.id === columnId) {
        return { ...col, cards: items };
      }
      return col;
    });
  }

  async function handleDndFinalize(columnId, e) {
    const { items } = e.detail;
    columns = columns.map(col => {
      if (col.id === columnId) {
        return { ...col, cards: items };
      }
      return col;
    });
    if (draggedCard && draggedCard.columnId !== columnId) {
      try {
        await api.cards.update(draggedCard.id, draggedCard.title, null, 0, columnId);
      } catch (e) {
        console.error('Failed to move card:', e);
        loadBoard();
      }
    }
    draggedCard = null;
  }

  function handleDragStart(e, card, columnId) {
    draggedCard = { ...card, columnId };
  }

  // Sync columns with board changes
  $effect(() => {
    if (board?.columns) {
      columns = [...board.columns];
    }
  });

  function formatDate(dateStr) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  }
</script>

<div class="board-view">
  <header>
    <div class="header-left">
      <button class="back-btn" onclick={onBack}>
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M12 4L6 10L12 16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Back
      </button>
      <h1>{board.name}</h1>
    </div>
    <div class="header-actions">
      {#if isBoardOwner()}
        {#if availableTeams.length > 0}
          <button class="share-btn" onclick={() => showShareModal = true}>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 3C8.44772 3 8 3.44772 8 4V8H4C3.44772 8 3 8.44772 3 9V10C3 10.6569 4.34315 12 6 12H8V14C8 14.5523 8.44772 15 9 15H9.5C10.0523 15 10.5 14.5523 10.5 14V12H12C13.6569 12 15 10.6569 15 9V8H10.5V4C10.5 3.44772 10.0523 3 9.5 3H9ZM4.5 9C4.5 8.72386 4.72386 8.5 5 8.5H6.5V9H4.5V9ZM12 9V9.5H13.5V9C13.5 8.72386 13.2761 8.5 13 8.5H12V9Z" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            Share
          </button>
        {:else}
          <button class="share-btn disabled" title="Create an organization to share boards">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 3C8.44772 3 8 3.44772 8 4V8H4C3.44772 8 3 8.44772 3 9V10C3 10.6569 4.34315 12 6 12H8V14C8 14.5523 8.44772 15 9 15H9.5C10.0523 15 10.5 14.5523 10.5 14V12H12C13.6569 12 15 10.6569 15 9V8H10.5V4C10.5 3.44772 10.0523 3 9.5 3H9ZM4.5 9C4.5 8.72386 4.72386 8.5 5 8.5H6.5V9H4.5V9ZM12 9V9.5H13.5V9C13.5 8.72386 13.2761 8.5 13 8.5H12V9Z" stroke="currentColor" stroke-width="1.5"/>
            </svg>
            Share
          </button>
        {/if}
      {/if}
      <span class="card-count">{columns.reduce((sum, col) => sum + col.cards.length, 0)} cards</span>
    </div>
  </header>

  {#if loading}
    <div class="loading">Loading board...</div>
  {:else}
    <div class="columns-container">
      {#each columns as column (column.id)}
        <div class="column">
          <div class="column-header">
            <h3>{column.name}</h3>
            <div class="column-actions">
              <span class="card-count">{column.cards.length}</span>
              {#if isBoardOwner()}
                <button class="column-delete-btn" onclick={() => deleteColumn(column.id, column.name)} title="Delete column">×</button>
              {/if}
            </div>
          </div>
          <div class="column-content">
            {#if column.cards.length > 0}
              <div
                class="cards-list"
                dndzone={{ items: column.cards, flipDurationMs: 200 }}
                onconsider={(e) => handleDndConsider(column.id, e)}
                onfinalize={(e) => handleDndFinalize(column.id, e)}
              >
                {#each column.cards as card (card.id)}
                  <div
                    class="card"
                    draggable="true"
                    ondragstart={(e) => handleDragStart(e, card, column.id)}
                    onclick={() => openEditCard(card)}
                    onkeydown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        openEditCard(card);
                      }
                    }}
                    role="button"
                    tabindex="0"
                    aria-label={card.description ? `Edit card: ${card.title}. ${card.description}` : `Edit card: ${card.title}`}
                  >
                    <div class="card-header">
                      <span class="card-title">{card.title}</span>
                      <button class="delete-btn" onclick={(e) => deleteCard(column.id, card.id, e)}>×</button>
                    </div>
                    {#if card.description}
                      <p class="card-description">{card.description}</p>
                    {/if}
                    <div class="card-meta">
                      {#if card.created_at}
                        <span>{formatDate(card.created_at)}</span>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>
            {:else}
              <div class="empty-column">No cards</div>
            {/if}
          </div>
          <button class="add-card-btn" onclick={() => openCreateCard(column.id)}>
            <span>+</span> Add card
          </button>
        </div>
      {/each}
      <button class="add-column-btn" onclick={() => { newColumnName = ''; showCreateColumnModal = true; }}>
        <span>+</span> Add Column
      </button>
    </div>
  {/if}

    {#if showCreateCardModal}
      <Modal open={showCreateCardModal} onClose={() => showCreateCardModal = false} title="Add Card">
        {#snippet children()}
          <h2 id="modal-title">Add Card</h2>
          <form onsubmit={(e) => { e.preventDefault(); createCard(); }}>
            <input
              bind:value={newCardTitle}
              placeholder="Card title"
              required
            />
            <div class="modal-actions">
              <button type="button" class="cancel-btn" onclick={() => showCreateCardModal = false}>Cancel</button>
              <button type="submit" class="create-btn" disabled={createLoading}>
                {createLoading ? 'Adding...' : 'Add Card'}
              </button>
            </div>
          </form>
        {/snippet}
      </Modal>
    {/if}

    {#if showEditCardModal}
      <Modal open={showEditCardModal} onClose={() => showEditCardModal = false} title="Edit Card">
        {#snippet children()}
          <h2 id="modal-title">Edit Card</h2>
          <form onsubmit={(e) => { e.preventDefault(); saveCard(); }}>
            <input
              bind:value={editTitle}
              placeholder="Card title"
              required
            />
            <textarea
              bind:value={editDescription}
              placeholder="Description (optional)"
              rows="3"
            ></textarea>
            <div class="modal-actions">
              <button type="button" class="cancel-btn" onclick={() => showEditCardModal = false}>Cancel</button>
              <button type="submit" class="create-btn" disabled={editLoading}>
                {editLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
          
          {#if editingCard}
            <Comments 
              card={editingCard} 
              onCommentsUpdate={handleCommentsUpdate}
            />
          {/if}
        {/snippet}
      </Modal>
    {/if}

    {#if showCreateColumnModal}
      <Modal open={showCreateColumnModal} onClose={() => showCreateColumnModal = false} title="Add Column">
        {#snippet children()}
          <h2 id="modal-title">Add Column</h2>
          <form onsubmit={(e) => { e.preventDefault(); createColumn(); }}>
            <input
              bind:value={newColumnName}
              placeholder="Column name"
              required
            />
            <div class="modal-actions">
              <button type="button" class="cancel-btn" onclick={() => showCreateColumnModal = false}>Cancel</button>
              <button type="submit" class="create-btn" disabled={createColumnLoading}>
                {createColumnLoading ? 'Adding...' : 'Add Column'}
              </button>
            </div>
          </form>
        {/snippet}
      </Modal>
    {/if}

    {#if showShareModal}
      <ShareModal
        open={showShareModal}
        onClose={() => showShareModal = false}
        {board}
        availableTeams={availableTeams}
        onShare={onShare}
      />
    {/if}
  </div>

  <style>
  .board-view {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--color-border);
    flex-shrink: 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .back-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    font-size: 0.875rem;
  }

  .back-btn:hover {
    background: var(--color-muted);
  }

  header h1 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0;
  }

  .card-count {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
  }

  .share-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    font-size: 0.875rem;
  }

  .share-btn:hover {
    background: var(--color-muted);
    border-color: var(--color-primary);
  }

  .share-btn.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .share-btn.disabled:hover {
    background: transparent;
    border-color: var(--color-border);
  }

  .loading {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-muted-foreground);
  }

  .columns-container {
    flex: 1;
    display: flex;
    gap: 1rem;
    padding: 1.5rem;
    overflow-x: auto;
    min-height: 0;
  }

  .column {
    flex: 0 0 300px;
    display: flex;
    flex-direction: column;
    background: var(--color-muted);
    border-radius: 12px;
    max-height: 100%;
  }

  .column-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--color-border);
  }

  .column-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .column-delete-btn {
    padding: 0.125rem 0.375rem;
    font-size: 1rem;
    line-height: 1;
    background: transparent;
    color: var(--color-muted-foreground);
    border: none;
    opacity: 0;
    transition: opacity 0.15s ease;
  }

  .column:hover .column-delete-btn {
    opacity: 1;
  }

  .column-delete-btn:hover {
    color: var(--color-destructive);
    background: transparent;
  }

  .column-header h3 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .column-content {
    flex: 1;
    overflow-y: auto;
    padding: 0.75rem;
    min-height: 100px;
  }

  .cards-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-height: 50px;
  }

  .card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 0.75rem;
    cursor: grab;
    transition: all 0.15s ease;
  }

  .card:hover {
    border-color: var(--color-primary);
  }

  .card:active {
    cursor: grabbing;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .card-title {
    font-size: 0.9375rem;
    font-weight: 500;
    color: var(--color-foreground);
    word-break: break-word;
  }

  .delete-btn {
    padding: 0.125rem 0.375rem;
    font-size: 1rem;
    line-height: 1;
    background: transparent;
    color: var(--color-muted-foreground);
    border: none;
    opacity: 0;
    transition: opacity 0.15s ease;
  }

  .card:hover .delete-btn {
    opacity: 1;
  }

  .delete-btn:hover {
    color: var(--color-destructive);
    background: transparent;
  }

  .card-description {
    font-size: 0.8125rem;
    color: var(--color-muted-foreground);
    margin: 0.5rem 0 0 0;
    line-height: 1.5;
  }

  .card-meta {
    font-size: 0.75rem;
    color: var(--color-muted-foreground);
    margin-top: 0.5rem;
  }

  .empty-column {
    text-align: center;
    padding: 2rem 1rem;
    color: var(--color-muted-foreground);
    font-size: 0.875rem;
  }

  .add-card-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: transparent;
    color: var(--color-muted-foreground);
    border: none;
    border-top: 1px solid var(--color-border);
    font-size: 0.875rem;
    transition: all 0.15s ease;
  }

  .add-card-btn:hover {
    background: var(--color-muted);
    color: var(--color-foreground);
  }

  .add-card-btn span {
    font-size: 1.25rem;
    font-weight: 300;
  }

  .add-column-btn {
    flex: 0 0 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    background: transparent;
    color: var(--color-muted-foreground);
    border: 2px dashed var(--color-border);
    border-radius: 12px;
    font-size: 0.9375rem;
    font-weight: 500;
    transition: all 0.15s ease;
    height: fit-content;
  }

  .add-column-btn:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: var(--color-card);
  }

  .add-column-btn span {
    font-size: 1.5rem;
    font-weight: 300;
  }

  #modal-title {
    margin: 0 0 1.25rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
  }

  input {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
  }

  input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary);
  }

  textarea {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
    font-family: inherit;
    resize: vertical;
    min-height: 80px;
  }

  textarea:focus {
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

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .cancel-btn {
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
  }

  .cancel-btn:hover {
    background: var(--color-muted);
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
</style>
