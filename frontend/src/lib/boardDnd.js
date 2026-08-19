import { TRIGGERS } from 'svelte-dnd-action';

/**
 * Drag-and-drop state for a board, extracted from BoardView so it can be
 * tested without driving a real drag.
 *
 * svelte-dnd-action fires `consider` continuously while a card is in flight
 * and `finalize` once per affected zone on drop -- which means a cross-column
 * move finalizes *twice*, once on the source column and once on the target.
 * Both need to renumber their own cards, and only the target needs to move the
 * card between columns, so the two calls have to be distinguishable. That is
 * what the snapshot taken at DRAG_STARTED is for: a column's "new" cards are
 * the ones absent from its own pre-drag card list.
 *
 * The caller owns the column array (it is Svelte $state in BoardView), so this
 * reads and writes it through accessors rather than holding it.
 *
 * @param {object} deps
 * @param {() => Array} deps.getColumns   current columns
 * @param {(cols: Array) => void} deps.setColumns  replace columns
 * @param {object} deps.api               api client ({ cards, columns })
 * @param {() => any} deps.reload         re-fetch the board, used to roll back
 * @param {(msg: string, err: Error) => void} [deps.onError]  defaults to console.error
 */
export function createBoardDnd({ getColumns, setColumns, api, reload, onError }) {
  // The board as it looked before the current drag began. Cleared once the
  // drag resolves; a finalize arriving without it has nothing to diff against.
  let originalColumnsState = null;
  let isDragInProgress = false;

  const report = onError || ((msg, err) => console.error(msg, err));

  function replaceCards(columnId, cards) {
    setColumns(getColumns().map(col => (col.id === columnId ? { ...col, cards } : col)));
  }

  function considerCards(columnId, e) {
    const { items, info } = e.detail;

    if (info.trigger === TRIGGERS.DRAG_STARTED) {
      originalColumnsState = JSON.parse(JSON.stringify(getColumns()));
      isDragInProgress = true;
    }

    // The drag ended without a drop (escape, or released outside any zone).
    // consider has already put the card back, so just drop the snapshot.
    if (info.trigger === TRIGGERS.DRAG_STOPPED) {
      isDragInProgress = false;
      originalColumnsState = null;
    }

    replaceCards(columnId, items);
  }

  async function finalizeCards(columnId, e) {
    // No drag ever started, or this one already resolved: a finalize here would
    // diff against a snapshot that no longer describes the pre-drag board.
    if (!isDragInProgress) return;

    const { items } = e.detail;

    if (!originalColumnsState) {
      originalColumnsState = JSON.parse(JSON.stringify(getColumns()));
    }

    const originalColumn = originalColumnsState.find(col => col.id === columnId);
    const originalCardIds = new Set(originalColumn?.cards.map(c => c.id) || []);

    const columnCards = items.map((card, index) => ({ ...card, position: index }));

    // Show the new order immediately; roll back below if the server disagrees.
    replaceCards(columnId, columnCards);

    // Absent from this column before the drag => it came from another one, so
    // its column_id is now stale on the server.
    const newCards = columnCards.filter(card => !originalCardIds.has(card.id));

    const reorderItems = columnCards.map((card, index) => ({ id: card.id, position: index }));

    try {
      await api.cards.reorder(reorderItems);

      for (const card of newCards) {
        await api.cards.update(
          card.id,
          card.title,
          card.description || null,
          card.position,
          columnId
        );
      }
    } catch (err) {
      report('Failed to reorder cards:', err);
      reload();
    } finally {
      originalColumnsState = null;
      isDragInProgress = false;
    }
  }

  function considerColumns(e) {
    setColumns(e.detail.items);
  }

  async function finalizeColumns(e) {
    const newColumns = e.detail.items.map((col, index) => ({ ...col, position: index }));
    setColumns(newColumns);

    const reorderItems = newColumns.map((col, index) => ({ id: col.id, position: index }));

    try {
      await api.columns.reorder(reorderItems);
    } catch (err) {
      report('Failed to reorder columns:', err);
      reload();
    }
  }

  return { considerCards, finalizeCards, considerColumns, finalizeColumns };
}
