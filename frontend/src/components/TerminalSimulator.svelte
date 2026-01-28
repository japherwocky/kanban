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
    background: #0f172a;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .terminal-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
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

  .control.close { background: #ef4444; }
  .control.minimize { background: #eab308; }
  .control.maximize { background: #22c55e; }

  .terminal-title {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
    color: #64748b;
    margin-left: auto;
    margin-right: auto;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
  }

  .terminal-content {
    padding: 16px 20px;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: #e2e8f0;
  }

  .command-line {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .prompt {
    color: #22c55e;
    margin-right: 8px;
    font-weight: 600;
  }

  .command {
    color: #f1f5f9;
  }

  .cursor {
    display: inline-block;
    width: 8px;
    height: 18px;
    background: #22c55e;
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
