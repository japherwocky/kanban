<script>
  import { navigate } from 'svelte-routing';

  let { children } = $props();

  const tabs = [
    { path: '/settings/api-keys', label: 'API Keys' },
  ];

  function goTo(path) {
    navigate(path);
  }
</script>

<div class="settings-layout">
  <header class="settings-header">
    <button class="back-btn" onclick={() => navigate('/boards')}>
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M12 4L6 10L12 16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      Back to Boards
    </button>
    <h1>Settings</h1>
  </header>

  <nav class="settings-nav">
    {#each tabs as tab}
      <button
        class="nav-tab"
        onclick={() => goTo(tab.path)}
      >
        {tab.label}
      </button>
    {/each}
  </nav>

  <main class="settings-content">
    {@render children()}
  </main>
</div>

<style>
  .settings-layout {
    padding: 1.5rem;
    max-width: 900px;
    margin: 0 auto;
  }

  .settings-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--color-border);
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
    cursor: pointer;
    border-radius: 8px;
    transition: all 0.15s ease;
  }

  .back-btn:hover {
    background: var(--color-muted);
  }

  .settings-header h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
    margin: 0;
  }

  .settings-nav {
    display: flex;
    gap: 0.25rem;
    margin-bottom: 2rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--color-border);
    overflow-x: auto;
  }

  .nav-tab {
    padding: 0.75rem 1.25rem;
    background: transparent;
    border: none;
    border-radius: 8px;
    color: var(--color-muted-foreground);
    font-size: 0.9375rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
  }

  .nav-tab:hover {
    color: var(--color-foreground);
    background: var(--color-muted);
  }

  .settings-content {
    min-height: 400px;
  }
</style>
