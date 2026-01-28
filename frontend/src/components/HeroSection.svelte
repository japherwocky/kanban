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
    background: linear-gradient(180deg, #0a0a0f 0%, #0f172a 50%, #0a0a0f 100%);
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
      radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
      radial-gradient(ellipse 60% 40% at 80% 60%, rgba(34, 197, 94, 0.08) 0%, transparent 40%);
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
    color: #f8fafc;
    margin: 0 0 20px 0;
    line-height: 1.15;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subhead {
    font-size: 1.25rem;
    color: #64748b;
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
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
  }

  .install-button:hover {
    border-color: rgba(59, 130, 246, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(59, 130, 246, 0.15);
  }

  .button-icon {
    font-size: 18px;
    color: #3b82f6;
  }

  .button-command {
    font-size: 15px;
    color: #e2e8f0;
    font-weight: 500;
    background: transparent;
    padding: 0;
  }

  .button-copy {
    font-size: 12px;
    color: #64748b;
    padding: 4px 10px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    transition: all 0.2s ease;
  }

  .install-button:hover .button-copy {
    color: #94a3b8;
    background: rgba(255, 255, 255, 0.1);
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
