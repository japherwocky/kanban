<script>
  import { fade, fly } from 'svelte/transition';

  let hoveredBox = $state(null);
  let mouseX = $state(0);
  let mouseY = $state(0);

  const logos = [
    { name: 'LangChain', color: '#0F172A' },
    { name: 'AutoGPT', color: '#4B0082' },
    { name: 'CrewAI', color: '#1E3A5F' },
    { name: 'OpenAI', color: '#10A37F' },
    { name: 'Anthropic', color: '#D4A574' }
  ];

  function handleMouseMove(event, boxId) {
    if (hoveredBox === boxId) {
      const rect = event.currentTarget.getBoundingClientRect();
      mouseX = ((event.clientX - rect.left) / rect.width) * 100;
      mouseY = ((event.clientY - rect.top) / rect.height) * 100;
    }
  }
</script>

<section class="features-section">
  <div class="features-header">
    <h2>Engineered for Autonomy</h2>
    <p>Every design decision optimized for AI agents and their human overseers.</p>
  </div>

  <div class="bento-grid">
    <!-- Box 1: Zero-Config Handshake (Large) -->
    <div
      class="bento-box box-large"
      class:hovered={hoveredBox === 1}
      onmouseenter={() => hoveredBox = 1}
      onmouseleave={() => hoveredBox = null}
      onmousemove={(e) => handleMouseMove(e, 1)}
      role="group"
      aria-label="Zero-Config Handshake feature"
    >
      <div class="box-content">
        <div class="box-header">
          <span class="box-icon">🔐</span>
          <h3>Zero-Config Handshake</h3>
        </div>
        <p class="box-description">Connect agents without OAuth dancing or API key management.</p>

        <div class="code-panel">
          <div class="code-line">
            <span class="code-keyword">class</span> <span class="code-type">Agent</span>:
          </div>
          <div class="code-line code-indent">
            <span class="code-keyword">def</span> <span class="code-function">__init__</span>(self):
          </div>
          <div
            class="code-line code-indent highlight"
            class:active={hoveredBox === 1}
          >
            &nbsp;&nbsp;&nbsp;&nbsp;api_key = <span class="code-string">None</span>  <span class="code-comment"># Auto-discovered</span>
          </div>
          <div class="code-line code-indent">
            &nbsp;&nbsp;&nbsp;&nbsp;endpoint = <span class="code-string">"wss://pkanban.io/stream"</span>
          </div>
        </div>
      </div>

      <div class="glow-spot" style="left: {mouseX}%; top: {mouseY}%"></div>
    </div>

    <!-- Box 2: LLM-Optimized Structure (Tall) -->
    <div
      class="bento-box box-tall"
      class:hovered={hoveredBox === 2}
      onmouseenter={() => hoveredBox = 2}
      onmouseleave={() => hoveredBox = null}
      onmousemove={(e) => handleMouseMove(e, 2)}
      role="group"
      aria-label="LLM-Optimized Structure feature"
    >
      <div class="box-content">
        <div class="box-header">
          <span class="box-icon">🧠</span>
          <h3>LLM-Optimized Structure</h3>
        </div>
        <p class="box-description">A hierarchy designed for context windows, not just human eyes.</p>

        <div class="structure-display">
          <div class="json-tree">
            <div class="json-line"><span class="json-brace">{'{'}</span></div>
            <div class="json-line code-indent"><span class="json-key">"board"</span>: <span class="json-string">"Sprint-24"</span>,</div>
            <div class="json-line code-indent"><span class="json-key">"columns"</span>: [</div>
            <div class="json-line code-indent-2"><span class="json-string">"Todo"</span>,</div>
            <div class="json-line code-indent-2"><span class="json-string">"In Progress"</span>,</div>
            <div class="json-line code-indent-2"><span class="json-string">"Done"</span></div>
            <div class="json-line code-indent"><span class="json-brace">]</span>,</div>
            <div class="json-line code-indent"><span class="json-key">"cards"</span>: <span class="json-number">3</span></div>
            <div class="json-line"><span class="json-brace">{'}'}</span></div>
          </div>

          <div class="robot-scanner" class:scanning={hoveredBox === 2}>
            <svg viewBox="0 0 100 100" class="robot-icon">
              <rect x="20" y="30" width="60" height="40" rx="5" fill="none" stroke="currentColor" stroke-width="2"/>
              <rect x="35" y="15" width="30" height="20" rx="3" fill="none" stroke="currentColor" stroke-width="2"/>
              <circle cx="50" cy="50" r="8" fill="none" stroke="currentColor" stroke-width="2"/>
              <line x1="50" y1="50" x2="50" y2="70" stroke="currentColor" stroke-width="2" class="scanner-beam"/>
            </svg>
          </div>
        </div>
      </div>

      <div class="glow-spot" style="left: {mouseX}%; top: {mouseY}%"></div>
    </div>

    <!-- Box 3: Works where your Agents live (Wide) -->
    <div
      class="bento-box box-wide"
      class:hovered={hoveredBox === 3}
      onmouseenter={() => hoveredBox = 3}
      onmouseleave={() => hoveredBox = null}
      onmousemove={(e) => handleMouseMove(e, 3)}
      role="group"
      aria-label="Integration partners"
    >
      <div class="box-content">
        <div class="box-header">
          <span class="box-icon">🔗</span>
          <h3>Works where your Agents live</h3>
        </div>
        <p class="box-description">Seamless integration with the tools powering your AI workforce.</p>

        <div class="logo-marquee">
          <div class="logo-track" class:paused={hoveredBox !== 3}>
            {#each [...logos, ...logos, ...logos] as logo, i}
              <div
                class="logo-item"
                class:colored={hoveredBox === 3}
                style="--logo-color: {logo.color}"
              >
                <span class="logo-text">{logo.name}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>

      <div class="glow-spot" style="left: {mouseX}%; top: {mouseY}%"></div>
    </div>
  </div>
</section>

<style>
  .features-section {
    max-width: 1200px;
    width: 100%;
    margin: 4rem auto;
    padding: 0 24px;
  }

  .features-header {
    text-align: center;
    margin-bottom: 3rem;
  }

  .features-header h2 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 1rem 0;
  }

  .features-header p {
    font-size: 1.125rem;
    color: var(--color-muted-foreground);
    margin: 0;
  }

  .bento-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    grid-template-rows: auto auto;
    gap: 20px;
  }

  .bento-box {
    position: relative;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    overflow: hidden;
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .bento-box:hover {
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateY(-4px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  }

  .bento-box.hovered {
    border-color: rgba(59, 130, 246, 0.5);
  }

  .glow-spot {
    position: absolute;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
    transform: translate(-50%, -50%);
    transition: opacity 0.3s ease;
    opacity: 0;
  }

  .bento-box.hovered .glow-spot {
    opacity: 1;
  }

  .box-content {
    position: relative;
    z-index: 1;
  }

  .box-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .box-icon {
    font-size: 24px;
  }

  .box-header h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0;
  }

  .box-description {
    font-size: 0.9375rem;
    color: var(--color-muted-foreground);
    margin: 0 0 1.5rem 0;
    line-height: 1.6;
  }

  /* Box Large */
  .box-large {
    grid-column: span 8;
    grid-row: span 1;
  }

  /* Box Tall */
  .box-tall {
    grid-column: span 4;
    grid-row: span 2;
  }

  /* Box Wide */
  .box-wide {
    grid-column: span 8;
    grid-row: span 1;
  }

  /* Code Panel Styles */
  .code-panel {
    background: #0f172a;
    border-radius: 8px;
    padding: 16px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
    line-height: 1.6;
  }

  .code-line {
    color: #64748b;
  }

  .code-indent {
    padding-left: 24px;
  }

  .code-indent-2 {
    padding-left: 48px;
  }

  .code-keyword { color: #c084fc; }
  .code-type { color: #60a5fa; }
  .code-function { color: #fbbf24; }
  .code-string { color: #4ade80; }
  .code-comment { color: #475569; }

  .code-line.highlight {
    background: rgba(74, 222, 128, 0.1);
    margin: 0 -16px;
    padding: 0 16px;
    border-left: 3px solid #4ade80;
    color: #e2e8f0;
    transition: all 0.2s ease;
  }

  .code-line.highlight.active {
    background: rgba(74, 222, 128, 0.2);
  }

  /* JSON Tree Styles */
  .structure-display {
    display: flex;
    gap: 20px;
    align-items: flex-start;
  }

  .json-tree {
    flex: 1;
    background: #0f172a;
    border-radius: 8px;
    padding: 16px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
    line-height: 1.8;
  }

  .json-line { color: #64748b; }
  .json-brace { color: #94a3b8; }
  .json-key { color: #60a5fa; }
  .json-string { color: #4ade80; }
  .json-number { color: #fbbf24; }

  .robot-scanner {
    width: 60px;
    height: 60px;
    color: #64748b;
    transition: all 0.3s ease;
  }

  .robot-scanner.scanning {
    color: #3b82f6;
  }

  .robot-icon {
    width: 100%;
    height: 100%;
  }

  .scanner-beam {
    opacity: 0;
    transition: opacity 0.3s ease;
  }

  .robot-scanner.scanning .scanner-beam {
    opacity: 1;
    animation: scan 1s ease-in-out infinite;
  }

  @keyframes scan {
    0%, 100% { transform: translateY(0); opacity: 0.5; }
    50% { transform: translateY(20px); opacity: 1; }
  }

  /* Logo Marquee Styles */
  .logo-marquee {
    overflow: hidden;
    padding: 16px 0;
  }

  .logo-track {
    display: flex;
    gap: 32px;
    animation: scroll 20s linear infinite;
  }

  .logo-track.paused {
    animation-play-state: paused;
  }

  @keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
  }

  .logo-item {
    flex-shrink: 0;
    padding: 12px 24px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    color: #64748b;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.3s ease;
  }

  .logo-item:hover,
  .logo-item.colored {
    background: rgba(255, 255, 255, 0.08);
    color: var(--logo-color, #3b82f6);
    border-color: rgba(255, 255, 255, 0.12);
  }

  .logo-text {
    white-space: nowrap;
  }

  /* Responsive */
  @media (max-width: 1024px) {
    .box-large,
    .box-wide {
      grid-column: span 12;
    }

    .box-tall {
      grid-column: span 12;
      grid-row: span 1;
    }

    .structure-display {
      flex-direction: column;
      align-items: center;
    }
  }

  @media (max-width: 640px) {
    .features-section {
      padding: 0 16px;
    }

    .features-header h2 {
      font-size: 1.75rem;
    }

    .features-header p {
      font-size: 1rem;
    }

    .bento-grid {
      gap: 16px;
    }

    .bento-box {
      padding: 20px;
    }

    .box-header h3 {
      font-size: 1.125rem;
    }

    .code-panel,
    .json-tree {
      font-size: 11px;
    }
  }
</style>
