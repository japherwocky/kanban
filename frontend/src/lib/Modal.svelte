<script>
  import { onMount, onDestroy } from 'svelte';

  let { open = false, onClose, title = 'Dialog', children } = $props();

  let modalRef = $state();
  let previousActiveElement = null;

  // Handle keyboard navigation
  function handleKeydown(e) {
    if (!open) return;

    // ESC to close
    if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
      return;
    }

    // Tab trapping - keep focus within modal
    if (e.key === 'Tab') {
      const focusableElements = modalRef.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement.focus();
        }
      }
    }
  }

  // Handle backdrop click
  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
      onClose();
    }
  }

  // Focus management
  $effect(() => {
    if (open) {
      // Save previous focused element
      previousActiveElement = document.activeElement;

      // Focus first focusable element in modal
      setTimeout(() => {
        const focusableElements = modalRef?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements && focusableElements.length > 0) {
          focusableElements[0].focus();
        }
      }, 0);

      // Add keyboard event listener
      document.addEventListener('keydown', handleKeydown);

      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Restore focus to previous element
      if (previousActiveElement) {
        setTimeout(() => previousActiveElement.focus(), 0);
      }

      // Remove keyboard event listener
      document.removeEventListener('keydown', handleKeydown);

      // Restore body scroll
      document.body.style.overflow = '';
    }

    return () => {
      document.removeEventListener('keydown', handleKeydown);
      document.body.style.overflow = '';
    };
  });
</script>

{#if open}
  <div
    class="modal-overlay"
    role="presentation"
    onclick={handleBackdropClick}
  >
    <div
      class="modal"
      bind:this={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {@render children()}
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    z-index: 50;
  }

  .modal {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.5rem;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }

  :global(.modal form) {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
</style>
