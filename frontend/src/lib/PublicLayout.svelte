<script>
  import Header from './Header.svelte';
  import Footer from './Footer.svelte';
</script>

<div class="public-layout">
  <Header />
  <main>
    <slot />
  </main>
  <Footer />
</div>

<style>
  .public-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
</style>
