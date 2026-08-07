<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { api } from '../lib/api.js';

  let status = $state('working'); // working | done | failed
  let error = $state(null);

  onMount(async () => {
    const token = new URLSearchParams(window.location.search).get('token');
    if (!token) {
      status = 'failed';
      error = 'This link is missing its verification token.';
      return;
    }

    try {
      const result = await api.auth.verifyEmail(token);
      // Verifying logs you in, same as a successful login would.
      localStorage.setItem('token', result.access_token);
      status = 'done';

      // Honour the redirect an invite link stashed before sending the user
      // off to sign up, so invite -> signup -> verify lands back on the invite.
      const redirectPath = localStorage.getItem('redirectPath') || '/boards';
      localStorage.removeItem('redirectPath');
      navigate(redirectPath);
    } catch (e) {
      status = 'failed';
      error = e.message;
    }
  });
</script>

<div class="verify-container">
  <div class="verify-card">
    {#if status === 'working'}
      <p class="loading">Verifying your email...</p>
    {:else if status === 'done'}
      <h1>You're verified</h1>
      <p>Taking you to your boards...</p>
    {:else}
      <h1 class="failed">Verification failed</h1>
      <p class="error">{error}</p>
      <p class="hint">
        Links expire after 24 hours and can only be used once.
        You can request a new one from the login page.
      </p>
      <a href="/login" class="back-link">Go to login</a>
    {/if}
  </div>
</div>

<style>
  .verify-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
  }

  .verify-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
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

  h1.failed {
    color: var(--color-destructive);
  }

  p {
    margin: 0;
    color: var(--color-foreground);
    line-height: 1.6;
  }

  .loading {
    color: var(--color-muted);
  }

  .error {
    color: var(--color-destructive);
    font-size: 0.9375rem;
  }

  .hint {
    color: var(--color-muted);
    font-size: 0.8125rem;
  }

  .back-link {
    color: var(--color-primary);
    text-decoration: none;
  }

  .back-link:hover {
    text-decoration: underline;
  }
</style>
