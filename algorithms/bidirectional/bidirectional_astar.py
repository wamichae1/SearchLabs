"""Bidirectional A* scaffolding.

This module is intentionally a stub. The algorithm has NOT been
implemented yet, so it must NOT be registered in the UI until the
generator below yields real events.

To implement Bidirectional A*:

* Keep this file free of ``pygame`` imports; use only the event
  contract from ``grid.py``.
* ``grid.neighbors(row, col)`` returns in-bounds neighbor cells but
  does NOT skip walls; filter ``CellState.WALL`` yourself.
* ``cell.weight`` is the terrain weight to factor into cost.
* Maintain two priority-queue frontiers (one from ``start``, one from
  ``goal``), each ordered by ``f = g + h`` with an admissible
  heuristic (Manhattan distance is a safe default on this grid).
  Alternate expansions between the frontiers, and terminate when the
  best meeting cell cannot be improved. Reconstruct the path across the
  meeting cell:

      from grid import Current, Discover, PathNode, Finished

  * ``Current(row, col)``   - cell being expanded right now.
  * ``Discover(row, col)``  - cell added to a frontier.
  * ``PathNode(row, col)``  - cell on the final reconstructed path.
  * ``Finished(found=bool)``- search complete.

The ``NotImplementedError`` below lets the scaffold be imported safely
without pretending the search works.
"""

from grid import Finished


def bidirectional_astar(grid, start, goal):
    """Bidirectional A*.

    Run two simultaneous A* searches from ``start`` and ``goal``,
    each guiding expansion with ``f(n) = g(n) + h(n)`` over weighted
    edges, stopping when the frontiers meet at the lowest f-cost and
    reconstructing the path across the meeting cell.

    NOTE: This is a stub. Replace the body with a real generator.
    """
    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "Bidirectional A* is a scaffold - implement the generator body."
    )
