<script>
  import { onMount, onDestroy } from 'svelte';
  import { executeCommand, getDemoState } from '$lib/demoApi';

  // Demo command sequence - uses actual CLI syntax
  const DEMO_COMMANDS = [
    'kanban board get 1',
    'kanban card create 1 "Fix API latency"',
    'kanban card update 12 "Fix API latency" --column 2',
    'kanban card update 12 "Fix API latency" --description "Optimize DB queries"'
  ];

  let displayedText = '';
  let currentLineIndex = 0;
  let currentCharIndex = 0;
  let isPaused = false;
  let showOutput = false;
  let outputLines = [];
  let commandHistory = [];
  let animationFrame;
  let timeoutId;
  let currentCommand = '';

  const TYPING_SPEED = 40;
  const PAUSE_AFTER_COMMAND = 1500;
  const PAUSE_BETWEEN_LINES = 300;

  function typeCharacter() {
    if (currentLineIndex >= DEMO_COMMANDS.length) {
      // Reset after completing all commands
      setTimeout(resetAnimation, PAUSE_AFTER_COMMAND);
      return;
    }

    currentCommand = DEMO_COMMANDS[currentLineIndex];

    if (currentCharIndex < currentCommand.length) {
      displayedText = currentCommand.substring(0, currentCharIndex + 1);
      currentCharIndex++;
      animationFrame = setTimeout(typeCharacter, TYPING_SPEED + Math.random() * 20);
    } else {
      // Command complete - execute it
      showOutput = true;
      const result = executeCommand(currentCommand);
      outputLines = result.stdout.split('\n');
      commandHistory = [...commandHistory, {
        command: currentCommand,
        output: result.stdout,
        exitCode: result.exitCode
      }];

      isPaused = true;
      timeoutId = setTimeout(() => {
        isPaused = false;
        showOutput = false;
        currentLineIndex++;
        currentCharIndex = 0;
        displayedText = '';
        // Dispatch state update for KanbanDemo
        window.dispatchEvent(new CustomEvent('demo-state-update', {
          detail: { state: getDemoState() }
        }));
        timeoutId = setTimeout(typeCharacter, PAUSE_BETWEEN_LINES);
      }, PAUSE_AFTER_COMMAND);
    }
  }

  function resetAnimation() {
    // Reset to beginning of demo
    currentLineIndex = 0;
    currentCharIndex = 0;
    displayedText = '';
    commandHistory = [];
    isPaused = false;
    showOutput = false;
    outputLines = [];
    // Reset demo state
    executeCommand('reset');
    window.dispatchEvent(new CustomEvent('demo-state-update', {
      detail: { state: getDemoState() }
    }));
    timeoutId = setTimeout(typeCharacter, PAUSE_BETWEEN_LINES);
  }

  onMount(() => {
    timeoutId = setTimeout(typeCharacter, 800);
  });

  onDestroy(() => {
    if (animationFrame) clearTimeout(animationFrame);
    if (timeoutId) clearTimeout(timeoutId);
  });
</script>

<div class="terminal-window">
  <div class="terminal-header">
    <div class="window-controls">
      <span class="control close"></span>
      <span class="control minimize"></span>
      <span class="control maximize"></span>
    </div>
    <div class="terminal-title">Terminal — zsh</div>
  </div>
  <div class="terminal-content">
    {#each commandHistory as entry}
      <div class="command-entry">
        <div class="command-line">
          <span class="prompt">➜  ~</span>
          <span class="command">{entry.command}</span>
        </div>
        <pre class="output {entry.exitCode !== 0 ? 'error' : ''}">{entry.output}</pre>
      </div>
    {/each}

    <div class="command-line">
      <span class="prompt">➜  ~</span>
      <span class="command">{displayedText}</span>
      <span class="cursor" class:hidden={isPaused}></span>
    </div>

    {#if showOutput && outputLines.length > 0}
      <pre class="output">{outputLines.join('\n')}</pre>
    {/if}
  </div>
</div>

<style>
  .terminal-window {
    width: 100%;
    height: 100%;
    min-height: 280px;
    background: var(--color-code-bg);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 25px 50px -12px color-mix(in srgb, var(--color-foreground) 20%, transparent);
    border: 1px solid var(--color-border);
  }

  .terminal-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: linear-gradient(180deg, var(--color-surface) 0%, var(--color-code-bg) 100%);
    border-bottom: 1px solid var(--color-border);
  }

  .window-controls {
    display: flex;
    gap: 8px;
  }

  .control {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }

  .control.close { background: var(--color-error); }
  .control.minimize { background: #eab308; }
  .control.maximize { background: var(--color-success); }

  .terminal-title {
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--color-muted-foreground);
    margin-left: auto;
    margin-right: auto;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
  }

  .terminal-content {
    padding: 16px 20px;
    font-family: var(--font-mono);
    font-size: 14px;
    line-height: 1.5;
    color: var(--color-code-fg);
    overflow-y: auto;
    max-height: calc(100% - 50px);
  }

  .command-entry {
    margin-bottom: 8px;
  }

  .command-entry:last-of-type {
    margin-bottom: 0;
  }

  .command-line {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .prompt {
    color: var(--color-success);
    margin-right: 8px;
    font-weight: 600;
  }

  .command {
    color: var(--color-code-fg);
  }

  .output {
    margin: 4px 0 8px 24px;
    color: var(--color-muted-foreground);
    font-size: 13px;
    white-space: pre-wrap;
    line-height: 1.4;
  }

  .output.error {
    color: var(--color-error);
  }

  .cursor {
    display: inline-block;
    width: 8px;
    height: 18px;
    background: var(--color-success);
    margin-left: 2px;
    animation: blink 1s step-end infinite;
    vertical-align: middle;
  }

  .cursor.hidden {
    opacity: 0;
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  @media (max-width: 768px) {
    .terminal-window {
      min-height: 200px;
    }

    .terminal-content {
      font-size: 13px;
      padding: 12px 16px;
    }

    .output {
      margin-left: 20px;
      font-size: 12px;
    }
  }
</style>
