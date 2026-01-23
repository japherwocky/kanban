<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';

  let username = $state('');
  let password = $state('');

  onMount(() => {
    const token = localStorage.getItem('token');
    const redirectPath = localStorage.getItem('redirectPath') || '/boards';
    if (token) {
      localStorage.removeItem('redirectPath');
      navigate(redirectPath);
    }
  });

  async function login() {
    try {
      const res = await fetch('/api/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        const redirectPath = localStorage.getItem('redirectPath') || '/boards';
        localStorage.removeItem('redirectPath');
        navigate(redirectPath);
      } else {
        alert('Login failed');
      }
    } catch (e) {
      alert('Login failed: ' + e.message);
    }
  }
</script>

<div class="login">
  <h1>Kanban Board</h1>
  <form onsubmit={(e) => { e.preventDefault(); login(); }}>
    <input bind:value={username} placeholder="Username" required />
    <input type="password" bind:value={password} placeholder="Password" required />
    <button type="submit">Login</button>
  </form>

  <div class="beta-section">
    <h2>Closed Beta</h2>
    <p class="beta-description">
      We're currently in closed beta. If you'd like early access or want to integrate agents into your workflow,
      reach out and let us know your use case.
    </p>
    <a href="mailto:pkanban@pearachute.com" class="beta-email">
      pkanban@pearachute.com
    </a>
    <p class="beta-subtext">
      We're actively seeking feedback from teams building AI workflows.
    </p>
  </div>
</div>

<style>
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

  .beta-section {
    margin-top: 2rem;
    max-width: 400px;
    width: 100%;
    text-align: center;
    background: linear-gradient(135deg, var(--color-card) 0%, rgba(var(--color-primary-rgb), 0.05) 100%);
    border: 2px solid var(--color-primary);
    border-radius: 12px;
    padding: 1.5rem;
  }

  .beta-section h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
  }

  .beta-description {
    color: var(--color-muted-foreground);
    font-size: 0.9375rem;
    margin: 0 0 1rem 0;
    line-height: 1.5;
  }

  .beta-email {
    display: inline-block;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    padding: 0.625rem 1.25rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }

  .beta-email:hover {
    transform: translateY(-1px);
    opacity: 0.9;
  }

  .beta-subtext {
    margin-top: 1rem;
    color: var(--color-muted-foreground);
    font-size: 0.8125rem;
    font-style: italic;
  }

  @media (max-width: 480px) {
    .beta-section {
      padding: 1rem;
    }

    .beta-section h2 {
      font-size: 1.25rem;
    }

    .beta-description {
      font-size: 0.875rem;
    }
  }
</style>
