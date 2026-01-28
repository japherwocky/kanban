<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
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
  <div class="hero">
    <div class="logo">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="8" width="48" height="48" rx="8" stroke="currentColor" stroke-width="3" fill="none"/>
        <rect x="16" y="20" width="12" height="8" rx="2" fill="currentColor"/>
        <rect x="16" y="32" width="12" height="8" rx="2" fill="currentColor"/>
        <rect x="32" y="20" width="12" height="8" rx="2" fill="currentColor"/>
        <rect x="48" y="20" width="4" height="8" rx="2" fill="currentColor"/>
      </svg>
    </div>
    
    <h1>Orchestrate Your Agents</h1>

    <p class="tagline">
      A kanban board that speaks both CLI and Web.
      Perfect for humans and AI agents working together.
    </p>

    <button class="cta-button" onclick={goToLogin}>
      Start Managing Tasks
    </button>

    <div class="features">
      <div class="feature featured">
        <h3>🤖 Agent-First CLI</h3>
        <p>pip install pkanban → agents can read/write boards instantly</p>
      </div>
      <div class="feature">
        <h3>⌨️ Command-Line Speed</h3>
        <p>kanban board-create, card-create, card-update - no UI friction</p>
      </div>
      <div class="feature">
        <h3>🌐 Web + CLI Sync</h3>
        <p>Same boards, same data - choose your interface</p>
      </div>
      <div class="feature">
        <h3>👥 Team Sharing</h3>
        <p>Organizations, teams, permissions - humans + agents collaborate</p>
      </div>
    </div>

    <div class="code-demo">
      <div class="code-header">
        <span class="code-badge">$</span>
        <span class="code-title">Agent commands</span>
      </div>
      <pre><code>pip install pkanban
kanban config --url https://kanban.pearachute.com
kanban login agent-name --password ***
kanban board-create "AI Research Sprint"
kanban card-create 1 "Implement RAG pipeline" --position 0
kanban card-create 1 "Add vector search" --position 1
kanban board 1</code></pre>
    </div>

    <div class="cta-secondary">
      <button class="link-button" onclick={goToQuickstart}>Quick Start Guide</button>
      <span>•</span>
      <button class="link-button" onclick={goToReference}>CLI Reference</button>
      <span>•</span>
      <button class="link-button" onclick={goToDocs}>Full Documentation</button>
    </div>

    <p class="login-prompt">
      Already have an account? <button class="link-button" onclick={goToLogin}>Sign in</button>
    </p>
  </div>

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

  .hero {
    max-width: 900px;
    width: 100%;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }

  .logo {
    color: var(--color-primary);
    margin-bottom: 0.5rem;
    animation: float 3s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  h1 {
    font-size: 3rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0;
    line-height: 1.2;
  }

  .tagline {
    font-size: 1.25rem;
    color: var(--color-muted-foreground);
    margin: 0;
    line-height: 1.6;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 1rem 0;
  }

  .feature {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1.5rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    transition: all 0.2s ease;
  }

  .feature.featured {
    border: 2px solid var(--color-primary);
    background: linear-gradient(135deg, var(--color-card) 0%, rgba(var(--color-primary-rgb), 0.1) 100%);
  }

  .feature.featured .feature-icon {
    font-size: 2.5rem;
  }

  .feature.featured strong {
    color: var(--color-primary);
  }

  .feature:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .feature h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .feature p {
    font-size: 0.9375rem;
    color: var(--color-muted-foreground);
    line-height: 1.6;
    margin: 0;
  }

  .code-demo {
    margin: 1.5rem 0;
    background: #1e1e1e;
    border-radius: 8px;
    overflow: hidden;
    width: 100%;
    max-width: 600px;
  }

  .code-header {
    background: #2d2d2d;
    padding: 0.5rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-bottom: 1px solid #3d3d3d;
  }

  .code-badge {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .code-title {
    color: #9ca3af;
    font-size: 0.875rem;
  }

  .code-demo pre {
    margin: 0;
    padding: 1rem;
    overflow-x: auto;
    background: #1e1e1e;
    color: #d4d4d4;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .code-demo code {
    background: transparent;
    padding: 0;
  }

  .cta-secondary {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 1rem 0;
    color: var(--color-muted-foreground);
    font-size: 0.875rem;
  }

  .cta-button {
    margin-top: 1rem;
    padding: 1rem 3rem;
    font-size: 1.125rem;
    font-weight: 600;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .cta-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  .cta-button:active {
    transform: translateY(0);
  }

  .login-prompt {
    margin-top: 0.5rem;
    color: var(--color-muted-foreground);
    font-size: 0.875rem;
  }

  .link-button {
    background: none;
    border: none;
    color: var(--color-primary);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0;
    text-decoration: underline;
    transition: opacity 0.2s ease;
  }

  .link-button:hover {
    opacity: 0.8;
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
    h1 {
      font-size: 2rem;
    }

    .tagline {
      font-size: 1rem;
    }

    .features {
      gap: 1rem;
    }

    .feature {
      padding: 0.75rem;
    }

    .cta-button {
      padding: 0.875rem 2rem;
      font-size: 1rem;
    }

    .agent-cards {
      grid-template-columns: 1fr;
    }

    .agent-section h2 {
      font-size: 1.5rem;
    }

    .agent-description {
      font-size: 1rem;
    }

    .code-demo {
      font-size: 0.75rem;
    }

    .cta-secondary {
      flex-direction: column;
      gap: 0.5rem;
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

