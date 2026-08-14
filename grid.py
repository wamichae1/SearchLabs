import random
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto


# ============================================================
# GRID SIZES
# ============================================================

DEFAULT_GRID_SIZE = 25
MIN_GRID_SIZE = 15
MAX_GRID_SIZE = 45


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

        valid_sizes = [15, 25, 35, 45]
        if size is not None:
            if size in valid_sizes:
                self.size = size
            else:
                self.size = min(valid_sizes, key=lambda x: abs(x - size))
        elif self.size not in valid_sizes:
            self.size = DEFAULT_GRID_SIZE

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
        saved_start = self.start
        saved_goal = self.goal

        self.clear_walls()

        # Fill entire grid with walls first
        for row in range(self.size):
            for col in range(self.size):
                cell = self.get(row, col)
                if cell is not None:
                    cell.state = CellState.WALL

        # Carve passages using Randomized DFS (Recursive Backtracker)
        # Guarantees strictly 1-cell wide corridors and 1-cell thick walls (no double-wide roads).
        start_r, start_c = 1, 1
        if start_r >= self.size:
            start_r = 0
        if start_c >= self.size:
            start_c = 0

        cell = self.get(start_r, start_c)
        if cell is not None:
            cell.state = CellState.EMPTY

        stack = [(start_r, start_c)]

        while stack:
            r, c = stack[-1]
            neighbors = []
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    n_cell = self.get(nr, nc)
                    if n_cell is not None and n_cell.state == CellState.WALL:
                        neighbors.append((nr, nc, r + dr // 2, c + dc // 2))

            if neighbors:
                nr, nc, wr, wc = random.choice(neighbors)
                w_cell = self.get(wr, wc)
                n_cell = self.get(nr, nc)
                if w_cell is not None:
                    w_cell.state = CellState.EMPTY
                if n_cell is not None:
                    n_cell.state = CellState.EMPTY
                stack.append((nr, nc))
            else:
                stack.pop()

        # Add multiple paths (braiding) by opening some internal separating walls
        # to create loops and alternative routes without creating 2x2 open blocks.
        internal_walls = []
        for r in range(1, self.size - 1):
            for c in range(1, self.size - 1):
                cell = self.get(r, c)
                if cell is not None and cell.state == CellState.WALL:
                    top = self.get(r - 1, c)
                    bottom = self.get(r + 1, c)
                    left = self.get(r, c - 1)
                    right = self.get(r, c + 1)

                    is_h = (top and top.state == CellState.EMPTY) and (bottom and bottom.state == CellState.EMPTY) and not ((left and left.state == CellState.EMPTY) and (right and right.state == CellState.EMPTY))
                    is_v = (left and left.state == CellState.EMPTY) and (right and right.state == CellState.EMPTY) and not ((top and top.state == CellState.EMPTY) and (bottom and bottom.state == CellState.EMPTY))

                    if is_h or is_v:
                        internal_walls.append((r, c))

        random.shuffle(internal_walls)
        extra_count = int(len(internal_walls) * 0.3)  # 30% braiding for multiple paths
        for r, c in internal_walls[:extra_count]:
            w_cell = self.get(r, c)
            if w_cell is not None:
                w_cell.state = CellState.EMPTY

        self._ensure_fully_connected()

        self._restore_endpoint(saved_start, self.set_start)
        self._restore_endpoint(saved_goal, self.set_goal)

    def _is_walkable(self, cell):
        return cell is not None and cell.state != CellState.WALL

    def _open_cells(self):

        positions = []

        for row in range(self.size):

            for col in range(self.size):

                cell = self.get(row, col)

                if self._is_walkable(cell):
                    positions.append((row, col))

        return positions

    def _reachable_from(self, start):

        frontier = deque([start])
        seen = {start}

        while frontier:

            current = frontier.popleft()

            for neighbor in self.neighbors(current[0], current[1]):

                if not self._is_walkable(neighbor):
                    continue

                position = (neighbor.row, neighbor.col)

                if position in seen:
                    continue

                seen.add(position)
                frontier.append(position)

        return seen

    def is_fully_connected(self):
        """True when every open cell belongs to one component."""

        opens = self._open_cells()

        if len(opens) <= 1:
            return True

        return len(self._reachable_from(opens[0])) == len(opens)

    def _label_components(self):

        labels = {}
        next_id = 0

        for position in self._open_cells():

            if position in labels:
                continue

            frontier = deque([position])
            labels[position] = next_id

            while frontier:

                current = frontier.popleft()

                for neighbor in self.neighbors(current[0], current[1]):

                    if not self._is_walkable(neighbor):
                        continue

                    npos = (neighbor.row, neighbor.col)

                    if npos in labels:
                        continue

                    labels[npos] = next_id
                    frontier.append(npos)

            next_id += 1

        return labels

    def _find_bridge_wall(self):
        """Return a wall separating two open components, if any."""

        labels = self._label_components()

        for row in range(self.size):

            for col in range(self.size):

                cell = self.get(row, col)

                if cell is None or cell.state != CellState.WALL:
                    continue

                neighbor_components = set()

                for neighbor in self.neighbors(row, col):

                    if not self._is_walkable(neighbor):
                        continue

                    neighbor_components.add(
                        labels[(neighbor.row, neighbor.col)]
                    )

                if len(neighbor_components) >= 2:
                    return (row, col)

        return None

    def _ensure_fully_connected(self):
        """Remove walls until every open cell can reach every other."""

        while not self.is_fully_connected():

            bridge = self._find_bridge_wall()

            if bridge is not None:

                cell = self.get(*bridge)

                if cell is not None:
                    cell.state = CellState.EMPTY
                continue

            self._punch_extra_openings(1)

    def _restore_endpoint(self, position, setter):

        if position is None:
            return

        cell = self.get(*position)

        if cell is not None and cell.state == CellState.WALL:
            cell.state = CellState.EMPTY

        setter(*position)

    def has_path(self, start, goal):
        """True when goal is reachable from start through non-wall cells."""

        if start is None or goal is None:
            return False

        frontier = deque([start])
        seen = {start}

        while frontier:

            current = frontier.popleft()

            if current == goal:
                return True

            for neighbor in self.neighbors(current[0], current[1]):

                position = (neighbor.row, neighbor.col)

                if (
                    neighbor.state == CellState.WALL
                    or position in seen
                ):
                    continue

                seen.add(position)
                frontier.append(position)

        return False

    def _punch_extra_openings(self, count):
        """Remove random walls to add alternate routes through the maze."""

        walls = []

        for row in range(self.size):

            for col in range(self.size):

                cell = self.get(row, col)

                if cell is not None and cell.state == CellState.WALL:
                    walls.append((row, col))

        random.shuffle(walls)

        for row, col in walls[:count]:

            cell = self.get(row, col)

            if cell is not None:
                cell.state = CellState.EMPTY
