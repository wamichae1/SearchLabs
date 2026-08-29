"""Bidirectional BFS scaffolding.

This module is intentionally a stub. The algorithm has NOT been
implemented yet, so it must NOT be registered in the UI until the
generator below yields real events.

To implement Bidirectional BFS:

* Keep this file free of ``pygame`` imports - algorithms communicate
  with the visualizer only through the event contract in ``grid.py``.
* ``grid.neighbors(row, col)`` returns in-bounds neighbor cells but
  does NOT skip walls; filter ``CellState.WALL`` yourself.
* A bidirectional search expands two frontiers (one from ``start``,
  one from ``goal``) until they meet, then reconstructs a single path.
  You will need two ``came_from`` maps (one per direction), a meeting
  cell, and shared visited sets so expansions can be announced with the
  existing events:

      from grid import Current, Discover, PathNode, Finished

  * ``Current(row, col)``   - cell being expanded right now.
  * ``Discover(row, col)``  - cell added to a frontier.
  * ``PathNode(row, col)``  - cell on the final reconstructed path.
  * ``Finished(found=bool)``- search complete.

The visualizer calls ``bidirectional_bfs(grid, start, goal)`` and
steps its returned generator one event at a time, so the function
above must be a generator that yields the events above.

The ``NotImplementedError`` below lets the scaffold be imported safely
without pretending the search works.
"""

from grid import Finished


def bidirectional_bfs(grid, start, goal):
    """Bidirectional BFS.

    Expand two FIFO frontiers concurrently - one outward from ``start``
    and one backward from ``goal`` - until the two searches meet. When a
    meeting cell is found, stitch the forward and backward
    ``came_from`` trees together to reconstruct a path, then yield
    ``PathNode`` events and ``Finished(found=True)``.

    NOTE: This is a stub. Replace the body with a real generator.
    """
    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "Bidirectional BFS is a scaffold - implement the generator body."
    )
