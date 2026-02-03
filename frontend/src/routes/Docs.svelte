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

<div class="min-h-screen bg-[#050505] flex">
  <!-- Sidebar Navigation -->
  <nav class="w-64 fixed left-0 top-16 h-[calc(100vh-4rem)] border-r border-white/10 bg-[#050505] overflow-y-auto">
    <ul class="py-4 px-3 space-y-1">
      {#each docsSections as section}
        <li>
          <a
            href="{section.path}"
            class="block px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200
                   {activeSection === section.id
                     ? 'border-l-2 border-blue-500 text-white bg-white/5'
                     : 'text-slate-300 hover:bg-white/5 hover:text-white'}"
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
  :global(.markdown-body h1) {
    @apply text-3xl font-bold text-white mb-6 mt-8;
  }

  :global(.markdown-body h2) {
    @apply text-2xl font-semibold text-white mb-4 mt-10 pb-2 border-b border-white/10;
  }

  :global(.markdown-body h3) {
    @apply text-xl font-semibold text-white mb-3 mt-8;
  }

  :global(.markdown-body h4) {
    @apply text-lg font-medium text-white mb-2 mt-6;
  }

  :global(.markdown-body p) {
    @apply text-slate-300 leading-relaxed mb-4;
  }

  :global(.markdown-body a) {
    @apply text-blue-500 hover:text-blue-400 transition-colors duration-200;
  }

  :global(.markdown-body ul) {
    @apply list-disc list-inside space-y-2 mb-6 text-slate-300;
  }

  :global(.markdown-body ol) {
    @apply list-decimal list-inside space-y-2 mb-6 text-slate-300;
  }

  :global(.markdown-body li) {
    @apply leading-relaxed;
  }

  :global(.markdown-body strong) {
    @apply text-white font-semibold;
  }

  :global(.markdown-body code) {
    @apply bg-[#0F1117] border border-white/10 rounded px-1.5 py-0.5 text-sm font-mono text-pink-400;
  }

  :global(.markdown-body pre) {
    @apply bg-[#0F1117] border border-white/10 rounded-lg p-4 font-mono text-sm mb-6 overflow-x-auto;
  }

  :global(.markdown-body pre code) {
    @apply bg-transparent border-none p-0 text-slate-300;
  }

  /* Terminal-style command blocks */
  :global(.markdown-body pre:has(> code.shell)) {
    @apply relative;
  }

  :global(.markdown-body code.shell) {
    @apply text-emerald-500;
  }

  /* Table styling */
  :global(.markdown-body table) {
    @apply w-full mb-6 border-collapse;
  }

  :global(.markdown-body thead) {
    @apply border-b border-white/10;
  }

  :global(.markdown-body th) {
    @apply text-left text-xs uppercase text-gray-500 font-medium py-3 px-4;
  }

  :global(.markdown-body td) {
    @apply py-3 px-4 border-b border-white/10 text-slate-300;
  }

  :global(.markdown-body tbody tr:hover) {
    @apply bg-white/5;
  }

  /* Blockquotes */
  :global(.markdown-body blockquote) {
    @apply border-l-4 border-blue-500 pl-4 py-2 my-6 bg-white/5 rounded-r-lg text-slate-300;
  }

  /* Horizontal rules */
  :global(.markdown-body hr) {
    @apply border-white/10 my-8;
  }

  /* Inline code in tables */
  :global(.markdown-body td code) {
    @apply text-xs;
  }

  /* Responsive */
  @media (max-width: 768px) {
    nav {
      width: 100%;
      position: relative;
      top: 0;
      height: auto;
      border-right: none;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    main {
      margin-left: 0;
      padding: 1.5rem;
    }

    :global(.markdown-body h1) {
      @apply text-2xl;
    }

    :global(.markdown-body h2) {
      @apply text-xl;
    }
  }
</style>