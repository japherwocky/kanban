<div class="beta-section" style="
  --margin-top: {marginTop};
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
">
  <div class="beta-background"></div>
  <div class="beta-content">
    <h2>Initialize Your Workspace</h2>
    <p class="beta-description">
      We are onboarding high-throughput agent teams.
    </p>

    <form class="email-form" onsubmit={handleSubmit}>
      {#if success}
        <div class="success-message">
          <span class="success-prompt">$</span>
          <span>request received. we'll be in touch.</span>
        </div>
      {:else}
        <div class="input-wrapper">
          <span class="input-prompt">$</span>
          <input
            type="email"
            placeholder="agent@enterprise.io"
            class="email-input"
            bind:value={email}
            disabled={isSending}
          />
          <button type="submit" class="submit-button" class:sending={isSending} disabled={isSending}>
            {#if isSending}
              <span class="button-text">> sending_request...</span>
            {:else}
              <span class="button-text">> request_access</span>
            {/if}
          </button>
        </div>
        {#if error}
          <p class="error-message">{error}</p>
        {/if}
      {/if}
    </form>

    <p class="beta-subtext">
      Limited spots available for Q1 2025.
    </p>
  </div>
</div>

<script>
  import { api } from '$lib/api';

  let {
    marginTop = '4rem',
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

  let email = $state('');
  let isSending = $state(false);
  let success = $state(false);
  let error = $state('');

  async function handleSubmit(event) {
    event.preventDefault();
    if (isSending || success) return;

    isSending = true;
    error = '';

    try {
      await api.beta.signup(email);
      success = true;
    } catch (e) {
      error = e.message || 'Something went wrong. Please try again.';
    } finally {
      isSending = false;
    }
  }
</script>

<style>
  .beta-section {
    position: relative;
    margin-top: var(--margin-top, 4rem);
    width: 100%;
    overflow: hidden;
    border-radius: 20px;
  }

  .beta-background {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--color-primary) 8%, transparent) 0%,
      color-mix(in srgb, var(--color-accent) 12%, transparent) 40%,
      transparent 100%
    );
  }

  .beta-content {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: var(--padding, 3rem);
  }

  .beta-section h2 {
    font-size: var(--h2-font-size, 2rem);
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
    font-family: var(--font-mono);
  }

  .beta-description {
    color: var(--color-muted-foreground);
    font-size: var(--desc-font-size, 1.125rem);
    margin: 0 0 2rem 0;
    line-height: 1.6;
  }

  .email-form {
    margin-bottom: 1.5rem;
  }

  .input-wrapper {
    display: inline-flex;
    align-items: center;
    gap: 0;
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 4px;
    max-width: 500px;
    width: 100%;
    transition: all 0.2s ease;
  }

  .input-wrapper:focus-within {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 10%, transparent);
  }

  .input-prompt {
    padding: 0 12px;
    color: var(--color-success);
    font-family: var(--font-mono);
    font-size: 14px;
  }

  .email-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    padding: 12px 0;
    color: var(--color-foreground);
    font-size: 15px;
    font-family: var(--font-mono);
  }

  .email-input::placeholder {
    color: var(--color-muted-foreground);
  }

  .submit-button {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .submit-button:hover:not(.sending) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px color-mix(in srgb, var(--color-primary) 30%, transparent);
  }

  .submit-button.sending {
    opacity: 0.8;
    cursor: not-allowed;
  }

  .button-text {
    color: var(--color-primary-foreground);
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
  }

  .beta-subtext {
    color: var(--color-muted-foreground);
    font-size: var(--subtext-font-size, 0.875rem);
    margin: 0;
    font-style: italic;
  }

  .success-message {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: color-mix(in srgb, var(--color-success) 10%, transparent);
    border: 1px solid color-mix(in srgb, var(--color-success) 30%, transparent);
    border-radius: 12px;
    color: var(--color-success);
    font-family: var(--font-mono);
    font-size: 14px;
  }

  .success-prompt {
    color: var(--color-success);
  }

  .error-message {
    color: var(--color-error);
    font-size: 0.875rem;
    margin-top: 0.75rem;
    text-align: center;
  }

  @media (max-width: 640px) {
    .beta-content {
      padding: var(--mobile-padding, 1.5rem);
    }

    .beta-section h2 {
      font-size: var(--mobile-h2-font-size, 1.5rem);
    }

    .beta-description {
      font-size: var(--mobile-desc-font-size, 1rem);
    }

    .input-wrapper {
      flex-direction: column;
      gap: 8px;
      padding: 16px;
    }

    .input-prompt {
      align-self: flex-start;
      padding: 0;
    }

    .email-input {
      width: 100%;
      padding: 8px 0;
    }

    .submit-button {
      width: 100%;
    }

    .success-message {
      flex-direction: column;
      gap: 4px;
      text-align: center;
    }

    .success-prompt {
      align-self: flex-start;
    }
  }

  @media (max-width: 480px) {
    .beta-content {
      padding: var(--compact-padding, 1rem);
    }

    .beta-section h2 {
      font-size: var(--compact-h2-font-size, 1.25rem);
    }

    .beta-description {
      font-size: var(--compact-desc-font-size, 0.875rem);
    }
  }
</style>
