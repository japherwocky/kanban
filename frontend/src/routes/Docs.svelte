<script>
  import { onMount } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { marked } from 'marked';
  import Prism from 'prismjs';
  import 'prismjs/themes/prism.css';
  import 'prismjs/components/prism-bash';
  import 'prismjs/components/prism-javascript';

  export let params = { section: 'docs' };

  let markdownContent = '';
  let htmlContent = '';
  let loading = true;
  let error = '';
  let activeSection = params.section || 'docs';

  const docsSections = [
    { id: 'docs', title: 'Documentation', path: '/docs' },
    { id: 'quickstart', title: 'Quick Start', path: '/docs/quickstart' },
    { id: 'reference', title: 'Command Reference', path: '/docs/reference' },
    { id: 'workflows', title: 'Common Workflows', path: '/docs/workflows' }
  ];

  // Configure marked options
  marked.setOptions({
    breaks: true,
    gfm: true
  });

  // Custom renderer to fix markdown links to SPA routes
  const renderer = new marked.Renderer();
  const originalLinkRenderer = renderer.link.bind(renderer);

  renderer.link = function(href, title, text) {
    // Convert markdown file links to SPA route links
    if (href && href.endsWith('.md')) {
      // Remove .md and convert to SPA route
      href = href.replace('.md', '');
      // If it's a relative link (like quickstart.md), prepend /docs/
      if (!href.startsWith('/')) {
        href = '/docs/' + href;
      }
      // Handle anchor links (like quickstart.md#section)
      if (href.includes('#')) {
        const [path, anchor] = href.split('#');
        href = path + '#' + anchor;
      }
    }
    return originalLinkRenderer(href, title, text);
  };

  marked.use({ renderer });

  // Configure highlight function
  marked.setOptions({
    highlight: function(code, lang) {
      if (Prism.languages[lang]) {
        return Prism.highlight(code, Prism.languages[lang], lang);
      }
      return code;
    }
  });

  onMount(async () => {
    await loadDocumentation(activeSection);
  });

  // Watch for section changes
  $: if (params.section !== activeSection) {
    activeSection = params.section || 'docs';
    loadDocumentation(activeSection);
  }

  async function loadDocumentation(section) {
    loading = true;
    error = '';
    
    try {
      const response = await fetch(`/content/${section}.md`);
      
      if (!response.ok) {
        throw new Error(`Documentation not found: ${section}`);
      }
      
      markdownContent = await response.text();
      htmlContent = marked(markdownContent);
      
      // Re-highlight code blocks after content loads
      setTimeout(() => {
        Prism.highlightAll();
      }, 0);
      
    } catch (err) {
      error = `Failed to load documentation: ${err.message}`;
      htmlContent = `<h2>Documentation Not Found</h2><p>The requested documentation section does not exist.</p>`;
    }
    
    loading = false;
  }

  function handleSectionClick(sectionId) {
    activeSection = sectionId;
  }

  function copyCodeBlock(button) {
    const codeBlock = button.parentElement.nextElementSibling.querySelector('code');
    if (codeBlock) {
      navigator.clipboard.writeText(codeBlock.textContent).then(() => {
        button.textContent = '✓ Copied';
        setTimeout(() => {
          button.textContent = '📋 Copy';
        }, 2000);
      });
    }
  }

  function handleLinkClick(event) {
    const link = event.target.closest('a');
    if (!link) return;

    const href = link.getAttribute('href');
    if (!href) return;

    // Only handle docs links (let external links work normally)
    if (href.startsWith('/docs/') || href.startsWith('#')) {
      event.preventDefault();
      navigate(href);
    }
  }
</script>

