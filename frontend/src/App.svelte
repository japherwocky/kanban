<script>
  let username = '';
  let password = '';
  let token = localStorage.getItem('token');
  let view = 'login';

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
        <button on:click={logout}>Logout</button>
      </header>
      <p>Boards list will go here...</p>
    </div>
  {/if}
</main>

<style>
  main {
    font-family: system-ui, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }
  .login {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  input {
    padding: 0.5rem;
    font-size: 1rem;
  }
  button {
    padding: 0.5rem 1rem;
    font-size: 1rem;
    cursor: pointer;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
</style>
