"""Theta* Search - skeleton.
"""
from grid import Finished

def thetastar(grid, start, goal):
    if start is None or goal is None:
        yield Finished(found=False)
        return
    raise NotImplementedError("Theta* Search is not implemented yet - fill in thetastar.py")
