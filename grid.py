import random
from dataclasses import dataclass
from enum import Enum, auto


# ============================================================
# GRID SIZES
# ============================================================

DEFAULT_GRID_SIZE = 25
MIN_GRID_SIZE = 10
MAX_GRID_SIZE = 50


# ============================================================
# CELL STATES
# ============================================================

class CellState(Enum):
    EMPTY = auto()
    WALL = auto()
    START = auto()
    GOAL = auto()
    FRONTIER = auto()
    CURRENT = auto()
    VISITED = auto()
    PATH = auto()


# ============================================================
# EVENT CONTRACT
#
# Search algorithms are generators that yield these events.
# An algorithm must NOT import pygame — it talks to the
# visualizer only through this protocol.
#
# Typical flow per node expansion:
#
#     yield Current(...)          # node being expanded now
#     for neighbor in ...:
#         yield Discover(...)     # neighbor joined the frontier
#     ...
#     yield PathNode(...)         # cell on the final path
#     yield Finished(found)      # exactly once, at the end
#
# The visualizer paints states as follows:
#
#     Frontier  = queued, will be expanded later
#     Current  = being expanded right now (transient; settles
#                into Visited when the next node is expanded)
#     Visited  = fully processed
#     Path     = on the reconstructed path
#
# To add a new search, write a generator that yields these
# events and register it in main.py.
# ============================================================

@dataclass(frozen=True)
class Discover:
    """A cell was added to the frontier."""
    row: int
    col: int


@dataclass(frozen=True)
class Current:
    """The cell being expanded right now. The previous
    current cell settles into Visited automatically."""
    row: int
    col: int


@dataclass(frozen=True)
class PathNode:
    """A cell on the final reconstructed path."""
    row: int
    col: int


@dataclass(frozen=True)
class Finished:
    """The search completed. `found` is False when no path
    exists between start and goal."""
    found: bool


# ============================================================
# CELL
# ============================================================

@dataclass
class Cell:
    row: int
    col: int
    state: CellState = CellState.EMPTY


# ============================================================
# GRID
# ============================================================

class Grid:

    def __init__(self, size=DEFAULT_GRID_SIZE):
        self.size = size
        self.cells = []

        self.start = None
        self.goal = None

        self.reset(size)

    def reset(self, size=None):

        if size is not None:
            self.size = max(
                MIN_GRID_SIZE,
                min(MAX_GRID_SIZE, size)
            )

        self.cells = [
            [
                Cell(row, col)
                for col in range(self.size)
            ]
            for row in range(self.size)
        ]

        self.start = None
        self.goal = None

        # Default start
        self.set_start(
            self.size // 2,
            self.size // 5
        )

        # Default goal
        self.set_goal(
            self.size // 2,
            self.size - self.size // 5 - 1
        )

    def get(self, row, col):

        if 0 <= row < self.size and 0 <= col < self.size:
            return self.cells[row][col]

        return None

    def neighbors(self, row, col):
        """Returns in-bounds neighbors. Note: this does
        NOT skip walls — the search algorithm must decide
        which cells are traversable."""

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        result = []

        for dr, dc in directions:

            cell = self.get(
                row + dr,
                col + dc
            )

            if cell is not None:
                result.append(cell)

        return result

    def set_start(self, row, col):

        cell = self.get(row, col)

        if cell is None:
            return

        if cell.state == CellState.WALL:
            return

        # Refuse to place the start on the goal cell; the
        # two endpoints must never overlap.
        if self.goal == (row, col):
            return

        # Remove previous start
        if self.start is not None:

            old = self.get(*self.start)

            if old is not None:
                old.state = CellState.EMPTY

        cell.state = CellState.START
        self.start = (row, col)

    def set_goal(self, row, col):

        cell = self.get(row, col)

        if cell is None:
            return

        if cell.state == CellState.WALL:
            return

        # Refuse to place the goal on the start cell; the
        # two endpoints must never overlap.
        if self.start == (row, col):
            return

        # Remove previous goal
        if self.goal is not None:

            old = self.get(*self.goal)

            if old is not None:
                old.state = CellState.EMPTY

        cell.state = CellState.GOAL
        self.goal = (row, col)

    def clear_walls(self):

        for row in self.cells:

            for cell in row:

                if cell.state == CellState.WALL:
                    cell.state = CellState.EMPTY

    def clear_search(self):

        for row in self.cells:

            for cell in row:

                if cell.state in (
                    CellState.FRONTIER,
                    CellState.CURRENT,
                    CellState.VISITED,
                    CellState.PATH
                ):
                    cell.state = CellState.EMPTY

        if self.start is not None:

            start_cell = self.get(*self.start)

            if start_cell is not None:
                start_cell.state = CellState.START

        if self.goal is not None:

            goal_cell = self.get(*self.goal)

            if goal_cell is not None:
                goal_cell.state = CellState.GOAL

    def randomize_start_goal(self):

        available = []

        for row in range(self.size):

            for col in range(self.size):

                cell = self.get(row, col)

                if cell.state != CellState.WALL:
                    available.append((row, col))

        if len(available) < 2:
            return

        start = random.choice(available)

        remaining = [
            position
            for position in available
            if position != start
        ]

        goal = random.choice(remaining)

        for row in self.cells:

            for cell in row:

                if cell.state in (
                    CellState.START,
                    CellState.GOAL
                ):
                    cell.state = CellState.EMPTY

        self.start = None
        self.goal = None

        self.set_start(*start)
        self.set_goal(*goal)

    def generate_random_walls(self, density=0.30):

        self.clear_walls()

        for row in self.cells:

            for cell in row:

                if cell.state in (
                    CellState.START,
                    CellState.GOAL
                ):
                    continue

                if random.random() < density:
                    cell.state = CellState.WALL

    def generate_maze(self):

        self.clear_walls()

        def divide(x, y, width, height):

            if width < 3 or height < 3:
                return

            horizontal = width < height

            if horizontal:

                wall_y = (
                    y +
                    random.randrange(1, height - 1)
                )

                opening_x = (
                    x +
                    random.randrange(width)
                )

                for col in range(x, x + width):

                    if col == opening_x:
                        continue

                    cell = self.get(
                        wall_y,
                        col
                    )

                    if cell is not None and cell.state not in (
                        CellState.START,
                        CellState.GOAL
                    ):
                        cell.state = CellState.WALL

                divide(
                    x,
                    y,
                    width,
                    wall_y - y
                )

                divide(
                    x,
                    wall_y + 1,
                    width,
                    y + height - wall_y - 1
                )

            else:

                wall_x = (
                    x +
                    random.randrange(1, width - 1)
                )

                opening_y = (
                    y +
                    random.randrange(height)
                )

                for row in range(y, y + height):

                    if row == opening_y:
                        continue

                    cell = self.get(
                        row,
                        wall_x
                    )

                    if cell is not None and cell.state not in (
                        CellState.START,
                        CellState.GOAL
                    ):
                        cell.state = CellState.WALL

                divide(
                    x,
                    y,
                    wall_x - x,
                    height
                )

                divide(
                    wall_x + 1,
                    y,
                    x + width - wall_x - 1,
                    height
                )

        divide(
            0,
            0,
            self.size,
            self.size
        )
