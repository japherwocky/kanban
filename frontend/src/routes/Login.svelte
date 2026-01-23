<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import BetaSection from '../components/BetaSection.svelte';

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

  <BetaSection 
    marginTop="2rem"
    maxWidth="400px"
    borderRadius="12px"
    padding="1.5rem"
    h2FontSize="1.5rem"
    descFontSize="0.9375rem"
    emailPadding="0.625rem 1.25rem"
    emailBorderRadius="8px"
    emailFontWeight="500"
    emailFontSize="0.875rem"
    subtextFontSize="0.8125rem"
    compactPadding="1rem"
    compactH2FontSize="1.25rem"
    compactDescFontSize="0.875rem"
    compactEmailPadding="0.625rem 1.25rem"
    compactEmailFontSize="0.875rem"
  />
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
</style>
