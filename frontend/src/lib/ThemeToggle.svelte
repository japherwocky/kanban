<script>
  import { theme, getThemeLabel } from './theme.js';
  import { onMount } from 'svelte';

  let currentTheme = $state('system');
  let mounted = $state(false);

  theme.subscribe(t => {
    currentTheme = t;
  });

  onMount(() => {
    mounted = true;
  });

  const icons = {
    light: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>`,
    dark: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`,
    system: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>`
  };

  function cycleTheme() {
    theme.cycleTheme();
  }
</script>

<button
  onclick={cycleTheme}
  class="theme-toggle"
  title="Toggle theme: {getThemeLabel(currentTheme)}"
  aria-label="Toggle theme"
>
  {#if mounted}
    {@html icons[currentTheme] || icons.system}
  {:else}
    {@html icons.system}
  {/if}
</button>

<style>
  .theme-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .theme-toggle:hover {
    background: var(--color-muted);
  }

  .theme-toggle:focus {
    outline: 2px solid var(--color-primary);
    outline-offset: 2px;
  }
</style>
