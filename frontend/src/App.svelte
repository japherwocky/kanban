<script>
  import { onMount } from 'svelte';
  import { theme } from './lib/theme.js';
  import ThemeToggle from './lib/ThemeToggle.svelte';

  let username = '';
  let password = '';
  let token = localStorage.getItem('token');
  let view = 'login';

  onMount(() => {
    theme.init();
  });

  async function login() {
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
    } else {
      alert('Login failed');
    }
  }

  function logout() {
    token = null;
    localStorage.removeItem('token');
    view = 'login';
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
  {:else}
    <div class="app">
      <header>
        <h1>Kanban Board</h1>
        <div class="header-actions">
          <ThemeToggle />
          <button class="logout-btn" on:click={logout}>Logout</button>
        </div>
      </header>
      <p>Boards list will go here...</p>
    </div>
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
</style>
