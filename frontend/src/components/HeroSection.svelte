<script>
  import TerminalSimulator from './TerminalSimulator.svelte';
  import KanbanDemo from './KanbanDemo.svelte';

  function copyInstallCommand() {
    navigator.clipboard.writeText('pip install pkanban');
  }
</script>

<section class="hero-section">
  <div class="hero-content">
    <div class="text-content">
      <h1 class="headline">The Universal Interface for Agents & Humans.</h1>
      <p class="subhead">Orchestrate your AI agents using the universal language of compute: Standard Input/Output. No SDKs, just commands.</p>

      <button class="install-button" onclick={copyInstallCommand}>
        <span class="button-icon">⬡</span>
        <code class="button-command">pip install pkanban</code>
        <span class="button-copy">Copy</span>
      </button>
    </div>

    <div class="demo-container">
      <div class="demo-grid">
        <div class="demo-terminal">
          <TerminalSimulator />
        </div>
        <div class="demo-board">
          <KanbanDemo />
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .hero-section {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 60px 24px;
    background: linear-gradient(
      180deg,
      var(--color-background) 0%,
      color-mix(in srgb, var(--color-primary) 10%, transparent) 50%,
      var(--color-background) 100%
    );
    position: relative;
    overflow: hidden;
  }

  .hero-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
      radial-gradient(ellipse 80% 50% at 50% -20%, color-mix(in srgb, var(--color-primary) 15%, transparent) 0%, transparent 50%),
      radial-gradient(ellipse 60% 40% at 80% 60%, color-mix(in srgb, var(--color-success) 8%, transparent) 0%, transparent 40%);
    pointer-events: none;
  }

  .hero-content {
    max-width: 1200px;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 48px;
    position: relative;
    z-index: 1;
  }

  .text-content {
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
  }

  .headline {
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 20px 0;
    line-height: 1.15;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, var(--color-foreground) 0%, var(--color-muted-foreground) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subhead {
    font-size: 1.25rem;
    color: var(--color-muted-foreground);
    margin: 0 0 32px 0;
    line-height: 1.6;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }

  .install-button {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 14px 24px;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: var(--font-mono);
  }

  .install-button:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px color-mix(in srgb, var(--color-primary) 15%, transparent);
  }

  .button-icon {
    font-size: 18px;
    color: var(--color-primary);
  }

  .button-command {
    font-size: 15px;
    color: var(--color-foreground);
    font-weight: 500;
    background: transparent;
    padding: 0;
  }

  .button-copy {
    font-size: 12px;
    color: var(--color-muted-foreground);
    padding: 4px 10px;
    background: color-mix(in srgb, var(--color-foreground) 5%, transparent);
    border-radius: 6px;
    transition: all 0.2s ease;
  }

  .install-button:hover .button-copy {
    color: var(--color-foreground);
    background: color-mix(in srgb, var(--color-foreground) 10%, transparent);
  }

  .demo-container {
    width: 100%;
  }

  .demo-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    min-height: 400px;
  }

  .demo-terminal,
  .demo-board {
    position: relative;
  }

  @media (max-width: 1024px) {
    .headline {
      font-size: 2.75rem;
    }

    .subhead {
      font-size: 1.125rem;
    }

    .demo-grid {
      grid-template-columns: 1fr;
      gap: 16px;
      min-height: 700px;
    }
  }

  @media (max-width: 640px) {
    .hero-section {
      padding: 40px 16px;
    }

    .headline {
      font-size: 2rem;
    }

    .subhead {
      font-size: 1rem;
    }

    .install-button {
      width: 100%;
      justify-content: center;
      padding: 12px 20px;
    }

    .button-command {
      font-size: 13px;
    }

    .demo-grid {
      min-height: 600px;
    }
  }
</style>
