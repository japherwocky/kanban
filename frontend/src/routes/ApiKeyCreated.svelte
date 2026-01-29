<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';

  let apiKey = $state('');
  let keyName = $state('');
  let copied = $state(false);
  let mounted = $state(false);

  onMount(() => {
    // Get key from URL
    const params = new URLSearchParams(window.location.search);
    apiKey = params.get('key') || '';
    keyName = params.get('name') || 'API Key';
    mounted = true;

    // Clear URL to prevent re-exposure on refresh
    if (apiKey) {
      history.replaceState(null, '', window.location.pathname);
    }
  });

  async function copyKey() {
    if (!apiKey) return;

    try {
      await navigator.clipboard.writeText(apiKey);
      copied = true;
      setTimeout(() => {
        copied = false;
      }, 2000);
    } catch (e) {
      console.error('Failed to copy:', e);
    }
  }

  function done() {
    navigate('/settings/api-keys');
  }
</script>

<div class="key-created-page">
  <div class="success-icon">
    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="24" cy="24" r="20"/>
      <path d="M16 24l6 6 12-12" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>

  <h2>API Key Created</h2>
  <p class="key-name-display">{keyName}</p>

  <div class="warning-banner">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M10 6.67v5M10 14.67v.67"/>
      <circle cx="10" cy="10" r="8.33"/>
    </svg>
    <div>
      <strong>Copy this key now</strong>
      <p>You won't be able to see it again after leaving this page.</p>
    </div>
  </div>

  <div class="key-display">
    {#if mounted && apiKey}
      <code class="key-value">{apiKey}</code>
      <button class="copy-btn" onclick={copyKey} aria-label="Copy API key">
        {#if copied}
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M3.75 9l3.5 3.5 6.75-6.75" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Copied!
        {:else}
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="4" y="4" width="10" height="10" rx="1.5"/>
            <path d="M8.25 4v1.5a1.5 1.5 0 001.5 1.5h4"/>
          </svg>
          Copy
        {/if}
      </button>
    {:else}
      <p class="no-key">No key found. Please create a new API key.</p>
    {/if}
  </div>

  <div class="usage-section">
    <h3>Usage</h3>
    <p>Use this key to authenticate agents and CI pipelines:</p>
    <div class="code-example">
      <code>kanban --api-key {apiKey || 'your-api-key'} boards</code>
    </div>
    <p class="header-note">Or set the <code>X-API-Key</code> header when making API requests:</p>
    <div class="code-example">
      <code>curl -H "X-API-Key: {apiKey || 'your-api-key'}" https://api.example.com/boards</code>
    </div>
  </div>

  <button class="done-btn" onclick={done}>
    {copied ? 'Done' : 'I\'ve copied the key'}
  </button>
</div>

<style>
  .key-created-page {
    max-width: 520px;
    margin: 0 auto;
    text-align: center;
    animation: fadeIn 0.3s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .success-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    background: rgba(34, 197, 94, 0.1);
    border-radius: 50%;
    color: var(--color-success);
    margin-bottom: 1.5rem;
  }

  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 0.5rem 0;
  }

  .key-name-display {
    font-size: 1rem;
    color: var(--color-muted-foreground);
    margin: 0 0 1.5rem 0;
  }

  .warning-banner {
    display: flex;
    gap: 0.875rem;
    padding: 1rem;
    background: rgba(251, 191, 36, 0.1);
    border: 1px solid rgba(251, 191, 36, 0.3);
    border-radius: 10px;
    text-align: left;
    margin-bottom: 1.5rem;
  }

  .warning-banner svg {
    flex-shrink: 0;
    color: #f59e0b;
    margin-top: 0.125rem;
  }

  .warning-banner strong {
    display: block;
    font-size: 0.9375rem;
    font-weight: 600;
    color: #b45309;
    margin-bottom: 0.25rem;
  }

  .warning-banner p {
    font-size: 0.8125rem;
    color: #92400e;
    margin: 0;
    line-height: 1.4;
  }

  .key-display {
    display: flex;
    align-items: stretch;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--color-code-bg);
    border: 1px solid var(--color-border);
    border-radius: 10px;
    margin-bottom: 2rem;
  }

  .key-value {
    flex: 1;
    padding: 0.875rem 1rem;
    font-family: var(--font-mono);
    font-size: 0.875rem;
    color: var(--color-code-fg);
    background: transparent;
    border: none;
    word-break: break-all;
    text-align: left;
    line-height: 1.5;
  }

  .copy-btn {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.625rem 1rem;
    background: var(--color-muted);
    border: none;
    border-radius: 6px;
    font-size: 0.8125rem;
    font-weight: 500;
    color: var(--color-foreground);
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
  }

  .copy-btn:hover {
    background: var(--color-border);
  }

  .no-key {
    flex: 1;
    padding: 0.875rem;
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    margin: 0;
  }

  .usage-section {
    text-align: left;
    padding: 1.5rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    margin-bottom: 1.5rem;
  }

  .usage-section h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.5rem 0;
  }

  .usage-section > p {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    margin: 0 0 0.75rem 0;
  }

  .code-example {
    padding: 0.75rem 1rem;
    background: var(--color-code-bg);
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .code-example code {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
    color: var(--color-code-fg);
    word-break: break-all;
  }

  .header-note {
    font-size: 0.8125rem;
    color: var(--color-muted-foreground);
    margin: 0 0 0.375rem 0;
  }

  .header-note code {
    padding: 0.125rem 0.375rem;
    background: var(--color-muted);
    border-radius: 4px;
    font-size: 0.75rem;
    color: var(--color-foreground);
  }

  .done-btn {
    width: 100%;
    padding: 0.875rem 1.5rem;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .done-btn:hover {
    opacity: 0.9;
  }

  @media (max-width: 480px) {
    .key-display {
      flex-direction: column;
    }

    .copy-btn {
      justify-content: center;
    }
  }
</style>
