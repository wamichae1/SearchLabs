"""Depth-First Search — skeleton.

Read bfs.py first. It is the worked example for the event
protocol and the came_from / frontier pattern you reuse here.

DEPTH-FIRST SEARCH
  Strategy  Plunge down one branch as far as possible, then
            backtrack to the most recent unfinished branch.
  Data      A stack (LIFO): the last node discovered is the
            first one expanded.
  Complete  Yes on a finite grid — it eventually tries every
            reachable cell, though it can dive very deep.
  Optimal   No. The first path it reaches the goal by is
            rarely the shortest one.

YOUR JOB
  This is BFS with essentially one change — the data
  structure and the order you take nodes from it:
    1. Use a list as a stack:
           frontier.append(node)        # push
           current = frontier.pop()     # take the NEWEST (LIFO)
       Compare with bfs.py, which uses deque + popleft (FIFO).
    2. Everything else — came_from, the neighbor loop, the
       wall check, the goal test, the path reconstruction,
       and the events you yield — is identical to bfs.py.

  The import below only pulls Finished (used by the guard).
  When you write the body, extend it to also import the
  events and states you need:
      from grid import (
          CellState, Current, Discover, PathNode, Finished
      )

  Then delete the raise and write your code. The visualizer
  picks DFS up automatically once it yields real events.
"""

from grid import (
    CellState,
    Current,
    Discover,
    PathNode,
    Finished,
)

def dfs(grid, start, goal):

    if start is None or goal is None:
        yield Finished(found=False)
        return

    came_from = {start: None}

    frontier = [start]

    while frontier:

        current  = frontier.pop()
        # Annouce the node expanding
        yield Current(current[0],current[1])
        # Check if node is the goal
        if current  == goal:

            path = []
            node = goal

            while node is not None:
                path.append(node)
                node = came_from[node]

            path.reverse()
            # Draw out the path from start to goal
            for cell in path:
                yield PathNode(cell[0], cell[1])

            yield Finished(found=True)
            return

        for neighbor in grid.neighbors(current[0], current[1]):
            position = (neighbor.row, neighbor.col)

            if neighbor.state == CellState.WALL:
                continue

            if position not in came_from:
                came_from[position] = current
                frontier.append(position)
                yield Discover(position[0], position[1])
            
    # Frontier exhausted without reaching the goal.
    yield Finished(found=False)