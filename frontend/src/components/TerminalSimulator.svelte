<script>
  import { onMount, onDestroy } from 'svelte';

  const COMMANDS = [
    { text: 'pkanban add "Fix API latency"', action: 'add' },
    { text: 'pkanban move 12 --to "In Progress"', action: 'move' }
  ];

  let displayedText = '';
  let currentLineIndex = 0;
  let currentCharIndex = 0;
  let isPaused = false;
  let animationFrame;
  let timeoutId;

  const TYPING_SPEED = 50;
  const PAUSE_AFTER_COMMAND = 2000;
  const PAUSE_BETWEEN_LINES = 500;

  function typeCharacter() {
    if (currentLineIndex >= COMMANDS.length) {
      // Reset animation after completing all lines
      setTimeout(resetAnimation, PAUSE_AFTER_COMMAND);
      return;
    }

    const currentLine = COMMANDS[currentLineIndex].text;

    if (currentCharIndex < currentLine.length) {
      displayedText = currentLine.substring(0, currentCharIndex + 1);
      currentCharIndex++;
      animationFrame = setTimeout(typeCharacter, TYPING_SPEED);
    } else {
      // Line complete, dispatch event and pause
      dispatchCommand(COMMANDS[currentLineIndex].action);
      isPaused = true;
      timeoutId = setTimeout(() => {
        isPaused = false;
        currentLineIndex++;
        currentCharIndex = 0;
        displayedText = '';
        timeoutId = setTimeout(typeCharacter, PAUSE_BETWEEN_LINES);
      }, PAUSE_AFTER_COMMAND);
    }
  }

  function resetAnimation() {
    currentLineIndex = 0;
    currentCharIndex = 0;
    displayedText = '';
    isPaused = false;
    timeoutId = setTimeout(typeCharacter, PAUSE_BETWEEN_LINES);
  }

  function dispatchCommand(action) {
    window.dispatchEvent(new CustomEvent('terminal-command', { detail: { action } }));
  }

  onMount(() => {
    timeoutId = setTimeout(typeCharacter, 1000);
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
    <div class="command-line">
      <span class="prompt">➜  ~</span>
      <span class="command">{displayedText}</span>
      <span class="cursor" class:hidden={isPaused}></span>
    </div>
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
    line-height: 1.6;
    color: var(--color-code-fg);
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
  }
</style>
