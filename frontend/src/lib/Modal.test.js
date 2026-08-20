import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { render, screen } from '@testing-library/svelte';
import ModalHarness from './Modal.test.svelte';

const renderModal = (props = {}) =>
  render(ModalHarness, { props: { open: true, onClose: () => {}, ...props } });

describe('Modal accessible name', () => {
  // The dialog has always carried aria-labelledby="modal-title", but Modal
  // rendered no such element -- every caller was expected to supply its own
  // <h2 id="modal-title"> inside the slot, and 10 of the 22 did not. Those
  // dialogs pointed at an id that existed nowhere and so had no accessible
  // name at all, which a screen reader announces as an unlabelled dialog.
  // The `title` prop was declared for this and simply never rendered.

  it('names the dialog from the title prop', () => {
    renderModal({ title: 'Create User' });
    expect(screen.getByRole('dialog', { name: 'Create User' })).toBeInTheDocument();
  });

  it('resolves aria-labelledby to an element that exists', () => {
    const { container } = renderModal({ title: 'Edit Board' });
    const dialog = container.querySelector('[role="dialog"]');
    const target = container.querySelector(`#${dialog.getAttribute('aria-labelledby')}`);
    expect(target).not.toBeNull();
    expect(target.textContent.trim()).toBe('Edit Board');
  });

  it('folds titleBadge into the accessible name', () => {
    // Loose on whitespace: the badge is a nested inline span, and the accname
    // algorithm concatenates inline content without inserting a separator, so
    // the visible space between title and badge is not part of the name.
    renderModal({ title: 'Edit Card', titleBadge: '#42' });
    expect(screen.getByRole('dialog', { name: /^Edit Card\s*#42$/ })).toBeInTheDocument();
  });

  it('renders nothing while closed', () => {
    renderModal({ open: false, title: 'Create User' });
    expect(screen.queryByRole('dialog')).toBeNull();
  });
});

describe('Modal title ownership', () => {
  // Modal owns the heading now. A caller that keeps its own
  // <h2 id="modal-title"> puts a duplicate id in the document and shows the
  // title twice -- both invisible to a unit test that only renders Modal, so
  // assert it against the source of every component instead.
  // vitest runs with the frontend package as its cwd (see vite.config.js).
  const srcDir = join(process.cwd(), 'src');

  const svelteFiles = (dir) =>
    readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) return svelteFiles(full);
      return entry.name.endsWith('.svelte') ? [full] : [];
    });

  it('is the only component that renders id="modal-title"', () => {
    const offenders = svelteFiles(srcDir).filter(
      (file) =>
        !file.endsWith('Modal.svelte') &&
        readFileSync(file, 'utf8').includes('id="modal-title"'),
    );
    expect(offenders).toEqual([]);
  });
});
