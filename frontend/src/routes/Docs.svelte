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
    return markdown.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, href) => {
      if (href.startsWith('http') || href.startsWith('#')) {
        return match;
      }
      if (!href.startsWith('/')) {
        href = '/docs/' + href;
      }
      return `[${text}](${href})`;
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

      setTimeout(() => {
        Prism.highlightAll();
      }, 0);

    } catch (err) {
      error = `Failed to load documentation: ${err.message}`;
      htmlContent = `<h2 class="text-white text-2xl font-semibold mb-4">Documentation Not Found</h2><p class="text-slate-300">The requested documentation section does not exist.</p>`;
    }

    loading = false;
  }

  function handleSectionClick(sectionPath, sectionId) {
    navigate(sectionPath);
  }
</script>

<div class="min-h-screen flex docs-container">
  <!-- Sidebar Navigation -->
  <nav class="w-64 fixed left-0 top-16 h-[calc(100vh-4rem)] border-r overflow-y-auto docs-sidebar">
    <ul class="py-4 px-3 space-y-1">
      {#each docsSections as section}
        <li>
          <a
            href="{section.path}"
            class="block px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 docs-nav-link"
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
  <main class="flex-1 ml-64 p-8 max-w-4xl">
    <!-- Glow effect behind title -->
    <div class="relative mb-8">
      <div class="absolute -inset-4 bg-gradient-to-r from-blue-500/20 via-indigo-500/10 to-purple-500/20 rounded-xl blur-xl opacity-50"></div>
      <div class="relative">
        <h1 class="text-4xl font-bold text-white mb-3">Documentation</h1>
        <p class="text-slate-400 text-lg">Everything you need to build with Kanban CLI</p>
      </div>
    </div>

    {#if loading}
      <div class="flex items-center justify-center min-h-[400px]">
        <div class="text-center">
          <div class="inline-flex items-center justify-center w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-slate-400">Loading documentation...</p>
        </div>
      </div>
    {:else if error}
      <div class="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-400">
        {error}
      </div>
    {:else}
      <!-- Terminal-style command blocks -->
      <div class="markdown-body space-y-6">
        {@html htmlContent}
      </div>
    {/if}
  </main>
</div>

<style>
  .docs-container {
    min-height: 100vh;
    background-color: var(--color-background);
    color: var(--color-foreground);
  }

  .docs-sidebar {
    background-color: var(--color-card);
    border-color: var(--color-border);
  }

  .docs-nav-link {
    color: var(--color-foreground);
  }

  .docs-nav-link:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }

  .docs-nav-link.active {
    border-left-color: var(--color-primary);
    color: var(--color-foreground);
    background-color: rgba(255, 255, 255, 0.05);
  }

  :global(.markdown-body h1) {
    font-size: 1.875rem;
    font-weight: 700;
    color: white;
    margin-bottom: 1.5rem;
    margin-top: 2rem;
  }

  :global(.markdown-body h2) {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin-bottom: 1rem;
    margin-top: 2.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);
  }

  :global(.markdown-body h3) {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin-bottom: 0.75rem;
    margin-top: 2rem;
  }

  :global(.markdown-body h4) {
    font-size: 1.125rem;
    font-weight: 500;
    color: var(--color-foreground);
    margin-bottom: 0.5rem;
    margin-top: 1.5rem;
  }

  :global(.markdown-body p) {
    color: var(--color-muted-foreground);
    line-height: 1.625;
    margin-bottom: 1rem;
  }

  :global(.markdown-body a) {
    color: var(--color-primary);
    transition: color 0.2s;
  }

  :global(.markdown-body a:hover) {
    color: var(--color-accent);
  }

  :global(.markdown-body ul) {
    list-style-type: disc;
    padding-left: 1rem;
    margin-bottom: 1.5rem;
    color: var(--color-muted-foreground);
  }

  :global(.markdown-body ol) {
    list-style-type: decimal;
    padding-left: 1rem;
    margin-bottom: 1.5rem;
    color: var(--color-muted-foreground);
  }

  :global(.markdown-body li) {
    line-height: 1.625;
  }

  :global(.markdown-body strong) {
    color: var(--color-foreground);
    font-weight: 600;
  }

  :global(.markdown-body code) {
    background-color: var(--color-code-bg);
    border: 1px solid var(--color-border);
    border-radius: 0.25rem;
    padding: 0.125rem 0.375rem;
    font-size: 0.875rem;
    font-family: monospace;
    color: #22c55e;
  }

  :global(.markdown-body pre) {
    background-color: var(--color-code-bg);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 1rem;
    font-family: monospace;
    font-size: 0.875rem;
    margin-bottom: 1.5rem;
    overflow-x: auto;
  }

  :global(.markdown-body pre code) {
    background-color: transparent;
    border: none;
    padding: 0;
    color: var(--color-code-fg);
  }

  /* Terminal-style command blocks */
  :global(.markdown-body pre:has(> code.shell)) {
    position: relative;
  }

  :global(.markdown-body code.shell) {
    color: var(--color-success);
  }

  /* Table styling */
  :global(.markdown-body table) {
    width: 100%;
    margin-bottom: 1.5rem;
    border-collapse: collapse;
  }

  :global(.markdown-body thead) {
    border-bottom: 1px solid var(--color-border);
  }

  :global(.markdown-body th) {
    text-align: left;
    font-size: 0.75rem;
    text-transform: uppercase;
    color: var(--color-muted-foreground);
    font-weight: 500;
    padding: 0.75rem 1rem;
  }

  :global(.markdown-body td) {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--color-border);
    color: var(--color-muted-foreground);
  }

  :global(.markdown-body tbody tr:hover) {
    background-color: rgba(255, 255, 255, 0.05);
  }

  /* Blockquotes */
  :global(.markdown-body blockquote) {
    border-left: 4px solid var(--color-primary);
    padding-left: 1rem;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 0 0.5rem 0.5rem 0;
    color: var(--color-muted-foreground);
  }

  /* Horizontal rules */
  :global(.markdown-body hr) {
    border-color: var(--color-border);
    margin-top: 2rem;
    margin-bottom: 2rem;
  }

  /* Inline code in tables */
  :global(.markdown-body td code) {
    font-size: 0.75rem;
  }

  /* Responsive */
  @media (max-width: 768px) {
    nav {
      width: 100%;
      position: relative;
      top: 0;
      height: auto;
      border-right: none;
      border-bottom: 1px solid var(--color-border);
    }

    main {
      margin-left: 0;
      padding: 1.5rem;
    }

    :global(.markdown-body h1) {
      font-size: 1.5rem;
    }

    :global(.markdown-body h2) {
      font-size: 1.25rem;
    }
  }
</style>