<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import ThemeToggle from '../lib/ThemeToggle.svelte';

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
</script>

<div class="landing">
  <div class="theme-toggle-wrapper">
    <ThemeToggle />
  </div>
  
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
    
    <h1>Kanban Board</h1>
    
    <p class="tagline">
      Organize your work, collaborate with your team, and get things done.
    </p>
    
    <div class="features">
      <div class="feature">
        <span class="feature-icon">📋</span>
        <span>Create unlimited boards</span>
      </div>
      <div class="feature">
        <span class="feature-icon">👥</span>
        <span>Team collaboration</span>
      </div>
      <div class="feature">
        <span class="feature-icon">🎨</span>
        <span>Customize your workflow</span>
      </div>
    </div>
    
    <button class="cta-button" onclick={goToLogin}>
      Get Started
    </button>
    
    <p class="login-prompt">
      Already have an account? <button class="link-button" onclick={goToLogin}>Sign in</button>
    </p>
  </div>
</div>

<style>
  .landing {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    background: var(--color-background);
    position: relative;
  }

  .theme-toggle-wrapper {
    position: absolute;
    top: 1.5rem;
    right: 1.5rem;
  }

  .hero {
    max-width: 600px;
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
    display: flex;
    gap: 2rem;
    margin: 1rem 0;
    flex-wrap: wrap;
    justify-content: center;
  }

  .feature {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    min-width: 140px;
    transition: all 0.2s ease;
  }

  .feature:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .feature-icon {
    font-size: 2rem;
  }

  .feature span:last-child {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    text-align: center;
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
      min-width: 120px;
      padding: 0.75rem;
    }

    .cta-button {
      padding: 0.875rem 2rem;
      font-size: 1rem;
    }
  }
</style>

