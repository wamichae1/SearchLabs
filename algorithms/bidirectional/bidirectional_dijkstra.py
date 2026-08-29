"""Bidirectional Dijkstra scaffolding.

This module is intentionally a stub. The algorithm has NOT been
implemented yet, so it must NOT be registered in the UI until the
generator below yields real events.

To implement Bidirectional Dijkstra:

* Keep this file free of ``pygame`` imports; use only the event
  contract from ``grid.py``.
* ``grid.neighbors(row, col)`` returns in-bounds neighbor cells but
  does NOT skip walls; filter ``CellState.WALL`` yourself.
* ``cell.weight`` is the terrain weight to factor into cost.
* Expand two priority-queue frontiers (one from ``start``, one from
  ``goal``), each keyed by accumulated cost. Use a tie-breaker so
  forward/backward expansions alternate predictably. Stop when the
  best candidate is dominated by the best meeting-point cost, then
  reconstruct the path across the meeting cell:

      from grid import Current, Discover, PathNode, Finished

  * ``Current(row, col)``   - cell being expanded right now.
  * ``Discover(row, col)``  - cell added to a frontier.
  * ``PathNode(row, col)``  - cell on the final reconstructed path.
  * ``Finished(found=bool)``- search complete.

The ``NotImplementedError`` below lets the scaffold be imported safely
without pretending the search works.
"""

from grid import Finished


def bidirectional_dijkstra(grid, start, goal):
    """Bidirectional Dijkstra.

    Run two simultaneous Dijkstra searches from ``start`` and
    ``goal`` over weighted edges (``cell.weight + 1`` per step) until
    the frontiers meet at the lowest possible cost, then reconstruct
    the weighted shortest path.

    NOTE: This is a stub. Replace the body with a real generator.
    """
    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "Bidirectional Dijkstra is a scaffold - implement the generator body."
    )
