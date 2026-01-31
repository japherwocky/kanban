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
    { id: 'workflows', title: 'Common Workflows', path: '/docs/workflows' },
    { id: 'commands', title: 'All Commands', path: '/docs/commands' }
  ];

  // Configure marked options
  marked.setOptions({
    breaks: true,
    gfm: true,
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

  function convertMarkdownLinks(markdown) {
    // Convert relative .md links to /docs/ routes
    // [text](quickstart.md) → [text](/docs/quickstart)
    // [text](reference.md#section) → [text](/docs/reference#section)
    return markdown.replace(/\[([^\]]+)\]\(([^)]+?\.md[^)]*)\)/g, (match, text, href) => {
      let newHref = href.replace('.md', '');
      if (!newHref.startsWith('/')) {
        newHref = '/docs/' + newHref;
      }
      return `[${text}](${newHref})`;
    });
  }

  async function loadDocumentation(section) {
    loading = true;
    error = '';
    
    try {
      const response = await fetch(`/docs/${section}.md`);

      if (!response.ok) {
        throw new Error(`Documentation not found: ${section}`);
      }

      let rawMarkdown = await response.text();
      markdownContent = convertMarkdownLinks(rawMarkdown);
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

  function handleSectionClick(sectionPath, sectionId) {
    console.log('Navigating to:', sectionPath, 'from section:', sectionId);
    // Navigate to the new URL
    navigate(sectionPath);
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

  /* Responsive */
  @media (max-width: 768px) {
    .docs-sidebar {
      width: 200px;
    }
    
    .docs-main {
      padding: 1.5rem;
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
            on:click={() => handleSectionClick(section.path, section.id)}
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
      <div class="markdown-body">
        {@html htmlContent}
      </div>
    {/if}
  </main>
</div>