<style>
  .docs-container {
    display: flex;
    min-height: calc(100vh - 60px);
    background: var(--color-background);
    color: var(--color-foreground);
  }

  .docs-sidebar {
    width: 280px;
    background: var(--color-card);
    border-right: 1px solid var(--color-border);
    padding: 2rem 1rem;
    position: sticky;
    top: 60px;
    height: calc(100vh - 60px);
    overflow-y: auto;
  }

  .docs-nav {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .docs-nav li {
    margin-bottom: 0.5rem;
  }

  .docs-nav a {
    display: block;
    padding: 0.75rem 1rem;
    color: var(--color-foreground);
    text-decoration: none;
    border-radius: 8px;
    transition: all 0.2s ease;
    font-weight: 500;
  }

  .docs-nav a:hover {
    background: var(--color-muted);
    color: var(--color-primary);
  }

  .docs-nav a.active {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
  }

  .docs-main {
    flex: 1;
    padding: 2rem 3rem;
    max-width: 800px;
    overflow-y: auto;
  }

  .docs-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    font-size: 1.125rem;
    color: var(--color-muted-foreground);
  }

  .docs-error {
    background: var(--color-error);
    color: var(--color-error-foreground);
    padding: 1rem;
    border-radius: 8px;
    margin: 2rem 0;
  }

  .markdown-body {
    line-height: 1.6;
  }

  .markdown-body h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 2rem 0 1rem 0;
    color: var(--color-foreground);
  }

  .markdown-body h2 {
    font-size: 2rem;
    font-weight: 600;
    margin: 1.5rem 0 0.75rem 0;
    color: var(--color-foreground);
    border-bottom: 2px solid var(--color-border);
    padding-bottom: 0.5rem;
  }

  .markdown-body h3 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 1.25rem 0 0.5rem 0;
    color: var(--color-foreground);
  }

  .markdown-body h4 {
    font-size: 1.25rem;
    font-weight: 600;
    margin: 1rem 0 0.5rem 0;
    color: var(--color-foreground);
  }

  .markdown-body p {
    margin: 1rem 0;
    color: var(--color-muted-foreground);
  }

  .markdown-body ul, .markdown-body ol {
    margin: 1rem 0;
    padding-left: 2rem;
  }

  .markdown-body li {
    margin: 0.5rem 0;
    color: var(--color-muted-foreground);
  }

  .markdown-body a {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 500;
  }

  .markdown-body a:hover {
    text-decoration: underline;
  }

  .markdown-body blockquote {
    border-left: 4px solid var(--color-primary);
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
    color: var(--color-muted-foreground);
  }

  .markdown-body code {
    background: var(--color-muted);
    color: var(--color-foreground);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
  }

  .markdown-body pre {
    background: var(--color-muted);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    padding: 1rem;
    margin: 1rem 0;
    overflow-x: auto;
    position: relative;
  }

  .markdown-body pre code {
    background: transparent;
    padding: 0;
    border-radius: 0;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  .code-block-wrapper {
    position: relative;
  }

  .copy-button {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    background: var(--color-background);
    border: 1px solid var(--color-border);
    color: var(--color-muted-foreground);
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.75rem;
    transition: all 0.2s ease;
  }

  .copy-button:hover {
    background: var(--color-card);
    color: var(--color-primary);
    border-color: var(--color-primary);
  }

  .markdown-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
  }

  .markdown-body th,
  .markdown-body td {
    border: 1px solid var(--color-border);
    padding: 0.75rem;
    text-align: left;
  }

  .markdown-body th {
    background: var(--color-muted);
    font-weight: 600;
  }

  .markdown-body hr {
    border: none;
    border-top: 2px solid var(--color-border);
    margin: 2rem 0;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .docs-sidebar {
      width: 200px;
    }
    
    .docs-main {
      padding: 1.5rem;
    }
    
    .markdown-body h1 {
      font-size: 2rem;
    }
    
    .markdown-body h2 {
      font-size: 1.5rem;
    }
  }

  @media (max-width: 640px) {
    .docs-container {
      flex-direction: column;
    }
    
    .docs-sidebar {
      width: 100%;
      height: auto;
      position: static;
      border-right: none;
      border-bottom: 1px solid var(--color-border);
    }
    
    .docs-nav {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    
    .docs-nav li {
      margin: 0;
    }
    
    .docs-nav a {
      padding: 0.5rem 1rem;
      font-size: 0.875rem;
    }
  }
</style>

<div class="docs-container">
  <!-- Sidebar Navigation -->
  <nav class="docs-sidebar">
    <ul class="docs-nav">
      {#each docsSections as section}
        <li>
          <a 
            href="{section.path}" 
            class:active={activeSection === section.id}
            on:click|preventDefault={() => handleSectionClick(section.id)}
          >
            {section.title}
          </a>
        </li>
      {/each}
    </ul>
  </nav>

  <!-- Main Content -->
  <main class="docs-main">
    {#if loading}
      <div class="docs-loading">
        <div>Loading documentation...</div>
      </div>
    {:else if error}
      <div class="docs-error">
        {error}
      </div>
    {:else}
      <div class="markdown-body" on:click={handleLinkClick}>
        {@html htmlContent}
      </div>
    {/if}
  </main>
</div>