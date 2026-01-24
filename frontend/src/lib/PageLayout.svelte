<script>
  import BetaSection from '../components/BetaSection.svelte';

  export let title = '';
  export let description = '';
</script>

<div class="page">
  <div class="page-container">
    <h1>{title}</h1>
    {#if description}
      <p class="description">{description}</p>
    {/if}

    <slot />
  </div>
</div>

<style>
  .page {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem 1.5rem;
  }

  .page-container {
    max-width: 700px;
    width: 100%;
  }

  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 1rem 0;
    text-align: center;
  }

  .description {
    font-size: 1.125rem;
    color: var(--color-muted-foreground);
    line-height: 1.6;
    margin: 0 0 2rem 0;
    text-align: center;
  }

  @media (max-width: 640px) {
    .page {
      padding: 2rem 1rem;
    }

    h1 {
      font-size: 1.75rem;
    }
  }
</style>
