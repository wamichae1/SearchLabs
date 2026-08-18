"""Dijkstra's Algorithm - skeleton.

Read bfs.py first for the event protocol.
"""
from grid import Finished

def dijkstra(grid, start, goal):
    if start is None or goal is None:
        yield Finished(found=False)
        return
    raise NotImplementedError("Dijkstra is not implemented yet - fill in dijkstra.py")
