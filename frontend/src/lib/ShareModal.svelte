<script>
   import Modal from './Modal.svelte';

   let { open, onClose, board, availableTeams, onShare } = $props();
   let selectedTeamId = $state(board?.shared_team_id || null);
   let isPublicToOrg = $state(board?.is_public_to_org || false);
   let loading = $state(false);

   async function handleShare() {
     loading = true;
     try {
       // If public to org, don't send team_id
       // Otherwise, send the selected team_id (or null to unshare)
       await onShare(isPublicToOrg ? null : selectedTeamId, isPublicToOrg);
       onClose();
     } catch (e) {
       alert('Failed to share board: ' + e.message);
     } finally {
       loading = false;
     }
   }

   // When public is checked, clear team selection
   $effect(() => {
     if (isPublicToOrg) {
       selectedTeamId = null;
     }
   });
 </script>

 {#if open}
   <Modal open={open} onClose={onClose} title="Share Board">
     {#snippet children()}
       <h2 id="modal-title">Share Board: {board?.name}</h2>

       <div class="share-content">
         <div class="share-option">
           <label class="checkbox-label">
             <input
               type="checkbox"
               bind:checked={isPublicToOrg}
               id="public-checkbox"
             />
             <span>Public to organization</span>
           </label>
           <p class="share-help">When public, all organization members can view and edit this board.</p>
         </div>

         {#if !isPublicToOrg}
           <label class="share-label">Share with team:</label>
           <select
             class="team-select"
             bind:value={selectedTeamId}
             disabled={isPublicToOrg}
           >
             <option value={null}>Not shared</option>
             {#each availableTeams as team}
               <option value={team.id}>{team.name} ({team.organization})</option>
             {/each}
           </select>
         {/if}

         <div class="share-info">
           {#if isPublicToOrg && !board?.is_public_to_org}
             <p class="info">ℹ️ This will make the board accessible to all organization members.</p>
           {:else if !isPublicToOrg && board?.shared_team_id && !selectedTeamId}
             <p class="warning">⚠️ This will unshare the board from its current team.</p>
           {:else if !isPublicToOrg && selectedTeamId && selectedTeamId !== board?.shared_team_id}
             <p class="info">ℹ️ This will share the board with the selected team. All team members will be able to view and edit.</p>
           {:else if !isPublicToOrg && !board?.shared_team_id && !selectedTeamId}
             <p class="info">ℹ️ Sharing a board allows all team members to view and edit it.</p>
           {:else}
             <p class="info">ℹ️ This board is currently {board?.is_public_to_org ? 'public to the organization' : 'shared with ' + availableTeams.find(t => t.id === board.shared_team_id)?.name + '.'}</p>
           {/if}
         </div>
       </div>

       <div class="modal-actions">
         <button type="button" class="cancel-btn" onclick={onClose}>Cancel</button>
         <button type="button" class="create-btn" onclick={handleShare} disabled={loading}>
           {loading ? 'Saving...' : 'Save'}
         </button>
       </div>
     {/snippet}
   </Modal>
 {/if}

<style>
   #modal-title {
     margin: 0 0 1.25rem 0;
     font-size: 1.25rem;
     font-weight: 600;
     color: var(--color-foreground);
   }

   .share-content {
     display: flex;
     flex-direction: column;
     gap: 1.25rem;
   }

   .share-option {
     display: flex;
     flex-direction: column;
     gap: 0.5rem;
     padding: 1rem;
     border-radius: 8px;
     background: var(--color-muted);
   }

   .checkbox-label {
     display: flex;
     align-items: center;
     gap: 0.75rem;
     font-size: 1rem;
     font-weight: 500;
     color: var(--color-foreground);
     cursor: pointer;
   }

   .checkbox-label input[type="checkbox"] {
     width: 1.25rem;
     height: 1.25rem;
     cursor: pointer;
   }

   .share-help {
     font-size: 0.875rem;
     color: var(--color-muted-foreground);
     margin: 0;
   }

   .share-label {
     font-size: 0.875rem;
     font-weight: 500;
     color: var(--color-foreground);
   }

   .team-select {
     padding: 0.75rem 1rem;
     font-size: 1rem;
     border-radius: 8px;
     border: 1px solid var(--color-border);
     background: var(--color-card);
     color: var(--color-foreground);
     width: 100%;
   }

   .team-select:focus {
     outline: none;
    border-color: var(--color-primary);
     box-shadow: 0 0 0 3px var(--color-primary);
   }

   .team-select:disabled {
    opacity: 0.5;
    cursor: not-allowed;
   }

   .share-info p {
     font-size: 0.875rem;
     margin: 0;
     padding: 0.75rem;
     border-radius: 6px;
   }

   .share-info .warning {
     background: var(--color-destructive, #fef2f2);
     color: var(--color-destructive, #991b1b);
     border:1px solid var(--color-destructive, #fecaca);
   }

   .share-info .info {
     background: var(--color-muted);
     color: var(--color-foreground);
   }

   .modal-actions {
     display: flex;
     justify-content: flex-end;
     gap: 0.75rem;
     margin-top: 1rem;
   }

   .cancel-btn {
     background: transparent;
     color: var(--color-foreground);
     border:1px solid var(--color-border);
   }

   .cancel-btn:hover {
     background: var(--color-muted);
   }

   .create-btn {
     background: var(--color-primary);
     color: var(--color-primary-foreground);
     border: none;
   }

   .create-btn:hover {
     opacity: 0.9;
   }

   .create-btn:disabled {
     opacity: 0.5;
     cursor: not-allowed;
   }
 </style>
