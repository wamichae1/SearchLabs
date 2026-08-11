"""Greedy Best-First Search — skeleton.

Read bfs.py first for the event protocol.

GREEDY BEST-FIRST
  Strategy  Always expand the node that looks closest to the
            goal, using ONLY the heuristic h. It ignores the
            cost so far, so it races straight toward the goal.
  Data      A priority queue (min-heap) keyed by h.
  Heuristic Manhattan distance (see astar.py):
                h(a, b) = |a.row - b.row| + |a.col - b.col|
  Complete  Yes on a finite grid (with a visited check).
  Optimal   No. It is fast and often finds a path quickly,
            but that path is usually not the shortest,
            because cost-so-far is ignored. Compare it side
            by side with A* to see the trade-off.

YOUR JOB
  Same skeleton as A*, but the heap key is just
  manhattan(pos, goal) instead of g + h. You still need a
  visited check (membership in came_from works) so you do
  not keep re-expanding the same cell.

  Extend the import below with:
      from grid import (
          CellState, Current, Discover, PathNode, Finished
      )
  and add at the top:
      import heapq

  The manhattan() helper below is provided. Sketch:
    came_from = {start: None}
    heap = [(manhattan(start, goal), start)]
    while heap:
        _, current = heapq.heappop(heap)
        if current in expanded:        # track what you've popped
            continue
        expanded.add(current)
        yield Current(current[0], current[1])
        if current == goal:
            ... rebuild path from came_from ...
            for cell in path: yield PathNode(cell[0], cell[1])
            yield Finished(found=True)
            return
        for neighbor in grid.neighbors(current[0], current[1]):
            if neighbor.state == CellState.WALL:
                continue
            pos = (neighbor.row, neighbor.col)
            if pos not in came_from:
                came_from[pos] = current
                heapq.heappush(heap, (manhattan(pos, goal), pos))
                yield Discover(pos[0], pos[1])
    yield Finished(found=False)

  Delete the raise and write it.
"""

from grid import Finished


def manhattan(a, b):
    """Manhattan distance between two (row, col) points."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def greedy(grid, start, goal):

    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "Greedy is not implemented yet — fill in greedy.py"
    )
