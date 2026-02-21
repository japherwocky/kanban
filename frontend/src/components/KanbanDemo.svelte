<script>
  import { onMount, onDestroy } from 'svelte';
  import { getDemoState } from '$lib/demoApi';

  // Initial cards - will be replaced by state from demoApi
  let columns = $state([
    { id: 1, name: 'Todo', cards: [] },
    { id: 2, name: 'In Progress', cards: [] },
    { id: 3, name: 'Done', cards: [] }
  ]);

  let animatedCard = $state(null);
  let previousCardState = $state(null);
  let isAnimating = $state(false);

  function updateColumnsFromState(state) {
    if (!state || !state.board) return;

    const newColumns = state.board.columns.map(col => ({
      id: col.id,
      name: col.name,
      cards: col.cards.map(card => ({
        id: card.id,
        title: card.title,
        description: card.description,
        isNew: card.isNew,
        justMoved: card.justMoved
      }))
    }));

    // Detect changes for animations
    detectChanges(columns, newColumns);
    columns = newColumns;
  }

  function detectChanges(oldCols, newCols) {
    if (!oldCols || oldCols.length === 0) {
      // First load - just set state without animation
      return;
    }

    // Check for new cards
    for (const newCol of newCols) {
      const oldCol = oldCols.find(c => c.id === newCol.id);
      for (const newCard of newCol.cards) {
        const oldCard = oldCol?.cards.find(c => c.id === newCard.id);
        if (!oldCard) {
          // New card added
          animatedCard = { ...newCard, columnId: newCol.id, isNew: true };
          setTimeout(() => {
            animatedCard = null;
          }, 300);
          return; // Handle one change at a time
        }
      }
    }

    // Check for moved cards
    for (const newCol of newCols) {
      const oldCol = oldCols.find(c => c.id === newCol.id);
      for (const newCard of newCol.cards) {
        const oldCard = oldCol?.cards.find(c => c.id === newCard.id);
        if (oldCard && oldCol.id !== newCol.id) {
          // Card moved between columns
          animatedCard = { ...newCard, columnId: newCol.id, justMoved: true };
          setTimeout(() => {
            animatedCard = null;
          }, 600);
          return;
        }
      }
    }

    // Check for description updates
    for (const newCol of newCols) {
      const oldCol = oldCols.find(c => c.id === newCol.id);
      for (const newCard of newCol.cards) {
        const oldCard = oldCol?.cards.find(c => c.id === newCard.id);
        if (oldCard && oldCard.description !== newCard.description && newCard.description) {
          // Description added
          animatedCard = { ...newCard, columnId: newCol.id, descriptionUpdated: true };
          setTimeout(() => {
            animatedCard = null;
          }, 500);
          return;
        }
      }
    }
  }

  function handleStateUpdate(event) {
    const { state } = event.detail;
    updateColumnsFromState(state);
  }

  onMount(() => {
    window.addEventListener('demo-state-update', handleStateUpdate);
    // Initialize with demo state
    updateColumnsFromState(getDemoState());
  });

  onDestroy(() => {
    window.removeEventListener('demo-state-update', handleStateUpdate);
  });

  function getCardsByStatus(status) {
    const col = columns.find(c => c.name === status);
    return col ? col.cards : [];
  }

  function getColumnCount(status) {
    return getCardsByStatus(status).length;
  }
</script>

