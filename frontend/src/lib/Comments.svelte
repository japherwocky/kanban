<script>
  import { api } from './api.js';

  let { card, onCommentsUpdate } = $props();

  let comments = $state(card?.comments || []);
  let newComment = $state('');
  let loading = $state(false);
  let editingCommentId = $state(null);
  let editContent = $state('');

  // Get current user's id from token
  let currentUserId = $state(null);
  try {
    const token = localStorage.getItem('token');
    if (token) {
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      currentUserId = tokenData.sub;
    }
  } catch (e) {
    console.error('Failed to decode token:', e);
  }

  // Update comments when card prop changes
  $effect(() => {
    if (card?.comments) {
      comments = [...card.comments];
    }
  });

  function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    
    return date.toLocaleDateString();
  }

  async function createComment() {
    if (!newComment.trim()) return;
    
    loading = true;
    try {
      const comment = await api.comments.create(card.id, newComment.trim());
      comments = [...comments, comment];
      newComment = '';
      
      // Notify parent component of the update
      if (onCommentsUpdate) {
        onCommentsUpdate(card.id, [...comments]);
      }
    } catch (e) {
      alert('Failed to create comment: ' + e.message);
    } finally {
      loading = false;
    }
  }

  async function deleteComment(commentId) {
    if (!confirm('Delete this comment?')) return;
    
    try {
      await api.comments.delete(commentId);
      comments = comments.filter(c => c.id !== commentId);
      
      // Notify parent component of the update
      if (onCommentsUpdate) {
        onCommentsUpdate(card.id, [...comments]);
      }
    } catch (e) {
      alert('Failed to delete comment: ' + e.message);
    }
  }

  function startEdit(comment) {
    editingCommentId = comment.id;
    editContent = comment.content;
  }

  function cancelEdit() {
    editingCommentId = null;
    editContent = '';
  }

  async function saveEdit(commentId) {
    if (!editContent.trim()) return;
    
    try {
      const updatedComment = await api.comments.update(commentId, editContent.trim());
      comments = comments.map(c => c.id === commentId ? updatedComment : c);
      editingCommentId = null;
      editContent = '';
      
      // Notify parent component of the update
      if (onCommentsUpdate) {
        onCommentsUpdate(card.id, [...comments]);
      }
    } catch (e) {
      alert('Failed to update comment: ' + e.message);
    }
  }

  function handleKeydown(event, action, ...args) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      action(...args);
    }
  }
</script>

