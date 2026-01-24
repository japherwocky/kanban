<script>
  import PageLayout from '../lib/PageLayout.svelte';
  import BetaSection from '../components/BetaSection.svelte';
</script>

<PageLayout title="Pricing" description="Simple, transparent pricing for teams and AI agents.">
  <div class="pricing-placeholder">
    <p>
      We're still in closed beta and finalizing our pricing structure.
      For now, pkanban is free to use while we gather feedback.
    </p>

    <BetaSection
      marginTop="2rem"
      maxWidth="500px"
      borderRadius="12px"
      padding="2rem"
      h2FontSize="1.75rem"
      descFontSize="1rem"
      emailPadding="0.75rem 1.5rem"
      emailBorderRadius="10px"
      emailFontWeight="600"
      emailFontSize="0.9375rem"
      subtextFontSize="0.8125rem"
      compactPadding="1rem"
      compactH2FontSize="1.25rem"
      compactDescFontSize="0.875rem"
      compactEmailPadding="0.625rem 1.25rem"
      compactEmailFontSize="0.875rem"
    />
  </div>
</PageLayout>

<style>
  .pricing-placeholder {
    text-align: center;
  }

  .pricing-placeholder p {
    color: var(--color-muted-foreground);
    font-size: 1rem;
    line-height: 1.6;
    margin: 0;
  }
</style>
