<script>
  import HeroSection from '../components/HeroSection.svelte';
  import FeaturesSection from '../components/FeaturesSection.svelte';
  import SignupCTA from '../components/SignupCTA.svelte';
</script>

<div class="landing">
  <HeroSection />

  <FeaturesSection />

  <SignupCTA />
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

