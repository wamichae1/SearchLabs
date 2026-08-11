"""A* Search — skeleton.

Read bfs.py first for the event protocol.

A-STAR
  Strategy  Like Dijkstra, but the priority is
                f = g + h
            where g is the cost so far and h is a heuristic
            estimating the remaining cost to the goal.
  Data      A priority queue (min-heap) keyed by f.
  Heuristic On a 4-connected grid, the Manhattan distance is
            admissible, so A* stays optimal:
                h(a, b) = |a.row - b.row| + |a.col - b.col|
  Complete  Yes.
  Optimal   Yes, as long as h never overestimates the true
            remaining cost (admissible). Manhattan distance
            qualifies on a grid with unit step costs.

YOUR JOB
  Same skeleton as Dijkstra, but each heap entry is
  (f, g, node) and you recompute f = g + manhattan(pos, goal)
  when you push. Keep a `g_score` (best-known cost) dict and
  skip heap entries whose g is stale.

  Extend the import below with:
      from grid import (
          CellState, Current, Discover, PathNode, Finished
      )
  and add at the top:
      import heapq

  The manhattan() helper below is provided — focus on the
  search loop. Sketch:
    from math import inf
    g = {start: 0}
    came_from = {start: None}
    heap = [(manhattan(start, goal), 0, start)]
    while heap:
        f, cost, current = heapq.heappop(heap)
        if cost > g.get(current, inf):       # stale entry
            continue
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
            tentative = cost + 1
            if tentative < g.get(pos, inf):
                g[pos] = tentative
                came_from[pos] = current
                heapq.heappush(
                    heap,
                    (tentative + manhattan(pos, goal), tentative, pos)
                )
                yield Discover(pos[0], pos[1])
    yield Finished(found=False)

  Delete the raise and write it.
"""

from grid import Finished


def manhattan(a, b):
    """Manhattan distance between two (row, col) points.

    Admissible on a 4-connected grid with unit step costs,
    so A* stays optimal when you use it as the heuristic.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal):

    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "A* is not implemented yet — fill in astar.py"
    )
