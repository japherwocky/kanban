<script>
  // Modal takes its body as a `children` snippet, which cannot be passed
  // through @testing-library's plain props object -- this harness supplies one.
  import Modal from './Modal.svelte';

  let { open, onClose, title = undefined, titleBadge = undefined, wide = false } = $props();
</script>

<Modal {open} {onClose} {title} {titleBadge} {wide}>
  {#snippet children()}
    <form><button type="submit">Save</button></form>
  {/snippet}
</Modal>
