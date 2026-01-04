<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import BoardView from '../lib/BoardView.svelte';
  import { api } from '../lib/api.js';

  let { params } = $props();

  let board = $state(null);
  let loading = $state(true);
  let error = $state(null);

  onMount(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      const currentPath = window.location.pathname;
      localStorage.setItem('redirectPath', currentPath);
      navigate('/login');
      return;
    }

    try {
      loading = true;
      board = await api.boards.get(params.id);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function goBack() {
    navigate('/boards');
  }
</script>

{#if loading}
  <div class="loading">Loading board...</div>
{:else if error}
  <div class="error">
    <p>{error}</p>
    <button onclick={goBack}>Back to Boards</button>
  </div>
{:else if board}
  <BoardView board={board} onBack={goBack} />
{/if}

<style>
  .loading, .error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 1rem;
    text-align: center;
  }

  .loading {
    color: var(--color-muted-foreground);
  }

  .error {
    padding: 2rem;
  }

  .error p {
    color: var(--color-destructive);
  }

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
  }

  button:hover {
    opacity: 0.9;
  }
</style>
