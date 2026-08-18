"""Bidirectional Search - skeleton.
"""
from grid import Finished

def bidirectional(grid, start, goal):
    if start is None or goal is None:
        yield Finished(found=False)
        return
    raise NotImplementedError("Bidirectional Search is not implemented yet - fill in bidirectional.py")
