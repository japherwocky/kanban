<script>
  import PageLayout from '../lib/PageLayout.svelte';
  import SignupCTA from '../components/SignupCTA.svelte';
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
        <a href="https://github.com/japherwocky/kanban" target="_blank" rel="noopener">github.com/japherwocky/kanban</a>
      </div>

      <div class="contact-item">
        <h3>Location</h3>
        <p>Michigan</p>
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

    <SignupCTA
      marginTop="2rem"
      maxWidth="500px"
      borderRadius="12px"
      padding="2rem"
      h2FontSize="1.5rem"
      descFontSize="1rem"
      subtextFontSize="0.8125rem"
      compactPadding="1rem"
      compactH2FontSize="1.25rem"
      compactDescFontSize="0.875rem"
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
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-muted-foreground);
    margin: 0 0 0.25rem 0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .contact-item a,
  .contact-item p {
    font-size: var(--text-base);
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
    font-size: var(--text-xl);
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
    font-size: var(--text-base);
    line-height: 1.7;
    margin-bottom: 0.5rem;
  }

  @media (max-width: 640px) {
    .contact-info {
      gap: 1.25rem;
    }
  }
</style>
