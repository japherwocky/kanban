import { writable } from 'svelte/store';

const THEME_STORAGE_KEY = 'kanban-theme';

const getInitialTheme = () => {
  if (typeof window === 'undefined') return 'system';
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored && ['light', 'dark', 'system'].includes(stored)) {
    return stored;
  }
  return 'system';
};

const getSystemTheme = () => {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const applyTheme = (theme) => {
  if (typeof document === 'undefined') return;
  
  const resolvedTheme = theme === 'system' ? getSystemTheme() : theme;
  document.documentElement.classList.toggle('dark', resolvedTheme === 'dark');
};

const createThemeStore = () => {
  const { subscribe, set, update } = writable(getInitialTheme());

  return {
    subscribe,
    setTheme: (theme) => {
      if (!['light', 'dark', 'system'].includes(theme)) return;
      set(theme);
      localStorage.setItem(THEME_STORAGE_KEY, theme);
      applyTheme(theme);
    },
    cycleTheme: () => {
      update(current => {
        const next = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
        localStorage.setItem(THEME_STORAGE_KEY, next);
        applyTheme(next);
        return next;
      });
    },
    init: () => {
      const theme = getInitialTheme();
      set(theme);
      applyTheme(theme);

      if (typeof window !== 'undefined') {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
          const current = localStorage.getItem(THEME_STORAGE_KEY);
          if (current === 'system') {
            applyTheme('system');
          }
        });
      }
    }
  };
};

export const theme = createThemeStore();

export const getThemeLabel = (theme) => {
  switch (theme) {
    case 'light': return 'Light';
    case 'dark': return 'Dark';
    case 'system': return 'System';
    default: return 'System';
  }
};
