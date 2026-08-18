"""A* Search - skeleton.

Read bfs.py first for the event protocol.
"""

from grid import Finished


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(grid, start, goal):

    if start is None or goal is None:
        yield Finished(found=False)
        return

    raise NotImplementedError(
        "A* is not implemented yet - fill in astar.py"
    )
