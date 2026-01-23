<div class="beta-section" style="
  --margin-top: {marginTop};
  --max-width: {maxWidth};
  --border-radius: {borderRadius};
  --padding: {padding};
  --h2-font-size: {h2FontSize};
  --desc-font-size: {descFontSize};
  --email-padding: {emailPadding};
  --email-border-radius: {emailBorderRadius};
  --email-font-weight: {emailFontWeight};
  --email-font-size: {emailFontSize};
  --subtext-font-size: {subtextFontSize};
  --mobile-padding: {mobilePadding};
  --mobile-h2-font-size: {mobileH2FontSize};
  --mobile-desc-font-size: {mobileDescFontSize};
  --compact-padding: {compactPadding};
  --compact-h2-font-size: {compactH2FontSize};
  --compact-desc-font-size: {compactDescFontSize};
  --compact-email-padding: {compactEmailPadding};
  --compact-email-font-size: {compactEmailFontSize};
">
  <h2>Closed Beta</h2>
  <p class="beta-description">
    We're currently in closed beta. If you'd like early access or want to integrate agents into your workflow,
    reach out and let us know your use case.
  </p>
  <a href="mailto:pkanban@pearachute.com" class="beta-email">
    pkanban@pearachute.com
  </a>
  <p class="beta-subtext">
    We're actively seeking feedback from teams building AI workflows.
  </p>
</div>

<script>
  export let marginTop = '4rem';
  export let maxWidth = '600px';
  export let borderRadius = '16px';
  export let padding = '2.5rem';
  export let h2FontSize = '2rem';
  export let descFontSize = '1.125rem';
  export let emailPadding = '0.875rem 2rem';
  export let emailBorderRadius = '12px';
  export let emailFontWeight = '600';
  export let emailFontSize = '1rem';
  export let subtextFontSize = '0.875rem';
  export let mobilePadding = '1.5rem';
  export let mobileH2FontSize = '1.5rem';
  export let mobileDescFontSize = '1rem';
  export let compactPadding = '1rem';
  export let compactH2FontSize = '1.25rem';
  export let compactDescFontSize = '0.875rem';
  export let compactEmailPadding = '0.625rem 1.25rem';
  export let compactEmailFontSize = '0.875rem';
</script>

<style>
  .beta-section {
    margin-top: var(--margin-top, 4rem);
    max-width: var(--max-width, 600px);
    width: 100%;
    text-align: center;
    background: linear-gradient(135deg, var(--color-card) 0%, rgba(var(--color-primary-rgb), 0.05) 100%);
    border: 2px solid var(--color-primary);
    border-radius: var(--border-radius, 16px);
    padding: var(--padding, 2.5rem);
  }

  .beta-section h2 {
    font-size: var(--h2-font-size, 2rem);
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0 0 1rem 0;
  }

  .beta-description {
    color: var(--color-muted-foreground);
    font-size: var(--desc-font-size, 1.125rem);
    margin: 0 0 1.5rem 0;
    line-height: 1.6;
  }

  .beta-email {
    display: inline-block;
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    padding: var(--email-padding, 0.875rem 2rem);
    border-radius: var(--email-border-radius, 12px);
    text-decoration: none;
    font-weight: var(--email-font-weight, 600);
    font-size: var(--email-font-size, 1rem);
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .beta-email:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }

  .beta-subtext {
    margin-top: 1.5rem;
    color: var(--color-muted-foreground);
    font-size: var(--subtext-font-size, 0.875rem);
    font-style: italic;
  }

  @media (max-width: 640px) {
    .beta-section {
      padding: var(--mobile-padding, 1.5rem);
    }

    .beta-section h2 {
      font-size: var(--mobile-h2-font-size, 1.5rem);
    }

    .beta-description {
      font-size: var(--mobile-desc-font-size, 1rem);
    }
  }

  @media (max-width: 480px) {
    .beta-section {
      padding: var(--compact-padding, 1rem);
    }

    .beta-section h2 {
      font-size: var(--compact-h2-font-size, 1.25rem);
    }

    .beta-description {
      font-size: var(--compact-desc-font-size, 0.875rem);
    }

    .beta-email {
      padding: var(--compact-email-padding, 0.625rem 1.25rem);
      font-size: var(--compact-email-font-size, 0.875rem);
    }
  }
</style>