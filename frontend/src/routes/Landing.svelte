<script>
  import { navigate } from 'svelte-routing';
  import HeroSection from '../components/HeroSection.svelte';
  import FeaturesSection from '../components/FeaturesSection.svelte';
  import BetaSection from '../components/BetaSection.svelte';

  function goToLogin() {
    navigate('/login');
  }

  function goToDocs() {
    navigate('/docs');
  }

  function goToQuickstart() {
    navigate('/docs/quickstart');
  }

  function goToReference() {
    navigate('/docs/reference');
  }
</script>

<div class="landing">
  <HeroSection />

  <FeaturesSection />

  <BetaSection />
</div>

<style>
  .landing {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: var(--color-background);
  }
</style>

