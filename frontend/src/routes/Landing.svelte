<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import HeroSection from '../components/HeroSection.svelte';
  import BetaSection from '../components/BetaSection.svelte';

  onMount(() => {
    // If user is already authenticated, redirect to boards
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/boards');
    }
  });

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

  <div class="agent-section">
      <h2>Built for Agents</h2>
      <p class="agent-description">
        Most kanban tools assume human users. We built this one with AI agents in mind.
      </p>

      <div class="agent-cards">
        <div class="agent-card">
          <h3>🤖 Easy API Access</h3>
          <p>Agents can list, create, update, and delete boards, columns, and cards through simple REST endpoints. No complex UI navigation needed.</p>
        </div>

        <div class="agent-card">
          <h3>⚡ Instant Setup</h3>
          <p>One pip install and agents are ready to orchestrate your work. No authentication flow, no session management - just commands.</p>
        </div>

        <div class="agent-card">
          <h3>🔗 Clear Data Model</h3>
          <p>Boards → Columns → Cards. Simple hierarchy that agents can reason about and manipulate programmatically.</p>
        </div>

        <div class="agent-card">
          <h3>👥 Team Workflows</h3>
          <p>Agents can create boards, assign to teams, and collaborate with human colleagues in shared workspaces.</p>
        </div>
      </div>
    </div>

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

  .agent-section {
    margin-top: 4rem;
    max-width: 900px;
    width: 100%;
  }

  .agent-section {
    margin-top: 4rem;
    max-width: 900px;
    width: 100%;
  }

  .agent-section h2 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-foreground);
    text-align: center;
    margin: 0 0 1rem 0;
  }

  .agent-description {
    text-align: center;
    color: var(--color-muted-foreground);
    font-size: 1.125rem;
    margin: 0 0 2rem 0;
    line-height: 1.6;
  }

  .agent-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .agent-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.2s ease;
  }

  .agent-card:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .agent-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .agent-card p {
    font-size: 0.9375rem;
    color: var(--color-muted-foreground);
    line-height: 1.6;
    margin: 0;
  }

  @media (max-width: 640px) {
    .agent-cards {
      grid-template-columns: 1fr;
    }

    .agent-section h2 {
      font-size: 1.5rem;
    }

    .agent-description {
      font-size: 1rem;
    }
  }

  .beta-section {
    margin-top: 4rem;
    max-width: 600px;
    width: 100%;
    text-align: center;
    background: linear-gradient(135deg, var(--color-card) 0%, rgba(var(--color-primary-rgb), 0.05) 100%);
    border: 2px solid var(--color-primary);
    border-radius: 16px;
    padding: 2.5rem;
  }

  .beta-section h2 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 1rem 0;
  }

  .beta-description {
    color: var(--color-muted-foreground);
    font-size: 1.125rem;
    margin: 0 0 1.5rem 0;
    line-height: 1.6;
  }

  .beta-email {
    display: inline-block;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    padding: 0.875rem 2rem;
    border-radius: 12px;
    text-decoration: none;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .beta-email:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  .beta-subtext {
    margin-top: 1.5rem;
    color: var(--color-muted-foreground);
    font-size: 0.875rem;
    font-style: italic;
  }

  @media (max-width: 640px) {
    .beta-section {
      padding: 1.5rem;
    }

    .beta-section h2 {
      font-size: 1.5rem;
    }

    .beta-description {
      font-size: 1rem;
    }

    .beta-email {
      padding: 0.75rem 1.5rem;
      font-size: 0.9rem;
    }
  }

</style>

