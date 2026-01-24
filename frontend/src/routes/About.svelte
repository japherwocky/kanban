<script>
  import PageLayout from '../lib/PageLayout.svelte';
  import BetaSection from '../components/BetaSection.svelte';
</script>

<PageLayout
  title="About"
  description="Building the kanban tool we wanted for orchestrating human and AI agent workflows."
>
  <div class="about-content">
    <section>
      <h2>Our Mission</h2>
      <p>
        Most task management tools are built for humans. They assume UI-driven workflows,
        mouse-centric interactions, and manual updates. But AI agents think differently.
      </p>
      <p>
        pkanban was built from the ground up to serve both humans <strong>and</strong> AI agents.
        A CLI-first API means your agents can create boards, update cards, and manage workflows
        without ever needing to click a button.
      </p>
    </section>

    <section>
      <h2>Why "pkanban"?</h2>
      <p>
        The "p" stands for pip. It started as a Python package for AI agents to manage their
        workflows, and evolved into a full-featured kanban tool that syncs between CLI and web.
      </p>
    </section>

    <section>
      <h2>Built For</h2>
      <ul>
        <li>Teams building AI-powered workflows</li>
        <li>Developers who prefer the terminal</li>
        <li>Automation pipelines that need task tracking</li>
        <li>Anyone who wants a simple, fast kanban board</li>
      </ul>
    </section>

    <BetaSection
      marginTop="2.5rem"
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
  .about-content {
    text-align: left;
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
    section {
      margin-bottom: 1.5rem;
    }

    h2 {
      font-size: 1.125rem;
    }
  }
</style>
