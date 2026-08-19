import { describe, it, expect, vi } from 'vitest';
import { TRIGGERS } from 'svelte-dnd-action';
import { createBoardDnd } from './boardDnd.js';

const card = (id) => ({ id, title: 'card ' + id, description: null, position: 0 });

function harness(initialColumns) {
  let columns = initialColumns;
  const api = {
    cards: { reorder: vi.fn().mockResolvedValue({}), update: vi.fn().mockResolvedValue({}) },
    columns: { reorder: vi.fn().mockResolvedValue({}) },
  };
  const reload = vi.fn();
  const onError = vi.fn();
  const dnd = createBoardDnd({
    getColumns: () => columns,
    setColumns: (next) => { columns = next; },
    api, reload, onError,
  });
  return { dnd, api, reload, onError, get columns() { return columns; } };
}

const consider = (items, trigger) => ({ detail: { items, info: { trigger } } });
const finalize = (items) => ({ detail: { items, info: { trigger: TRIGGERS.DROPPED_INTO_ZONE } } });

// Todo holds cards 1 and 2; Done holds card 3.
const board = () => ([
  { id: 10, name: 'Todo', cards: [card(1), card(2)] },
  { id: 20, name: 'Done', cards: [card(3)] },
]);

describe('createBoardDnd - consider', () => {
  it('writes the in-flight order into the column being hovered', () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    expect(h.columns[0].cards.map(c => c.id)).toEqual([2, 1]);
    expect(h.columns[1].cards.map(c => c.id)).toEqual([3]);
  });

  it('leaves the other columns untouched', () => {
    const h = harness(board());
    const doneBefore = h.columns[1];
    h.dnd.considerCards(10, consider([card(1)], TRIGGERS.DRAG_STARTED));
    expect(h.columns[1]).toBe(doneBefore);
  });
});

describe('createBoardDnd - the drag guard', () => {
  it('ignores a finalize that no drag ever started', async () => {
    const h = harness(board());
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));
    expect(h.api.cards.reorder).not.toHaveBeenCalled();
    expect(h.columns[0].cards.map(c => c.id)).toEqual([1, 2]);
  });

  it('ignores a finalize arriving after the drag was abandoned', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    h.dnd.considerCards(10, consider([card(1), card(2)], TRIGGERS.DRAG_STOPPED));
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));
    expect(h.api.cards.reorder).not.toHaveBeenCalled();
  });

  it('ignores a second finalize once the first has fully resolved', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));
    h.api.cards.reorder.mockClear();
    await h.dnd.finalizeCards(10, finalize([card(1), card(2)]));
    expect(h.api.cards.reorder).not.toHaveBeenCalled();
  });
});

describe('createBoardDnd - reordering within one column', () => {
  it('renumbers positions from zero and sends them', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));

    expect(h.api.cards.reorder).toHaveBeenCalledWith([
      { id: 2, position: 0 },
      { id: 1, position: 1 },
    ]);
    expect(h.columns[0].cards.map(c => [c.id, c.position])).toEqual([[2, 0], [1, 1]]);
  });

  it('does not touch column_id when nothing crossed columns', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));
    expect(h.api.cards.update).not.toHaveBeenCalled();
  });
});

describe('createBoardDnd - moving a card between columns', () => {
  // A cross-column move finalizes twice, once per zone. Only the target may
  // rewrite column_id; the source just renumbers what it has left.
  it('reassigns column_id on the target column only', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(1), card(2)], TRIGGERS.DRAG_STARTED));

    await h.dnd.finalizeCards(20, finalize([card(2), card(3)]));

    expect(h.api.cards.update).toHaveBeenCalledTimes(1);
    expect(h.api.cards.update).toHaveBeenCalledWith(2, 'card 2', null, 0, 20);
  });

  it('renumbers the source column without reassigning anything', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(1), card(2)], TRIGGERS.DRAG_STARTED));

    await h.dnd.finalizeCards(10, finalize([card(1)]));

    expect(h.api.cards.reorder).toHaveBeenCalledWith([{ id: 1, position: 0 }]);
    expect(h.api.cards.update).not.toHaveBeenCalled();
  });

  it('lets both zones finalize when they are dispatched together', async () => {
    const h = harness(board());
    h.dnd.considerCards(10, consider([card(1), card(2)], TRIGGERS.DRAG_STARTED));

    await Promise.all([
      h.dnd.finalizeCards(10, finalize([card(1)])),
      h.dnd.finalizeCards(20, finalize([card(2), card(3)])),
    ]);

    expect(h.api.cards.reorder).toHaveBeenCalledTimes(2);
    expect(h.api.cards.update).toHaveBeenCalledTimes(1);
  });
});

describe('createBoardDnd - rollback', () => {
  it('re-fetches the board when the reorder call fails', async () => {
    const h = harness(board());
    h.api.cards.reorder.mockRejectedValue(new Error('boom'));
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));

    expect(h.reload).toHaveBeenCalledTimes(1);
    expect(h.onError).toHaveBeenCalled();
  });

  it('re-fetches when the cross-column update fails', async () => {
    const h = harness(board());
    h.api.cards.update.mockRejectedValue(new Error('boom'));
    h.dnd.considerCards(10, consider([card(1), card(2)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(20, finalize([card(2), card(3)]));
    expect(h.reload).toHaveBeenCalledTimes(1);
  });

  it('clears drag state after a failure, so the next drag still works', async () => {
    const h = harness(board());
    h.api.cards.reorder.mockRejectedValueOnce(new Error('boom'));
    h.dnd.considerCards(10, consider([card(2), card(1)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(10, finalize([card(2), card(1)]));

    h.dnd.considerCards(10, consider([card(1), card(2)], TRIGGERS.DRAG_STARTED));
    await h.dnd.finalizeCards(10, finalize([card(1), card(2)]));
    expect(h.api.cards.reorder).toHaveBeenCalledTimes(2);
  });
});

describe('createBoardDnd - reordering columns', () => {
  it('renumbers columns and syncs the order', async () => {
    const h = harness(board());
    await h.dnd.finalizeColumns({ detail: { items: [h.columns[1], h.columns[0]] } });

    expect(h.columns.map(c => [c.id, c.position])).toEqual([[20, 0], [10, 1]]);
    expect(h.api.columns.reorder).toHaveBeenCalledWith([
      { id: 20, position: 0 },
      { id: 10, position: 1 },
    ]);
  });

  it('re-fetches the board when the column reorder fails', async () => {
    const h = harness(board());
    h.api.columns.reorder.mockRejectedValue(new Error('boom'));
    await h.dnd.finalizeColumns({ detail: { items: [h.columns[1], h.columns[0]] } });
    expect(h.reload).toHaveBeenCalledTimes(1);
  });

  it('swaps the array wholesale on consider', () => {
    const h = harness(board());
    h.dnd.considerColumns({ detail: { items: [h.columns[1], h.columns[0]] } });
    expect(h.columns.map(c => c.id)).toEqual([20, 10]);
  });
});
