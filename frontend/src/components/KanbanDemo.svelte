<script>
  import { onMount, onDestroy } from 'svelte';

  let cards = $state([
    { id: 1, title: 'Setup project structure', status: 'todo' },
    { id: 2, title: 'Configure database', status: 'done' },
    { id: 3, title: 'Design API schema', status: 'done' }
  ]);

  let animatedCard = $state(null);
  let cardPosition = $state({ x: 0, y: 0 });
  let isAnimating = $state(false);

  function handleTerminalCommand(event) {
    const { action } = event.detail;

    if (action === 'add') {
      addCard();
    } else if (action === 'move') {
      moveCard();
    }
  }

  function addCard() {
    const newCard = {
      id: 12,
      title: 'Fix API latency',
      status: 'todo',
      isNew: true
    };

    animatedCard = newCard;
    isAnimating = true;

    // Animate card appearing
    setTimeout(() => {
      animatedCard.isNew = false;
      cards = [...cards, newCard];
      isAnimating = false;
    }, 300);
  }

  function moveCard() {
    const cardToMove = cards.find(c => c.id === 12);
    if (cardToMove && cardToMove.status === 'todo') {
      // Start animation
      animatedCard = cardToMove;

      // Update status after animation
      setTimeout(() => {
        animatedCard.status = 'in-progress';
        cardToMove.status = 'in-progress';
      }, 600);
    }
  }

  onMount(() => {
    window.addEventListener('terminal-command', handleTerminalCommand);
  });

  onDestroy(() => {
    window.removeEventListener('terminal-command', handleTerminalCommand);
  });

  function getCardsByStatus(status) {
    return cards.filter(card => card.status === status);
  }
</script>

<div class="kanban-board">
  <div class="column">
    <div class="column-header">
      <span class="column-dot todo"></span>
      <span class="column-title">Todo</span>
      <span class="column-count">{getCardsByStatus('todo').length}</span>
    </div>
    <div class="column-content">
      {#each getCardsByStatus('todo') as card (card.id)}
        <div
          class="card"
          class:animated={animatedCard?.id === card.id && card.status === 'todo'}
          class:move-target={animatedCard?.id === card.id && animatedCard?.status === 'in-progress'}
        >
          <div class="card-content">
            <span class="card-id">#{card.id}</span>
            <p class="card-title">{card.title}</p>
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
      <span class="column-count">{getCardsByStatus('in-progress').length}</span>
    </div>
    <div class="column-content">
      {#each getCardsByStatus('in-progress') as card (card.id)}
        <div
          class="card"
          class:animated={animatedCard?.id === card.id && card.status === 'in-progress'}
          class:move-source={animatedCard?.id === card.id && animatedCard?.status === 'todo'}
        >
          <div class="card-content">
            <span class="card-id">#{card.id}</span>
            <p class="card-title">{card.title}</p>
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
      <span class="column-dot done"></span>
      <span class="column-title">Done</span>
      <span class="column-count">{getCardsByStatus('done').length}</span>
    </div>
    <div class="column-content">
      {#each getCardsByStatus('done') as card (card.id)}
        <div class="card done-card">
          <div class="card-content">
            <span class="card-id">#{card.id}</span>
            <p class="card-title">{card.title}</p>
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
    background: rgba(15, 23, 42, 0.6);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
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

  .column-dot.todo { background: #64748b; }
  .column-dot.in-progress { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
  .column-dot.done { background: #22c55e; box-shadow: 0 0 8px #22c55e; }

  .column-title {
    font-size: 13px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .column-count {
    font-size: 12px;
    color: #64748b;
    background: rgba(255, 255, 255, 0.05);
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
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 14px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    backdrop-filter: blur(8px);
  }

  .card:hover {
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
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

  .card.done-card {
    opacity: 0.6;
  }

  .card-content {
    margin-bottom: 12px;
  }

  .card-id {
    font-size: 11px;
    color: #64748b;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }

  .card-title {
    font-size: 14px;
    color: #e2e8f0;
    font-weight: 500;
    margin: 6px 0 0 0;
    line-height: 1.4;
  }

  .card-footer {
    display: flex;
    justify-content: flex-end;
  }

  .card-avatar {
    width: 24px;
    height: 24px;
    border-radius: 6px;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  }

  .card-avatar.done-avatar {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
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
