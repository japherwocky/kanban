<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import Modal from '../lib/Modal.svelte';

  let teams = $state([]);
  let teamsLoading = $state(false);
  let organizations = $state([]);
  let showCreateTeamModal = $state(false);
  let showEditTeamModal = $state(false);
  let showMembersModal = $state(false);
  let selectedTeam = $state(null);
  let newTeamName = $state('');
  let newTeamOrgId = $state('');
  let editTeamName = $state('');
  let editTeamOrgId = $state('');
  let teamMembers = $state([]);
  let availableMembers = $state([]);
  let addMemberUsername = $state('');

  onMount(async () => {
    await Promise.all([loadTeams(), loadOrganizations()]);
  });

  async function loadTeams() {
    teamsLoading = true;
    try {
      teams = await api.admin.teams.list();
    } catch (e) {
      console.error('Failed to load teams:', e);
      alert('Failed to load teams: ' + e.message);
    } finally {
      teamsLoading = false;
    }
  }

  async function loadOrganizations() {
    try {
      organizations = await api.admin.organizations.list();
    } catch (e) {
      console.error('Failed to load organizations:', e);
    }
  }

  function getOrgNameById(orgId) {
    const org = organizations.find(o => o.id === orgId);
    return org?.name || 'Unknown';
  }

  async function createTeam() {
    if (!newTeamName.trim() || !newTeamOrgId) return;

    try {
      await api.admin.teams.create({
        name: newTeamName.trim(),
        organization_id: parseInt(newTeamOrgId),
      });
      newTeamName = '';
      newTeamOrgId = '';
      showCreateTeamModal = false;
      await loadTeams();
    } catch (e) {
      alert('Failed to create team: ' + e.message);
    }
  }

  function openEditTeam(team) {
    selectedTeam = team;
    editTeamName = team.name;
    editTeamOrgId = team.organization_id.toString();
    showEditTeamModal = true;
  }

  async function updateTeam() {
    if (!selectedTeam) return;

    try {
      await api.admin.teams.update(selectedTeam.id, {
        name: editTeamName.trim(),
        organization_id: parseInt(editTeamOrgId),
      });
      showEditTeamModal = false;
      selectedTeam = null;
      await loadTeams();
    } catch (e) {
      alert('Failed to update team: ' + e.message);
    }
  }

  async function deleteTeam(teamId) {
    if (!confirm('Are you sure you want to delete this team? This will remove team members and unshare any boards. This action cannot be undone.')) return;

    try {
      await api.admin.teams.delete(teamId);
      teams = teams.filter(t => t.id !== teamId);
    } catch (e) {
      alert('Failed to delete team: ' + e.message);
    }
  }

  async function openMembersModal(team) {
    selectedTeam = team;
    await Promise.all([loadTeamMembers(team.id), loadAvailableMembers(team.id)]);
    showMembersModal = true;
  }

  async function loadTeamMembers(teamId) {
    try {
      teamMembers = await api.admin.teams.members.list(teamId);
    } catch (e) {
      console.error('Failed to load team members:', e);
      alert('Failed to load team members: ' + e.message);
    }
  }

  async function loadAvailableMembers(teamId) {
    try {
      availableMembers = await api.admin.teams.members.available(teamId);
    } catch (e) {
      console.error('Failed to load available members:', e);
    }
  }

  async function addMember() {
    if (!addMemberUsername.trim()) return;

    try {
      await api.admin.teams.members.add(selectedTeam.id, addMemberUsername.trim());
      addMemberUsername = '';
      await Promise.all([loadTeamMembers(selectedTeam.id), loadAvailableMembers(selectedTeam.id)]);
    } catch (e) {
      alert('Failed to add member: ' + e.message);
    }
  }

  async function removeMember(userId, username) {
    if (!confirm(`Remove ${username} from this team?`)) return;

    try {
      await api.admin.teams.members.remove(selectedTeam.id, userId);
      teamMembers = teamMembers.filter(m => m.user_id !== userId);
      await loadAvailableMembers(selectedTeam.id);
    } catch (e) {
      alert('Failed to remove member: ' + e.message);
    }
  }
</script>

<div class="tab-header">
  <h2>Teams</h2>
  <button class="create-btn" onclick={() => showCreateTeamModal = true}>New Team</button>
</div>

