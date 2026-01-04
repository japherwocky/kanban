<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import BoardView from '../lib/BoardView.svelte';
  import { api } from '../lib/api.js';

  let { params } = $props();

  let board = $state(null);
  let loading = $state(true);
  let error = $state(null);
  let availableTeams = $state([]);

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
      [board, availableTeams] = await Promise.all([
        api.boards.get(params.id),
        loadAvailableTeams()
      ]);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function loadAvailableTeams() {
    try {
      const teams = [];
      const orgs = await api.organizations.list();

      for (const org of orgs) {
        const orgTeams = await api.organizations.teams.list(org.id);
        for (const team of orgTeams) {
          teams.push({
            id: team.id,
            name: team.name,
            organization: org.name
          });
        }
      }

      return teams;
    } catch (e) {
      console.error('Failed to load teams:', e);
      return [];
    }
  }

  function goBack() {
    navigate('/boards');
  }

  async function handleShare(teamId, isPublicToOrg) {
    await api.boards.share(board.id, teamId, isPublicToOrg);
    // Reload board to get updated shared_team_id and is_public_to_org
    board = await api.boards.get(board.id);
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
  <BoardView board={board} onBack={goBack} availableTeams={availableTeams} onShare={handleShare} />
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
