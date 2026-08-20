import svelte from 'eslint-plugin-svelte';
import svelteParser from 'svelte-eslint-parser';

// Advisory only. The CI step that runs this cannot fail the workflow -- the
// point is visibility, not enforcement. Severities are 'warn' to match, so
// `npm run lint` exits 0 locally too and never blocks a commit.
//
// Worth knowing what this bought us: run against BoardView.svelte as it stood
// before PR #40 and a single default rule reports both of the defects that
// took a browser session to find --
//
//   'onMount' is defined but never used   (dead import)
//   'dndzone' is defined but never used   (drag-and-drop never worked)
//
// The second is the interesting one. `dndzone={{...}}` uses the name as an
// attribute, not as a variable, so the import really is unread -- svelte-dnd-
// action is an action and only runs as `use:dndzone={...}`. A text search
// cannot see that; the AST can.

export default [
  {
    ignores: ['dist/**', 'node_modules/**', '../backend/static/**'],
  },

  ...svelte.configs['flat/recommended'],

  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
    },
  },

  {
    files: ['**/*.svelte'],
    languageOptions: {
      parser: svelteParser,
      ecmaVersion: 2024,
      sourceType: 'module',
    },
  },

  {
    files: ['**/*.svelte', '**/*.js'],
    rules: {
      // Everything recommended already flags, downgraded to advisory.
      'no-unused-vars': 'warn',
      'svelte/require-each-key': 'warn',
      'svelte/no-at-html-tags': 'warn',
      'svelte/no-useless-mustaches': 'warn',
      'svelte/prefer-writable-derived': 'warn',

      // Off: pure style, and it was 22 of 60 findings on adoption -- all of
      // them the explicit `{#snippet children()}` inside <Modal>, which Svelte
      // 5 makes implicit. Redundant, never wrong, and loud enough to bury the
      // rules above. Turn it back on if the Modal call sites are ever tidied.
      'svelte/no-useless-children-snippet': 'off',
    },
  },

  {
    // Tests run in node/jsdom and legitimately define things the app does not.
    files: ['**/*.test.js', 'src/test/**'],
    rules: {
      'no-unused-vars': 'off',
    },
  },
];
