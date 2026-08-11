from collections import deque

from grid import (
    CellState,
    Current,
    Discover,
    PathNode,
    Finished,
)


# ============================================================
# REFERENCE: BREADTH-FIRST SEARCH
#
# This is reference material. Study it, then implement your
# own searches (DFS, Dijkstra, A*, Greedy, ...) against the
# same event contract defined in grid.py.
#
# BFS expands nodes in order of distance from the start, so
# the first path it finds to the goal is guaranteed to be a
# shortest one (on an unweighted grid).
# ============================================================

def bfs(grid, start, goal):

    if start is None or goal is None:
        yield Finished(found=False)
        return

    # Trace `came_from` so we can rebuild the path once the
    # goal is reached. A node's presence in this dict also
    # means it has already been discovered.
    came_from = {start: None}

    frontier = deque([start])

    while frontier:

        current = frontier.popleft()

        # Announce the node we are expanding now.
        yield Current(current[0], current[1])

        if current == goal:

            path = []
            node = goal

            while node is not None:
                path.append(node)
                node = came_from[node]

            path.reverse()

            for cell in path:
                yield PathNode(cell[0], cell[1])

            yield Finished(found=True)
            return

        for neighbor in grid.neighbors(current[0], current[1]):

            position = (neighbor.row, neighbor.col)

            # Walls are not traversable.
            if neighbor.state == CellState.WALL:
                continue

            if position not in came_from:
                came_from[position] = current
                frontier.append(position)
                yield Discover(position[0], position[1])

    # Frontier exhausted without reaching the goal.
    yield Finished(found=False)