<div class="comments-section">
  <h4 class="comments-title">Comments ({comments.length})</h4>
  
  <!-- Comments list -->
  <div class="comments-list">
    {#each comments as comment (comment.id)}
      <div class="comment">
        <div class="comment-header">
          <span class="comment-author">{comment.username}</span>
          <span class="comment-time">{formatRelativeTime(comment.created_at)}</span>
          {#if comment.user_id === currentUserId}
            <div class="comment-actions">
              <button 
                class="comment-action-btn" 
                onclick={() => startEdit(comment)}
                title="Edit comment"
              >
                ✏️
              </button>
              <button 
                class="comment-action-btn delete" 
                onclick={() => deleteComment(comment.id)}
                title="Delete comment"
              >
                🗑️
              </button>
            </div>
          {/if}
        </div>
        
        <div class="comment-content">
          {#if editingCommentId === comment.id}
            <div class="edit-form">
              <textarea 
                bind:value={editContent}
                class="edit-textarea"
                placeholder="Edit your comment..."
                onkeydown={(e) => handleKeydown(e, saveEdit, comment.id)}
              ></textarea>
              <div class="edit-actions">
                <button 
                  class="btn btn-sm btn-primary" 
                  onclick={() => saveEdit(comment.id)}
                  disabled={!editContent.trim()}
                >
                  Save
                </button>
                <button 
                  class="btn btn-sm btn-secondary" 
                  onclick={cancelEdit}
                >
                  Cancel
                </button>
              </div>
            </div>
          {:else}
            <p class="comment-text">{comment.content}</p>
            {#if comment.updated_at && comment.updated_at !== comment.created_at}
              <span class="comment-edited">(edited)</span>
            {/if}
          {/if}
        </div>
      </div>
    {/each}
    
    {#if comments.length === 0}
      <p class="no-comments">No comments yet. Be the first to comment!</p>
    {/if}
  </div>
  
  <!-- New comment form -->
  <div class="new-comment-form">
    <textarea 
      bind:value={newComment}
      class="new-comment-input"
      placeholder="Add a comment..."
      disabled={loading}
      onkeydown={(e) => handleKeydown(e, createComment)}
    ></textarea>
    <button 
      class="btn btn-primary" 
      onclick={createComment}
      disabled={loading || !newComment.trim()}
    >
      {loading ? 'Adding...' : 'Add Comment'}
    </button>
  </div>
</div>

<style>
  .comments-section {
    margin-top: 1rem;
    border-top: 1px solid var(--border-color, #e0e0e0);
    padding-top: 1rem;
  }

  .comments-title {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color, #333);
  }

  .comments-list {
    max-height: 300px;
    overflow-y: auto;
    margin-bottom: 1rem;
  }

  .comment {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: var(--comment-bg, #f8f9fa);
    border-radius: 8px;
    border: 1px solid var(--border-color, #e0e0e0);
  }

  .comment-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .comment-author {
    font-weight: 600;
    color: var(--primary-color, #007bff);
  }

  .comment-time {
    font-size: 0.875rem;
    color: var(--text-muted, #6c757d);
  }

  .comment-actions {
    margin-left: auto;
    display: flex;
    gap: 0.25rem;
  }

  .comment-action-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    font-size: 0.875rem;
    opacity: 0.7;
    transition: opacity 0.2s;
  }

  .comment-action-btn:hover {
    opacity: 1;
    background: var(--hover-bg, rgba(0, 0, 0, 0.1));
  }

  .comment-action-btn.delete:hover {
    background: var(--danger-bg, rgba(220, 53, 69, 0.1));
  }

  .comment-content {
    margin: 0;
  }

  .comment-text {
    margin: 0;
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  .comment-edited {
    font-size: 0.75rem;
    color: var(--text-muted, #6c757d);
    font-style: italic;
  }

  .edit-form {
    margin: 0;
  }

  .edit-textarea {
    width: 100%;
    min-height: 60px;
    padding: 0.5rem;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 4px;
    font-family: inherit;
    font-size: 0.875rem;
    resize: vertical;
    margin-bottom: 0.5rem;
  }

  .edit-actions {
    display: flex;
    gap: 0.5rem;
  }

  .no-comments {
    text-align: center;
    color: var(--text-muted, #6c757d);
    font-style: italic;
    margin: 2rem 0;
  }

  .new-comment-form {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .new-comment-input {
    width: 100%;
    min-height: 80px;
    padding: 0.75rem;
    border: 1px solid var(--border-color, #e0e0e0);
    border-radius: 8px;
    font-family: inherit;
    font-size: 0.875rem;
    resize: vertical;
    transition: border-color 0.2s;
  }

  .new-comment-input:focus {
    outline: none;
    border-color: var(--primary-color, #007bff);
    box-shadow: 0 0 0 2px var(--primary-color-alpha, rgba(0, 123, 255, 0.25));
  }

  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    align-self: flex-start;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-primary {
    background: var(--primary-color, #007bff);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--primary-color-dark, #0056b3);
  }

  .btn-secondary {
    background: var(--secondary-color, #6c757d);
    color: white;
  }

  .btn-secondary:hover:not(:disabled) {
    background: var(--secondary-color-dark, #545b62);
  }

  .btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }

  /* Dark theme support */
  @media (prefers-color-scheme: dark) {
    .comments-section {
      border-top-color: #444;
    }

    .comments-title {
      color: #e0e0e0;
    }

    .comment {
      background: #2a2a2a;
      border-color: #444;
    }

    .comment-author {
      color: #4dabf7;
    }

    .comment-time, .comment-edited, .no-comments {
      color: #adb5bd;
    }

    .comment-text {
      color: #e0e0e0;
    }

    .edit-textarea, .new-comment-input {
      background: #1a1a1a;
      border-color: #444;
      color: #e0e0e0;
    }

    .edit-textarea:focus, .new-comment-input:focus {
      border-color: #4dabf7;
      box-shadow: 0 0 0 2px rgba(77, 171, 247, 0.25);
    }

    .comment-action-btn:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    .comment-action-btn.delete:hover {
      background: rgba(220, 53, 69, 0.2);
    }
  }
</style>
