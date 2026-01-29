<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import ThemeToggle from './ThemeToggle.svelte';

  let isMenuOpen = $state(false);
  let isUserMenuOpen = $state(false);
  let isLoggedIn = $state(false);
  let username = $state('');

  onMount(() => {
    checkAuth();
  });

  function checkAuth() {
    const token = localStorage.getItem('token');
    isLoggedIn = !!token;
    // Get username from token or storage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        username = user.username || '';
      } catch (e) {
        // Ignore parse errors
      }
    }
  }

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  function closeMenu() {
    isMenuOpen = false;
  }

  function goTo(path) {
    navigate(path);
    closeMenu();
    isUserMenuOpen = false;
  }

  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    isLoggedIn = false;
    isUserMenuOpen = false;
    navigate('/');
  }
</script>

<header class="header">
  <div class="header-container">
    <!-- Logo -->
    <button class="logo" onclick={() => goTo('/')}>
      <svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="8" y="8" width="48" height="48" rx="8" stroke="currentColor" stroke-width="3" fill="none"/>
        <rect x="16" y="20" width="12" height="8" rx="2" fill="currentColor"/>
        <rect x="16" y="32" width="12" height="8" rx="2" fill="currentColor"/>
        <rect x="32" y="20" width="12" height="8" rx="2" fill="currentColor"/>
        <rect x="48" y="20" width="4" height="8" rx="2" fill="currentColor"/>
      </svg>
      <span>pkanban</span>
    </button>

    <!-- Desktop Nav -->
    <nav class="nav-desktop">
      <button onclick={() => goTo('/docs')}>Documentation</button>
      <button onclick={() => goTo('/pricing')}>Pricing</button>
      <button onclick={() => goTo('/about')}>About</button>
    </nav>

    <!-- Right Side -->
    <div class="header-right">
      <ThemeToggle />

      {#if isLoggedIn}
        <div class="user-menu-container">
          <button
            class="user-menu-trigger"
            onclick={() => isUserMenuOpen = !isUserMenuOpen}
            aria-expanded={isUserMenuOpen}
          >
            <span class="user-avatar">{username ? username[0].toUpperCase() : 'U'}</span>
            <span class="username">{username || 'User'}</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M4 6l4 4 4-4" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          {#if isUserMenuOpen}
            <div class="user-menu-dropdown">
              <button class="dropdown-item" onclick={() => goTo('/settings/api-keys')}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="10" height="10" rx="1.5"/>
                  <path d="M6 6.5v3a1.5 1.5 0 001.5 1.5h1"/>
                </svg>
                API Keys
              </button>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout" onclick={logout}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M10.5 3.5L6.5 7.5l4 4"/>
                  <path d="M13 12.5h-5a2 2 0 01-2-2V9a2 2 0 012-2h5"/>
                </svg>
                Log out
              </button>
            </div>
          {/if}
        </div>
      {:else}
        <div class="auth-buttons">
          <button class="btn-secondary" onclick={() => goTo('/login')}>Log in</button>
          <button class="btn-primary" onclick={() => goTo('/login')}>Sign up</button>
        </div>
      {/if}

      <!-- Mobile Menu Button -->
      <button class="mobile-toggle" onclick={toggleMenu} aria-label="Toggle menu">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          {#if isMenuOpen}
            <path d="M18 6L6 18M6 6l12 12" />
          {:else}
            <path d="M3 12h18M3 6h18M3 18h18" />
          {/if}
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile Nav -->
  {#if isMenuOpen}
    <nav class="nav-mobile">
      <button onclick={() => goTo('/docs')}>Documentation</button>
      <button onclick={() => goTo('/pricing')}>Pricing</button>
      <button onclick={() => goTo('/about')}>About</button>
      <button onclick={() => goTo('/about')}>Contact</button>
      <div class="mobile-divider"></div>
      <button onclick={() => goTo('/login')}>Log in</button>
      <button onclick={() => goTo('/login')}>Sign up</button>
    </nav>
  {/if}
</header>

<style>
  .header {
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--color-background);
    border-bottom: 1px solid var(--color-border);
  }

  .header-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    color: var(--color-foreground);
    font-size: 1.25rem;
    font-weight: 600;
    cursor: pointer;
    padding: 0;
    transition: opacity 0.15s ease;
  }

  .logo:hover {
    opacity: 0.8;
  }

  .logo svg {
    color: var(--color-primary);
  }

  .nav-desktop {
    display: none;
    align-items: center;
    gap: 0.5rem;
  }

  .nav-desktop button {
    background: none;
    border: none;
    color: var(--color-muted-foreground);
    font-size: 0.9375rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    transition: all 0.15s ease;
  }

  .nav-desktop button:hover {
    color: var(--color-foreground);
    background: var(--color-muted);
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .auth-buttons {
    display: none;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-secondary {
    background: none;
    border: none;
    color: var(--color-muted-foreground);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0.5rem 0.875rem;
    border-radius: 6px;
    transition: all 0.15s ease;
  }

  .btn-secondary:hover {
    color: var(--color-foreground);
    background: var(--color-muted);
  }

  .btn-primary {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0.5rem 0.875rem;
    border-radius: 6px;
    transition: all 0.15s ease;
  }

  .btn-primary:hover {
    opacity: 0.9;
  }

  .mobile-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: none;
    border: 1px solid var(--color-border);
    border-radius: 8px;
    color: var(--color-foreground);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .mobile-toggle:hover {
    background: var(--color-muted);
  }

  .nav-mobile {
    display: flex;
    flex-direction: column;
    padding: 0.75rem 1.5rem 1rem;
    border-top: 1px solid var(--color-border);
  }

  .nav-mobile button {
    background: none;
    border: none;
    color: var(--color-muted-foreground);
    font-size: 0.9375rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0.75rem 0;
    text-align: left;
    transition: color 0.15s ease;
  }

  .nav-mobile button:hover {
    color: var(--color-foreground);
  }

  .mobile-divider {
    height: 1px;
    background: var(--color-border);
    margin: 0.5rem 0;
  }

  .user-menu-container {
    position: relative;
  }

  .user-menu-trigger {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.375rem 0.75rem 0.375rem 0.5rem;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    color: var(--color-foreground);
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.15s ease;
  }

  .user-menu-trigger:hover {
    background: var(--color-muted);
  }

  .user-avatar {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.875rem;
  }

  .username {
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .user-menu-dropdown {
    position: absolute;
    top: calc(100% + 4px);
    right: 0;
    min-width: 180px;
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    padding: 0.375rem;
    z-index: 50;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    width: 100%;
    padding: 0.625rem 0.75rem;
    background: transparent;
    border: none;
    border-radius: 6px;
    color: var(--color-foreground);
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    text-align: left;
  }

  .dropdown-item:hover {
    background: var(--color-muted);
  }

  .dropdown-item.logout {
    color: var(--color-error);
  }

  .dropdown-item.logout:hover {
    background: rgba(239, 68, 68, 0.1);
  }

  .dropdown-divider {
    height: 1px;
    background: var(--color-border);
    margin: 0.375rem 0;
  }

  @media (min-width: 768px) {
    .nav-desktop {
      display: flex;
    }

    .auth-buttons {
      display: flex;
    }

    .mobile-toggle {
      display: none;
    }

    .nav-mobile {
      display: none !important;
    }
  }
</style>