{#if teamsLoading}
  <div class="loading">Loading teams...</div>
{:else if teams.length === 0}
  <div class="empty-state">No teams found</div>
{:else}
  <div class="teams-grid">
    {#each teams as team (team.id)}
      <div class="team-card">
        <div class="team-info">
          <h3>{team.name}</h3>
          <p class="org-badge">Org: {team.organization_name}</p>
        </div>
        <div class="team-stats">
          <div class="stat">
            <span class="stat-value">{team.member_count}</span>
            <span class="stat-label">Members</span>
          </div>
        </div>
        <div class="team-actions">
          <button class="action-btn" onclick={() => openMembersModal(team)}>Members</button>
          <button class="action-btn" onclick={() => openEditTeam(team)}>Edit</button>
          <button class="action-btn delete" onclick={() => deleteTeam(team.id)}>Delete</button>
        </div>
      </div>
    {/each}
  </div>
{/if}

{#if showCreateTeamModal}
  <Modal open={showCreateTeamModal} onClose={() => showCreateTeamModal = false} title="Create Team">
    {#snippet children()}
      <h2>Create New Team</h2>
      <form onsubmit={(e) => { e.preventDefault(); createTeam(); }}>
        <label>
          Name
          <input
            type="text"
            bind:value={newTeamName}
            placeholder="Enter team name"
            required
          />
        </label>
        <label>
          Organization
          <select bind:value={newTeamOrgId} required>
            <option value="">Select organization...</option>
            {#each organizations as org}
              <option value={org.id}>{org.name}</option>
            {/each}
          </select>
        </label>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" onclick={() => showCreateTeamModal = false}>Cancel</button>
          <button type="submit" class="create-btn">Create Team</button>
        </div>
      </form>
    {/snippet}
  </Modal>
{/if}

{#if showEditTeamModal}
  <Modal open={showEditTeamModal} onClose={() => showEditTeamModal = false} title="Edit Team">
    {#snippet children()}
      <h2>Edit Team: {selectedTeam?.name}</h2>
      <form onsubmit={(e) => { e.preventDefault(); updateTeam(); }}>
        <label>
          Name
          <input
            type="text"
            bind:value={editTeamName}
            placeholder="Enter team name"
            required
          />
        </label>
        <label>
          Organization
          <select bind:value={editTeamOrgId} required>
            <option value="">Select organization...</option>
            {#each organizations as org}
              <option value={org.id}>{org.name}</option>
            {/each}
          </select>
        </label>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" onclick={() => showEditTeamModal = false}>Cancel</button>
          <button type="submit" class="create-btn">Save Changes</button>
        </div>
      </form>
    {/snippet}
  </Modal>
{/if}

{#if showMembersModal}
  <Modal open={showMembersModal} onClose={() => showMembersModal = false} title="Manage Members">
    {#snippet children()}
      <h2>Team Members: {selectedTeam?.name}</h2>

      <div class="members-section">
        <h3>Add Member</h3>
        <form onsubmit={(e) => { e.preventDefault(); addMember(); }}>
          <div class="add-member-form">
            <select bind:value={addMemberUsername} required>
              <option value="">Select user to add...</option>
              {#each availableMembers as member}
                <option value={member.username}>{member.username}</option>
              {/each}
              {#if availableMembers.length === 0}
                <option disabled value="">No available users (all org members are already on this team)</option>
              {/if}
            </select>
            <button type="submit" class="add-btn" disabled={!addMemberUsername || availableMembers.length === 0}>Add</button>
          </div>
        </form>
      </div>

      <div class="members-section">
        <h3>Current Members ({teamMembers.length})</h3>
        {#if teamMembers.length === 0}
          <p class="no-members">No members yet</p>
        {:else}
          <div class="members-list">
            {#each teamMembers as member (member.id)}
              <div class="member-item">
                <span class="member-username">@{member.username}</span>
                <button class="remove-btn" onclick={() => removeMember(member.user_id, member.username)}>Remove</button>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="modal-actions">
        <button type="button" class="cancel-btn" onclick={() => showMembersModal = false}>Close</button>
      </div>
    {/snippet}
  </Modal>
{/if}

<style>
  .loading, .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: var(--color-muted-foreground);
  }

  .tab-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }

  .tab-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-foreground);
    margin: 0;
  }

  .create-btn {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
  }

  .create-btn:hover {
    opacity: 0.9;
  }

  .teams-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1rem;
  }

  .team-card {
    background: var(--color-card);
    border: 1px solid var(--color-border);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .team-info h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.25rem 0;
  }

  .team-info .org-badge {
    font-size: 0.875rem;
    color: var(--color-muted-foreground);
    margin: 0;
  }

  .team-stats {
    display: flex;
    gap: 1.5rem;
    margin: 1rem 0;
  }

  .stat {
    display: flex;
    flex-direction: column;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-primary);
  }

  .stat-label {
    font-size: 0.75rem;
    color: var(--color-muted-foreground);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .team-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .team-actions button {
    flex: 1;
  }

  .action-btn {
    padding: 0.5rem;
    font-size: 0.875rem;
    background: var(--color-muted);
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
    border-radius: 6px;
  }

  .action-btn:hover {
    background: var(--color-border);
  }

  .action-btn.delete {
    color: var(--color-destructive);
    border-color: var(--color-destructive);
  }

  .action-btn.delete:hover {
    background: var(--color-destructive);
    color: var(--color-destructive-foreground);
  }

  .members-section {
    margin-bottom: 2rem;
  }

  .members-section h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-foreground);
    margin: 0 0 0.75rem 0;
  }

  .add-member-form {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
  }

  .add-member-form select {
    flex: 1;
  }

  .add-btn {
    background: var(--color-primary);
    color: var(--color-primary-foreground);
    border: none;
    padding: 0.75rem 1.25rem;
    font-size: 0.875rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    white-space: nowrap;
  }

  .add-btn:hover:not(:disabled) {
    opacity: 0.9;
  }

  .add-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .no-members {
    color: var(--color-muted-foreground);
    font-style: italic;
  }

  .members-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .member-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: var(--color-muted);
    border-radius: 6px;
  }

  .member-username {
    font-weight: 500;
    color: var(--color-foreground);
  }

  .remove-btn {
    background: transparent;
    color: var(--color-destructive);
    border: 1px solid var(--color-destructive);
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    border-radius: 4px;
    cursor: pointer;
  }

  .remove-btn:hover {
    background: var(--color-destructive);
    color: var(--color-destructive-foreground);
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  label {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--color-foreground);
  }

  select, input {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 8px;
    border: 1px solid var(--color-border);
    background: var(--color-card);
    color: var(--color-foreground);
    transition: border-color 0.15s ease;
    width: 100%;
  }

  select:focus, input:focus {
    outline: none;
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px var(--color-primary);
  }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .cancel-btn {
    background: transparent;
    color: var(--color-foreground);
    border: 1px solid var(--color-border);
  }

  .cancel-btn:hover {
    background: var(--color-muted);
  }

  button {
    padding: 0.75rem 1rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
  }
</style>
