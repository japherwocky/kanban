<script>
  import PageLayout from '../lib/PageLayout.svelte';
</script>

<PageLayout title="Terms of Service" description="">
  <div class="legal-content">
    <section>
      <p class="last-updated">Last updated: January 2026</p>

      <h2>Acceptance of Terms</h2>
      <p>
        By using pkanban, you agree to these terms of service. If you do not agree,
        please do not use the service.
      </p>

      <h2>Use of Service</h2>
      <p>
        pkanban is provided "as is" for task management and workflow orchestration.
        You are responsible for maintaining the security of your account credentials.
      </p>

      <h2>Content and Data</h2>
      <p>
        You retain ownership of all data you create using pkanban. We do not claim
        ownership of your board data, task information, or any content you upload.
      </p>

      <h2>AI Agent Integration</h2>
      <p>
        When using pkanban's CLI or API with AI agents, you are responsible for
        ensuring agent actions comply with these terms. Use of automated agents
        should respect rate limits and intended functionality.
      </p>

      <h2>Limitations</h2>
      <p>
        During the closed beta period, we may limit features, storage, or access
        with prior notice. The service is provided without warranty of any kind.
      </p>

      <h2>Termination</h2>
      <p>
        We reserve the right to terminate or suspend access to the service at our
        discretion, without notice, for violations of these terms.
      </p>

      <h2>Contact</h2>
      <p>
        For questions about these terms, contact us at <a href="mailto:pkanban@pearachute.com">pkanban@pearachute.com</a>.
      </p>
    </section>
  </div>
</PageLayout>

<style>
  .legal-content {
    text-align: left;
  }

  .last-updated {
    color: var(--color-muted-foreground);
    font-size: 0.875rem;
    font-style: italic;
    margin: 0 0 2rem 0;
  }

  section {
    margin-bottom: 2rem;
  }

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
  }

  p {
    color: var(--color-muted-foreground);
    font-size: 1rem;
    line-height: 1.7;
    margin: 0 0 1rem 0;
  }

  a {
    color: var(--color-primary);
    text-decoration: none;
  }

  a:hover {
    text-decoration: underline;
  }

  @media (max-width: 640px) {
    h2 {
      font-size: 1.125rem;
    }
  }
</style>
