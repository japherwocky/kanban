<script>
  import PageLayout from '../lib/PageLayout.svelte';
  import BetaSection from '../components/BetaSection.svelte';
</script>

<PageLayout title="Contact" description="Get in touch with the pkanban team.">
  <div class="contact-content">
    <section class="contact-info">
      <div class="contact-item">
        <h3>Email</h3>
        <a href="mailto:pkanban@pearachute.com">pkanban@pearachute.com</a>
      </div>

      <div class="contact-item">
        <h3>GitHub</h3>
        <a href="https://github.com" target="_blank" rel="noopener">github.com/pkanban</a>
      </div>

      <div class="contact-item">
        <h3>Location</h3>
        <p>Portland, OR</p>
      </div>
    </section>

    <section class="use-cases">
      <h2>What We're Interested In</h2>
      <ul>
        <li>Teams building AI agent workflows</li>
        <li>Automation and CI/CD integrations</li>
        <li>Research applications for task orchestration</li>
        <li>Enterprise deployments</li>
      </ul>
    </section>

    <BetaSection
      marginTop="2rem"
      maxWidth="500px"
      borderRadius="12px"
      padding="2rem"
      h2FontSize="1.5rem"
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
  .contact-content {
    text-align: left;
  }

  .contact-info {
    display: grid;
    gap: 1.5rem;
    margin-bottom: 2.5rem;
  }

  .contact-item h3 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--color-muted-foreground);
    margin: 0 0 0.25rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .contact-item a,
  .contact-item p {
    font-size: 1rem;
    color: var(--color-foreground);
    margin: 0;
    text-decoration: none;
  }

  .contact-item a:hover {
    color: var(--color-primary);
  }

  .use-cases {
    margin-bottom: 2rem;
  }

  .use-cases h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
  }

  ul {
    margin: 0;
    padding-left: 1.25rem;
    color: var(--color-muted-foreground);
  }

  li {
    font-size: 1rem;
    line-height: 1.7;
    margin-bottom: 0.5rem;
  }

  @media (max-width: 640px) {
    .contact-info {
      gap: 1.25rem;
    }
  }
</style>
