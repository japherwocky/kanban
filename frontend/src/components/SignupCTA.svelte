<script>
  import { link } from 'svelte-routing';

  // Sizing knobs. Every page that renders this wants a slightly different
  // scale -- the landing page gets the full-size version, Login gets a
  // compact one under the form -- so the dimensions come in as props rather
  // than being forked into per-page copies of the markup.
  let {
    marginTop = '4rem',
    // Off on the login page, where "already have an account?" is noise --
    // they are looking at the login form.
    showLoginLink = true,
    maxWidth = null,
    borderRadius = '20px',
    padding = '3rem',
    h2FontSize = '2rem',
    descFontSize = '1.125rem',
    subtextFontSize = '0.875rem',
    mobilePadding = '1.5rem',
    mobileH2FontSize = '1.5rem',
    mobileDescFontSize = '1rem',
    compactPadding = '1rem',
    compactH2FontSize = '1.25rem',
    compactDescFontSize = '0.875rem'
  } = $props();
</script>

<div
  class="signup-cta"
  style="
    --margin-top: {marginTop};
    --max-width: {maxWidth ?? 'none'};
    --border-radius: {borderRadius};
    --padding: {padding};
    --h2-font-size: {h2FontSize};
    --desc-font-size: {descFontSize};
    --subtext-font-size: {subtextFontSize};
    --mobile-padding: {mobilePadding};
    --mobile-h2-font-size: {mobileH2FontSize};
    --mobile-desc-font-size: {mobileDescFontSize};
    --compact-padding: {compactPadding};
    --compact-h2-font-size: {compactH2FontSize};
    --compact-desc-font-size: {compactDescFontSize};
  "
>
  <div class="cta-background"></div>
  <div class="cta-content">
    <h2>Initialize Your Workspace</h2>
    <p class="cta-description">
      Create an account and start orchestrating agents in minutes.
    </p>

    <a href="/signup" use:link class="cta-button">
      <span class="button-prompt">$</span>
      <span class="button-text">create_account</span>
    </a>

    <p class="cta-subtext">
      {#if showLoginLink}
        Free to start. Already have an account?
        <a href="/login" use:link class="inline-link">Log in</a>.
      {:else}
        Free to start.
      {/if}
    </p>
  </div>
</div>

<style>
  .signup-cta {
    position: relative;
    margin-top: var(--margin-top, 4rem);
    width: 100%;
    max-width: var(--max-width, none);
    overflow: hidden;
    border-radius: var(--border-radius, 20px);
  }

  .cta-background {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--color-primary) 8%, transparent) 0%,
      color-mix(in srgb, var(--color-accent) 12%, transparent) 40%,
      transparent 100%
    );
  }

  .cta-content {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: var(--padding, 3rem);
  }

  .signup-cta h2 {
    font-size: var(--h2-font-size, 2rem);
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
    font-family: var(--font-mono);
  }

  .cta-description {
    color: var(--color-muted-foreground);
    font-size: var(--desc-font-size, 1.125rem);
    margin: 0 0 2rem 0;
    line-height: 1.6;
  }

  .cta-button {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    margin-bottom: 1.5rem;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s ease;
  }

  .cta-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 30%, transparent);
  }

  .cta-button:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 40%, transparent);
  }

  .button-prompt,
  .button-text {
    color: var(--color-primary-foreground);
    font-family: var(--font-mono);
    font-weight: 500;
    white-space: nowrap;
  }

  .button-prompt {
    font-size: 14px;
    opacity: 0.8;
  }

  .button-text {
    font-size: 15px;
  }

  .cta-subtext {
    color: var(--color-muted-foreground);
    font-size: var(--subtext-font-size, 0.875rem);
    margin: 0;
  }

  .inline-link {
    color: var(--color-primary);
    text-decoration: none;
  }

  .inline-link:hover {
    text-decoration: underline;
  }

  @media (max-width: 640px) {
    .cta-content {
      padding: var(--mobile-padding, 1.5rem);
    }

    .signup-cta h2 {
      font-size: var(--mobile-h2-font-size, 1.5rem);
    }

    .cta-description {
      font-size: var(--mobile-desc-font-size, 1rem);
    }

    .cta-button {
      width: 100%;
      justify-content: center;
    }
  }

  @media (max-width: 480px) {
    .cta-content {
      padding: var(--compact-padding, 1rem);
    }

    .signup-cta h2 {
      font-size: var(--compact-h2-font-size, 1.25rem);
    }

    .cta-description {
      font-size: var(--compact-desc-font-size, 0.875rem);
    }
  }
</style>
