<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';

  let { children } = $props();
  let authChecked = $state(false);
  let isAuthenticated = $state(false);

  onMount(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      const currentPath = window.location.pathname;
      localStorage.setItem('redirectPath', currentPath);
      navigate('/login', { replace: true });
    } else {
      authChecked = true;
      isAuthenticated = true;
    }
  });
</script>

{#if authChecked && isAuthenticated}
  {@render children()}
{/if}