<div class="kanban-board">
  <div class="column">
    <div class="column-header">
      <span class="column-dot todo"></span>
      <span class="column-title">Todo</span>
      <span class="column-count">{getColumnCount('Todo')}</span>
    </div>
    <div class="column-content">
      {#each getCardsByStatus('Todo') as card (card.id)}
        <div
          class="card"
          class:animated={animatedCard?.id === card.id}
          class:move-target={animatedCard?.id === card.id && animatedCard?.columnId === 1}
          class:description-updated={animatedCard?.id === card.id && card.description}
        >
          <div class="card-content">
            <span class="card-id">#{card.id}</span>
            <p class="card-title">{card.title}</p>
            {#if card.description}
              <p class="card-description">{card.description}</p>
            {/if}
          </div>
          <div class="card-footer">
            <div class="card-avatar"></div>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <div class="column">
    <div class="column-header">
      <span class="column-dot in-progress"></span>
      <span class="column-title">In Progress</span>
      <span class="column-count">{getColumnCount('In Progress')}</span>
    </div>
    <div class="column-content">
      {#each getCardsByStatus('In Progress') as card (card.id)}
        <div
          class="card"
          class:animated={animatedCard?.id === card.id}
          class:move-source={animatedCard?.id === card.id && animatedCard?.columnId !== 2}
          class:description-updated={animatedCard?.id === card.id && card.description}
        >
          <div class="card-content">
            <span class="card-id">#{card.id}</span>
            <p class="card-title">{card.title}</p>
            {#if card.description}
              <p class="card-description">{card.description}</p>
            {/if}
          </div>
          <div class="card-footer">
            <div class="card-avatar in-progress-avatar"></div>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <div class="column">
    <div class="column-header">
      <span class="column-dot done"></span>
      <span class="column-title">Done</span>
      <span class="column-count">{getColumnCount('Done')}</span>
    </div>
    <div class="column-content">
      {#each getCardsByStatus('Done') as card (card.id)}
        <div class="card done-card">
          <div class="card-content">
            <span class="card-id">#{card.id}</span>
            <p class="card-title">{card.title}</p>
            {#if card.description}
              <p class="card-description">{card.description}</p>
            {/if}
          </div>
          <div class="card-footer">
            <div class="card-avatar done-avatar"></div>
          </div>
        </div>
      {/each}
    </div>
  </div>
</div>

<style>
  .kanban-board {
    display: flex;
    gap: 16px;
    height: 100%;
    padding: 20px;
    background: var(--color-surface);
    border-radius: 12px;
    border: 1px solid var(--color-border);
  }

  .column {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .column-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 4px;
    margin-bottom: 12px;
  }

  .column-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .column-dot.todo {
    background: var(--color-muted-foreground);
  }

  .column-dot.in-progress {
    background: #f59e0b;
    box-shadow: 0 0 8px #f59e0b;
  }

  .column-dot.done {
    background: var(--color-success);
    box-shadow: 0 0 8px var(--color-success);
  }

  /* Light mode status dots - more vibrant */
  :global(.light) .column-dot.in-progress {
    background: #d97706;
    box-shadow: 0 0 6px #f59e0b80;
  }

  :global(.light) .column-dot.done {
    background: #16a34a;
    box-shadow: 0 0 6px #22c55e80;
  }

  .column-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--color-foreground);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.7;
  }

  .column-count {
    font-size: 12px;
    color: var(--color-muted-foreground);
    background: color-mix(in srgb, var(--color-foreground) 5%, transparent);
    padding: 2px 8px;
    border-radius: 10px;
  }

  .column-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
    overflow-y: auto;
  }

  .card {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 14px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    backdrop-filter: blur(8px);
  }

  .card:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px color-mix(in srgb, var(--color-primary) 10%, transparent);
  }

  .card.animated {
    animation: cardAppear 0.3s ease-out;
  }

  .card.move-source {
    animation: cardMoveOut 0.5s ease-in-out forwards;
  }

  .card.move-target {
    animation: cardMoveIn 0.5s ease-in-out forwards;
  }

  .card.description-updated {
    animation: descriptionFlash 0.5s ease-out;
  }

  .card.done-card {
    opacity: 0.6;
  }

  .card-content {
    margin-bottom: 12px;
  }

  .card-id {
    font-size: 11px;
    color: var(--color-muted-foreground);
    font-family: var(--font-mono);
  }

  .card-title {
    font-size: 14px;
    color: var(--color-foreground);
    font-weight: 500;
    margin: 6px 0 0 0;
    line-height: 1.4;
  }

  .card-description {
    font-size: 12px;
    color: var(--color-muted-foreground);
    margin: 8px 0 0 0;
    line-height: 1.4;
    font-style: italic;
  }

  .card-footer {
    display: flex;
    justify-content: flex-end;
  }

  .card-avatar {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  }

  .card-avatar.in-progress-avatar {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  }

  .card-avatar.done-avatar {
    background: linear-gradient(135deg, var(--color-success) 0%, #16a34a 100%);
  }

  @keyframes cardAppear {
    from {
      opacity: 0;
      transform: translateY(20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  @keyframes cardMoveOut {
    from {
      opacity: 1;
      transform: translateX(0);
    }
    to {
      opacity: 0;
      transform: translateX(100px);
    }
  }

  @keyframes cardMoveIn {
    from {
      opacity: 0;
      transform: translateX(-100px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes descriptionFlash {
    from {
      background: color-mix(in srgb, var(--color-primary) 20%, transparent);
    }
    to {
      background: var(--color-surface);
    }
  }

  @media (max-width: 768px) {
    .kanban-board {
      flex-direction: column;
      gap: 12px;
      padding: 16px;
    }

    .column {
      min-height: 100px;
    }

    .card {
      padding: 12px;
    }

    .card-title {
      font-size: 13px;
    }
  }
</style>
