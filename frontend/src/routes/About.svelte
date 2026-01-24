<script>
  import PageLayout from '../lib/PageLayout.svelte';
  import BetaSection from '../components/BetaSection.svelte';
</script>

<PageLayout
  title="About"
  description="Building the kanban tool we wanted for orchestrating human and AI agent workflows."
>
  <div class="about-content">
    <p class="mascot-note">
      🦖 P.S. Our mascot is a pterodactyl. She's been reviewing the codebase since the Jurassic period and gives it two wings up.
    </p>

    <section>
      <h2>Our Mission</h2>
      <p>
        Most task management tools are built for humans. They assume UI-driven workflows,
        mouse-centric interactions, and manual updates. But AI agents think differently.
        (And honestly, some of us humans prefer the keyboard too.)
      </p>
      <p>
        pkanban was built from the ground up to serve both humans <strong>and</strong> AI agents.
        A CLI-first API means your agents can create boards, update cards, and manage workflows
        without ever needing to click a button. Pixel-free productivity — that's the dream.
      </p>
    </section>

    <section>
      <h2>Why "pkanban"?</h2>
      <p>
        The "p" stands for <strong>Pearachute</strong> — our domain and freelance brand.
        And just like in "pterodactyl," "psychology," and "ptarmigan," the p is <strong>silent</strong>.
        We're not lyin', we're just really excited about kanban.
      </p>
      <p>
        It started as a Python package for AI agents to manage their workflows, and evolved into
        a full-featured kanban tool that syncs between CLI and web. Now with 100% more pterodactyl.
      </p>
    </section>

    <section>
      <h2>Built For</h2>
      <div class="built-for-grid">
        <div class="built-for-card">
          <h3>🤖 AI-Powered Teams</h3>
          <p>Building workflows that orchestrate humans and agents together</p>
        </div>
        <div class="built-for-card">
          <h3>⌨️ CLI Devs</h3>
          <p>Developers who prefer the terminal (and making friends with robot overlords)</p>
        </div>
        <div class="built-for-card">
          <h3>⚙️ Automation Pipelines</h3>
          <p>Task tracking for CI/CD and agent workflows without the drag</p>
        </div>
        <div class="built-for-card">
          <h3>🚀 Simplicity Seekers</h3>
          <p>Fast, focused kanban boards without the enterprise bloat</p>
        </div>
      </div>
    </section>

    <BetaSection
      marginTop="2.5rem"
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
  .mascot-note {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    font-style: italic;
    margin-bottom: 2rem;
    padding: 0.75rem 1rem;
    background: var(--color-muted);
    border-radius: 8px;
    border-left: 3px solid var(--color-primary);
  }

  .about-content {
    text-align: left;
  }

  section {
    margin-bottom: 2rem;
  }

  h2 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-muted-foreground);
    margin: 0 0 1.5rem 0;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-variant: small-caps;
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

  .built-for-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
  }

  .built-for-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.25rem;
    transition: all 0.2s ease;
  }

  .built-for-card:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .built-for-card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .built-for-card p {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    line-height: 1.6;
    margin: 0;
  }

  @media (max-width: 640px) {
    section {
      margin-bottom: 1.5rem;
    }

    h2 {
      font-size: 0.875rem;
    }
  }
</style>
