<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { api } from '../lib/api.js';

  let { params = {} } = $props();

  let invite = $state(null);
  let loading = $state(true);
  let error = $state(null);
  let accepting = $state(false);

  onMount(async () => {
    try {
      invite = await api.invites.get(params.token);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  async function acceptInvite() {
    accepting = true;
    try {
      const result = await api.invites.accept(params.token);
      localStorage.setItem('redirectPath', `/organizations/${invite.id}`);
      navigate('/organizations');
    } catch (e) {
      alert(e.message);
    } finally {
      accepting = false;
    }
  }

  function goToLogin() {
    localStorage.setItem('redirectPath', `#!/invite/${params.token}`);
    navigate('/login');
  }

  function goToSignup() {
    localStorage.setItem('redirectPath', `#!/invite/${params.token}`);
    navigate('/signup');
  }
</script>

<div class="invite-container">
  <div class="invite-card">
    {#if loading}
      <div class="loading">Validating invite...</div>
    {:else if error}
      <div class="error">
        <h1>Invalid Invite</h1>
        <p>{error}</p>
        <a href="/" class="back-link">Go to homepage</a>
      </div>
    {:else}
      <h1>You're Invited!</h1>
      <p class="invite-text">
        <strong>{invite.created_by_username}</strong> has invited you to join
        <span class="org-name">{invite.organization_name}</span>
      </p>

      <div class="actions">
        {#if localStorage.getItem('token')}
          <button class="primary" onclick={acceptInvite} disabled={accepting}>
            {accepting ? 'Joining...' : 'Accept Invite'}
          </button>
        {:else}
          <p class="auth-prompt">Sign in to accept this invitation</p>
          <button class="primary" onclick={goToLogin}>Login</button>
          <button class="secondary" onclick={goToSignup}>Create Account</button>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .invite-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
  }

  .invite-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    width: 100%;
    max-width: 400px;
    padding: 2rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    text-align: center;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
    margin: 0;
  }

  .invite-text {
    font-size: 1rem;
    color: var(--color-foreground);
    line-height: 1.6;
  }

  .org-name {
    color: var(--color-primary);
    font-weight: 600;
  }

  .loading {
    color: var(--color-muted);
    font-size: 1rem;
  }

  .error h1 {
    color: var(--color-destructive);
  }

  .error p {
    color: var(--color-muted);
    margin: 0.5rem 0;
  }

  .back-link {
    color: var(--color-primary);
    text-decoration: none;
  }

  .back-link:hover {
    text-decoration: underline;
  }

  .actions {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
    margin-top: 1rem;
  }

  .auth-prompt {
    font-size: 0.875rem;
    color: var(--color-muted);
    margin: 0;
  }

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
    border: none;
  }

  button.primary {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
  }

  button.primary:hover:not(:disabled) {
    opacity: 0.9;
  }

  button.primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  button.secondary {
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
  }

  button.secondary:hover {
    background: var(--color-accent);
  }
</style>
