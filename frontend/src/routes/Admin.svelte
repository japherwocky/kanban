<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { api } from '../lib/api.js';
  import ThemeToggle from '../lib/ThemeToggle.svelte';
  import AdminUsers from './AdminUsers.svelte';
  import AdminOrganizations from './AdminOrganizations.svelte';
  import AdminTeams from './AdminTeams.svelte';
  import AdminBoards from './AdminBoards.svelte';

  const { params } = $props();

  let isAdmin = $state(false);
  let adminCheckLoading = $state(true);

  // Get current section from route, default to 'users'
  let currentSection = $derived(params.section || 'users');

  onMount(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    await checkAdminStatus();
    if (!isAdmin) {
      navigate('/');
      return;
    }
  });

  async function checkAdminStatus() {
    try {
      const status = await api.admin.status();
      isAdmin = status.is_admin;
    } catch (e) {
      console.error('Admin check failed:', e);
      isAdmin = false;
    } finally {
      adminCheckLoading = false;
    }
  }

  function logout() {
    localStorage.removeItem('token');
    navigate('/login');
  }

  function navigateTo(section) {
    navigate(`/admin/${section}`);
  }
</script>

{#if adminCheckLoading}
  <div class="loading">Checking admin permissions...</div>
{:else if !isAdmin}
  <div class="not-admin">
    <h2>Access Denied</h2>
    <p>You don't have admin permissions to access this page.</p>
    <button onclick={() => navigate('/')}>Go to Dashboard</button>
  </div>
{:else}
  <div class="admin-app">
    <header>
      <h1>Admin Dashboard</h1>
      <div class="header-actions">
        <button class="nav-btn" onclick={() => navigate('/')}>Back to App</button>
        <ThemeToggle />
        <button class="logout-btn" onclick={logout}>Logout</button>
      </div>
    </header>

    <div class="admin-layout">
      <aside class="sidebar">
        <nav>
          <button
            class:active={currentSection === 'users'}
            onclick={() => navigateTo('users')}
          >
            Users
          </button>
          <button
            class:active={currentSection === 'organizations'}
            onclick={() => navigateTo('organizations')}
          >
            Organizations
          </button>
          <button
            class:active={currentSection === 'teams'}
            onclick={() => navigateTo('teams')}
          >
            Teams
          </button>
          <button
            class:active={currentSection === 'boards'}
            onclick={() => navigateTo('boards')}
          >
            Boards
          </button>
        </nav>
      </aside>

      <main class="content">
        {#if currentSection === 'users'}
          <AdminUsers />
        {:else if currentSection === 'organizations'}
          <AdminOrganizations />
        {:else if currentSection === 'teams'}
          <AdminTeams />
        {:else if currentSection === 'boards'}
          <AdminBoards />
        {:else}
          <div class="coming-soon">
            <h2>{currentSection.charAt(0).toUpperCase() + currentSection.slice(1)}</h2>
            <p>This section is coming soon</p>
          </div>
        {/if}
      </main>
    </div>
  </div>
{/if}

<style>
  .loading, .not-admin, .coming-soon {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: var(--color-muted-foreground);
  }

  .not-admin h2 {
    color: var(--color-destructive);
    margin-bottom: 0.5rem;
  }

  .admin-app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-card);
  }

  header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-destructive);
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .nav-btn {
    padding: 0.5rem 1rem;
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    font-size: 0.875rem;
  }

  .nav-btn:hover {
    background: var(--color-muted);
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

  .admin-layout {
    display: flex;
    flex: 1;
  }

  .sidebar {
    width: 240px;
    background: var(--color-muted);
    border-right: 1px solid var(--color-border);
    padding: 1rem 0;
  }

  .sidebar nav {
    display: flex;
    flex-direction: column;
  }

  .sidebar button {
    width: 100%;
    padding: 0.75rem 1.5rem;
    text-align: left;
    background: transparent;
    border: none;
    color: var(--color-foreground);
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .sidebar button:hover:not(:disabled) {
    background: var(--color-card);
  }

  .sidebar button.active {
    background: var(--color-card);
    color: var(--color-primary);
    font-weight: 600;
    border-left: 3px solid var(--color-primary);
  }

  .sidebar button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .content {
    flex: 1;
    padding: 2rem;
  }

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .coming-soon h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin-bottom: 0.5rem;
  }
</style>
