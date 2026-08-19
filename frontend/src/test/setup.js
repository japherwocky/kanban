import '@testing-library/jest-dom/vitest';
import { beforeEach } from 'vitest';

// jsdom under this vitest/node combination hands back a bare object for
// window.localStorage -- getItem/setItem/clear are all missing, so anything
// touching storage throws "not a function" rather than failing on its own
// merits. The app reads storage in several places (the auth token in api.js,
// the theme in theme.js), so install a real Storage-shaped implementation and
// reset it between tests instead of depending on the environment.
function createStorage() {
  let data = Object.create(null);
  return {
    get length() { return Object.keys(data).length; },
    key: (i) => Object.keys(data)[i] ?? null,
    getItem: (k) => (k in data ? data[k] : null),
    setItem: (k, v) => { data[String(k)] = String(v); },
    removeItem: (k) => { delete data[k]; },
    clear: () => { data = Object.create(null); },
  };
}

function installStorage(name) {
  const store = createStorage();
  Object.defineProperty(window, name, {
    value: store, writable: true, configurable: true,
  });
  Object.defineProperty(globalThis, name, {
    value: store, writable: true, configurable: true,
  });
}

installStorage('localStorage');
installStorage('sessionStorage');

// jsdom does not implement matchMedia at all, and theme.js calls it on init to
// watch for OS colour-scheme changes. Report "not dark" so the light/dark
// decision under test comes from stored preference rather than from the host.
if (typeof window.matchMedia !== 'function') {
  window.matchMedia = (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => false,
  });
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});
