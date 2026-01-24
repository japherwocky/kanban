<script>
  import Header from './Header.svelte';
  import Footer from './Footer.svelte';
</script>

<Header />
<main>
  <slot />
</main>
<Footer />

<style>
  main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
</style>
