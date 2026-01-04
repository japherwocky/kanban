<script>
  import { navigate } from 'svelte-routing';
</script>

<div class="not-found">
  <h1>404</h1>
  <p>Page not found</p>
  <button onclick={() => navigate('/boards')}>Go to Boards</button>
</div>

<style>
  .not-found {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 1rem;
    text-align: center;
  }

  .not-found h1 {
    font-size: 4rem;
    font-weight: 700;
    color: var(--color-primary);
    margin: 0;
  }

  .not-found p {
    font-size: 1.125rem;
    color: var(--color-muted-foreground);
    margin: 0;
  }

  button {
    padding: 0.75rem 1.5rem;
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
