"""Dijkstra's Algorithm — skeleton.

Read bfs.py first for the event protocol.

DIJKSTRA
  Strategy  Expand the node with the smallest total cost
            from the start. Costs accumulate as you move.
  Data      A priority queue (min-heap) keyed by distance.
  Complete  Yes.
  Optimal   Yes — it finds the minimum-cost path.
            On an unweighted grid (every step costs 1) it
            behaves exactly like BFS, so the interesting
            case is a grid with weighted terrain. If you
            only ever use unit costs, you can stop at BFS.

YOUR JOB
  Same shape as BFS, but instead of a FIFO queue you use a
  min-heap of (cost, node) and a `dist` dictionary of the
  best-known cost to each cell. When you reach a neighbor
  more cheaply than recorded, you relax it and push it back.

  Extend the import below with:
      from grid import (
          CellState, Current, Discover, PathNode, Finished
      )
  and add at the top:
      import heapq

  Sketch:
    from math import inf               # or use float('inf')
    dist = {start: 0}
    came_from = {start: None}
    heap = [(0, start)]
    while heap:
        cost, current = heapq.heappop(heap)
        if cost > dist.get(current, inf):    # stale entry
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
            step_cost = 1                  # or read a weight
            new_cost = cost + step_cost
            if new_cost < dist.get(pos, inf):
                dist[pos] = new_cost
                came_from[pos] = current
                heapq.heappush(heap, (new_cost, pos))
                yield Discover(pos[0], pos[1])
    yield Finished(found=False)

  The stale-entry check matters: a cell can be pushed several
  times with improving costs; skip a popped entry whose cost
  is worse than the best you already recorded. Delete the raise
  and write it.
"""

from grid import Finished


def dijkstra(grid, start, goal):

    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "Dijkstra is not implemented yet — fill in dijkstra.py"
    )
