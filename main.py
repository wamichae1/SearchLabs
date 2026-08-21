import time
from dataclasses import dataclass

import pygame

from grid import (
    CellState,
    Discover,
    Current,
    PathNode,
    Finished,
    Grid,
)
from bfs import bfs
from dfs import dfs
from dijkstra import dijkstra
from astar import astar
from greedy import greedy
from bidirectional import bidirectional
from thetastar import thetastar

pygame.init()

# ============================================================
# WINDOW SETTINGS
# ============================================================

INITIAL_WIDTH = 1280
INITIAL_HEIGHT = 680

MIN_WINDOW_WIDTH = 1280
MIN_WINDOW_HEIGHT = 680

FPS = 60
INSTANT_SPEED = 61

screen = pygame.display.set_mode(
    (INITIAL_WIDTH, INITIAL_HEIGHT),
    pygame.RESIZABLE
)

pygame.display.set_caption("SearchLabs")

clock = pygame.time.Clock()



# ============================================================
# THEMES
# ============================================================

DARK_THEME = {
    "BG": (22, 24, 29),
    "PANEL": (30, 33, 40),
    "GRID_BACKGROUND": (236, 240, 246),
    "GRID_LINE": (65, 69, 78),
    "WALL": (35, 38, 44),
    "TEXT": (235, 237, 240),
    "MUTED_TEXT": (160, 165, 175),
    "ACCENT": (85, 150, 235),
    "BUTTON": (55, 60, 70),
    "BUTTON_HOVER": (70, 76, 88),
    "SLIDER_TRACK": (45, 50, 58),
}

LIGHT_THEME = {
    "BG": (245, 247, 250),
    "PANEL": (255, 255, 255),
    "GRID_BACKGROUND": (255, 255, 255),
    "GRID_LINE": (210, 215, 225),
    "WALL": (190, 195, 205),
    "TEXT": (30, 33, 40),
    "MUTED_TEXT": (100, 105, 115),
    "ACCENT": (40, 110, 200),
    "BUTTON": (225, 230, 238),
    "BUTTON_HOVER": (210, 216, 226),
    "SLIDER_TRACK": (200, 205, 215),
}

# ============================================================
# COLORS
# ============================================================

BG = (22, 24, 29)
PANEL = (30, 33, 40)

GRID_BACKGROUND = (236, 240, 246)
GRID_LINE = (65, 69, 78)

WALL = (35, 38, 44)
START = (60, 190, 105)
GOAL = (220, 75, 75)
FRONTIER = (245, 190, 75)
CURRENT = (255, 255, 255)
VISITED = (100, 165, 230)
PATH = (170, 100, 220)

TEXT = (235, 237, 240)
MUTED_TEXT = (160, 165, 175)
ACCENT = (150, 204, 255)

BUTTON = (55, 60, 70)
BUTTON_HOVER = (70, 76, 88)
SLIDER_TRACK = (45, 50, 58)

# Edit-mode pill colors (for the footer indicator).
MODE_COLORS = {
    "wall": (110, 116, 128),
    "start": START,
    "goal": GOAL,
    "erase": (130, 100, 160),
}


# ============================================================
# FONTS
# ============================================================

FONT = pygame.font.SysFont("consolas", 17)
SMALL_FONT = pygame.font.SysFont("consolas", 14)
TITLE_FONT = pygame.font.SysFont("consolas", 27, bold=True)
SECTION_FONT = pygame.font.SysFont("consolas", 19, bold=True)


# ============================================================
# LAYOUT CONSTANTS
# ============================================================

TOP_PAD = 20
SECTION_GAP = 8
SECTION_TITLE_PAD = 20
LINE_GAP = 18
BUTTON_HEIGHT = 28
BUTTON_GAP = 6

TOAST_DURATION = 1.6
TOAST_FADE = 0.5
TOAST_TEXT_COLOR = TEXT


# ============================================================
# ALGORITHM REGISTRY
# ============================================================

@dataclass
class Algorithm:
    """A pluggable search. `func` is a generator that yields
    the event protocol defined in grid.py. Add new searches
    here and they appear in the selector automatically."""
    key: str
    label: str
    func: object
    strategy: str
    structure: str
    complexity: str
    optimality: str


# ============================================================
# SEARCH VISUALIZER
# ============================================================

class SearchVisualizer:

    def __init__(self, grid):

        self.grid = grid

        self.algorithm = None

        self.running = False
        self.paused = False
        self.finished = False
        self.found = False

        self.generator = None
        self.current = None

        self.nodes_explored = 0
        self.nodes_discovered = 0
        self.path_length = 0
        self.path_cost = None
        self._current_path_cells = []

        self.start_time = None
        self.elapsed_time = 0.0

        self.not_implemented = None

    def reset(self):

        self.running = False
        self.paused = False
        self.finished = False
        self.found = False

        self.generator = None
        self.current = None

        self.nodes_explored = 0
        self.nodes_discovered = 0
        self.path_length = 0
        self.path_cost = None
        self._current_path_cells = []

        self.start_time = None
        self.elapsed_time = 0.0

        self.not_implemented = None

        self.grid.clear_search()

    def start(self, paused=False):

        if self.algorithm is None:
            return

        self.grid.clear_search()

        self.running = True
        self.paused = paused
        self.finished = False
        self.found = False
        self.not_implemented = None

        self.current = None
        self.generator = self.algorithm.func(
            self.grid,
            self.grid.start,
            self.grid.goal
        )

        self.nodes_explored = 0
        self.nodes_discovered = 0
        self.path_length = 0
        self.path_cost = None
        self._current_path_cells = []

        self.start_time = time.perf_counter()
        self.elapsed_time = 0.0

    def pause(self):

        if not self.running:
            return

        if self.paused:
            # Resume: shift start time so the clock keeps the
            # frozen elapsed value.
            self.start_time = (
                time.perf_counter()
                - self.elapsed_time
            )
            self.paused = False
        else:
            # Freeze: store elapsed before pausing.
            self.elapsed_time = (
                time.perf_counter()
                - self.start_time
            )
            self.paused = True

    def step(self):

        if self.generator is None or self.finished:
            return

        try:

            event = next(self.generator)
            self.process_event(event)

        except StopIteration:

            # Defensive: a well-behaved algorithm yields
            # Finished before stopping, but guard anyway.
            self.running = False
            self.finished = True

        except NotImplementedError as e:

            # A scaffold algorithm was selected before its
            # body was filled in. Surface it as a toast
            # instead of crashing the app.
            self.not_implemented = (
                str(e) or "Not implemented yet"
            )
            self.running = False
            self.paused = False
            self.generator = None

    def process_event(self, event):

        if isinstance(event, Current):

            # Settle the previous current cell into Visited.
            if self.current is not None:

                previous = self.grid.get(*self.current)

                if (
                    previous is not None
                    and previous.state == CellState.CURRENT
                ):
                    previous.state = CellState.VISITED

            cell = self.grid.get(event.row, event.col)

            if (
                cell is not None
                and cell.state not in (
                    CellState.START,
                    CellState.GOAL
                )
            ):
                cell.state = CellState.CURRENT

            self.current = (event.row, event.col)
            self.nodes_explored += 1

        elif isinstance(event, Discover):

            cell = self.grid.get(event.row, event.col)

            if cell is not None and cell.state == CellState.EMPTY:
                cell.state = CellState.FRONTIER

            self.nodes_discovered += 1

        elif isinstance(event, PathNode):

            cell = self.grid.get(event.row, event.col)

            if (
                cell is not None
                and cell.state not in (
                    CellState.START,
                    CellState.GOAL
                )
            ):
                cell.state = CellState.PATH

            self.path_length += 1
            if not hasattr(self, '_current_path_cells') or self._current_path_cells is None:
                self._current_path_cells = []
            self._current_path_cells.append((event.row, event.col))

        elif isinstance(event, Finished):

            # Settle any lingering current cell.
            if self.current is not None:

                previous = self.grid.get(*self.current)

                if (
                    previous is not None
                    and previous.state == CellState.CURRENT
                ):
                    previous.state = CellState.VISITED

            self.running = False
            self.finished = True
            self.found = event.found
            self.path_cost = getattr(event, 'cost', None)

            if self.found and self.path_cost is None and hasattr(self, '_current_path_cells'):
                self.path_cost = sum(
                    self.grid.get(r, c).weight
                    for r, c in self._current_path_cells
                    if self.grid.get(r, c) is not None
                )

            if not event.found:
                self.path_length = 0
                self.path_cost = None

            self.elapsed_time = (
                time.perf_counter()
                - self.start_time
            )

    def run_status(self):

        if self.not_implemented:
            return "Not implemented", MUTED_TEXT

        if self.generator is None:
            if (
                self.grid.start is None
                or self.grid.goal is None
            ):
                return "Set start and goal", GOAL
            return "Ready", MUTED_TEXT

        if self.finished:
            if self.found:
                if self.path_cost is not None:
                    return (
                        f"Path found: {self.path_length} nodes | Cost: {self.path_cost:g}",
                        START
                    )
                return (
                    f"Path found: {self.path_length} nodes",
                    START
                )
            return "No path found", GOAL

        if self.paused:
            return "Paused", MUTED_TEXT

        return "Running…", FRONTIER


# ============================================================
# BUTTON
# ============================================================

class Button:

    def __init__(self, text, action):

        self.text = text
        self.action = action

        self.rect = pygame.Rect(
            0,
            0,
            0,
            0
        )

    def set_rect(
        self,
        x,
        y,
        width,
        height
    ):

        self.rect = pygame.Rect(
            round(x),
            round(y),
            round(width),
            round(height)
        )

    def draw(self, surface):

        if self.rect.collidepoint(
            pygame.mouse.get_pos()
        ):
            color = BUTTON_HOVER
        else:
            color = BUTTON

        pygame.draw.rect(
            surface,
            color,
            self.rect,
            border_radius=6
        )

        pygame.draw.rect(
            surface,
            GRID_LINE,
            self.rect,
            width=1,
            border_radius=6
        )

        text_surface = SMALL_FONT.render(
            self.text,
            True,
            TEXT
        )

        surface.blit(
            text_surface,
            text_surface.get_rect(
                center=self.rect.center
            )
        )

    def handle_event(self, event):

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        if self.rect.collidepoint(event.pos):
            self.action()


# ============================================================
# SLIDER
# ============================================================

class Slider:
    """Horizontal speed slider: 1–60 steps per frame, 61 = instant."""

    def __init__(self, low=1, high=500, value=8):

        self.low = low
        self.high = high
        self.value = value

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.dragging = False

    def set_rect(self, x, y, width, height):

        self.rect = pygame.Rect(
            round(x),
            round(y),
            round(width),
            round(height)
        )

    def _proportion(self):

        if self.high == self.low:
            return 0.0

        return (self.value - self.low) / (self.high - self.low)

    def _set_from_x(self, x):

        proportion = (
            (x - self.rect.left)
            / max(1, self.rect.width)
        )

        proportion = max(0.0, min(1.0, proportion))

        self.value = round(
            self.low
            + proportion * (self.high - self.low)
        )

    def handle_event(self, event):

        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.dragging = True
            self._set_from_x(event.pos[0])

        elif (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
        ):
            self.dragging = False

        elif (
            event.type == pygame.MOUSEMOTION
            and self.dragging
        ):
            self._set_from_x(event.pos[0])

    def draw(self, surface):

        track = pygame.Rect(
            self.rect.left,
            self.rect.centery - 3,
            self.rect.width,
            6
        )

        pygame.draw.rect(
            surface,
            SLIDER_TRACK,
            track,
            border_radius=3
        )

        fill_width = int(track.width * self._proportion())

        if fill_width > 0:

            fill = pygame.Rect(
                track.left,
                track.top,
                fill_width,
                track.height
            )

            pygame.draw.rect(
                surface,
                ACCENT,
                fill,
                border_radius=3
            )

        handle_x = track.left + fill_width

        pygame.draw.circle(
            surface,
            TEXT,
            (handle_x, track.centery),
            7
        )

        pygame.draw.circle(
            surface,
            ACCENT,
            (handle_x, track.centery),
            4
        )


# ============================================================
# APPLICATION
# ============================================================

class Application:

    def __init__(self):

        self.grid = Grid()

        self.visualizer = SearchVisualizer(self.grid)

        self.algorithms = [
            Algorithm(
                "BFS",
                "Breadth-First Search",
                bfs,
                "Explores in concentric rings; nearest first.",
                "Data structure: Queue (FIFO)",
                "O(V + E) time   |   O(V) space",
                "Optimal: Yes (unweighted)"
            ),
            Algorithm(
                "DFS",
                "Depth-First Search",
                dfs,
                "Plunges down one branch, then backtracks.",
                "Data structure: Stack (LIFO)",
                "O(V + E) time   |   O(V) space",
                "Optimal: No"
            ),
            Algorithm(
                "Dijkstra",
                "Dijkstra's Algorithm",
                dijkstra,
                "Expands the lowest-cost node first.",
                "Data structure: Priority queue (min-heap)",
                "O((V + E) log V) time   |   O(V) space",
                "Optimal: Yes"
            ),
            Algorithm(
                "A*",
                "A* Search",
                astar,
                "Lowest f = g + h first; h guides to goal.",
                "Data structure: Priority queue (min-heap)",
                "O((V + E) log V) time   |   O(V) space",
                "Optimal: Yes (admissible h)"
            ),
            Algorithm(
                "Greedy",
                "Greedy Best-First",
                greedy,
                "Lowest heuristic h first; races to goal.",
                "Data structure: Priority queue (min-heap)",
                "O((V + E) log V) time   |   O(V) space",
                "Optimal: No"
            ),
            Algorithm(
                "BI",
                "Bidirectional Search",
                bidirectional,
                "Searches simultaneously from start and goal.",
                "Data structure: Two Queues / Bidirectional",
                "O(b^(d/2)) time   |   O(b^(d/2)) space",
                "Optimal: Yes (unweighted)"
            ),
            Algorithm(
                "TH",
                "Theta* Search",
                thetastar,
                "Any-angle pathfinding using line-of-sight.",
                "Data structure: Priority Queue (A* variant)",
                "O(V log V) time   |   O(V) space",
                "Optimal: Any-angle shortest path"
            )
        ]

        self.selected_algorithm = (
            self.algorithms[0]
            if self.algorithms
            else None
        )

        self.visualizer.algorithm = self.selected_algorithm

        self.dark_mode = True
        self.apply_theme()
        self.edit_mode = "wall"

        self.mouse_drawing = False
        self.mouse_erasing = False
        self._last_weight_cell = None

        self.slider = Slider(low=1, high=INSTANT_SPEED, value=8)

        self.show_help = False

        self.toast_text = None
        self.toast_color = TOAST_TEXT_COLOR
        self.toast_set_time = 0.0

        self.search_buttons = [
            Button("Run", self.run_algorithm),
            Button("Pause / Resume", self.toggle_pause),
            Button("Step", self.step_algorithm),
            Button("Reset Search", self.reset_search)
        ]

        self.utility_buttons = [
            Button("Random Walls", self.random_walls),
            Button("Random Weights", self.random_weights),
            Button("Generate Maze", self.generate_maze),
            Button("Clear Walls", self.clear_walls),
            Button("Random Start/Goal", self.randomize_start_goal),
            Button("Reset Grid", self.reset_grid)
        ]

        self.algorithm_pills = []

        self._layout_cache_key = None
        self._layout = None

    # ========================================================
    # TOAST
    # ========================================================

    def set_toast(self, text, color=TOAST_TEXT_COLOR):

        self.toast_text = text
        self.toast_color = color
        self.toast_set_time = time.perf_counter()

    # ========================================================
    # ALGORITHM SELECTION
    # ========================================================

    def select_algorithm(self, algorithm):

        if algorithm is self.selected_algorithm:
            return

        self.selected_algorithm = algorithm
        self.visualizer.algorithm = algorithm
        self.visualizer.reset()

        self.set_toast(f"Algorithm: {algorithm.label}", ACCENT)

    def cycle_algorithm(self, direction):

        if not self.algorithms:
            return

        if self.selected_algorithm is None:
            self.select_algorithm(self.algorithms[0])
            return

        index = self.algorithms.index(self.selected_algorithm)
        count = len(self.algorithms)
        nxt = (index + direction) % count

        self.select_algorithm(self.algorithms[nxt])

    # ========================================================
    # DYNAMIC LAYOUT
    # ========================================================

    def get_layout(self):

        size = screen.get_size()

        if self._layout_cache_key != size:
            self._layout_cache_key = size
            self._layout = self._compute_layout(size)

        return self._layout

    def _compute_layout(self, size):

        width, height = size

        # Right panel gets ~30% of the screen, capped so it
        # does not balloon on very wide monitors.
        panel_width = int(width * 0.30)

        panel_width = max(300, panel_width)
        panel_width = min(430, panel_width)

        left_width = width - panel_width

        header_height = 72
        footer_height = 58
        legend_height = 28
        gap = 8
        margin = 24

        grid_area = pygame.Rect(
            margin,
            header_height,
            left_width - 2 * margin,
            height
            - header_height
            - footer_height
            - legend_height
            - 2 * gap
        )

        legend_rect = pygame.Rect(
            margin,
            grid_area.bottom + gap,
            left_width - 2 * margin,
            legend_height
        )

        panel = pygame.Rect(
            left_width,
            0,
            panel_width,
            height
        )

        # The grid must always remain square and centered.
        side = min(grid_area.width, grid_area.height)

        grid_rect = pygame.Rect(
            round(grid_area.centerx - side / 2),
            round(grid_area.centery - side / 2),
            round(side),
            round(side)
        )

        return {
            "width": width,
            "height": height,
            "left_width": left_width,
            "panel": panel,
            "grid_area": grid_area,
            "grid_rect": grid_rect,
            "legend_rect": legend_rect
        }

    def get_actual_grid_rect(self):

        return self.get_layout()["grid_rect"]

    def _grid_boundary(self, start, span, index):
        """Pixel boundary that partitions span into grid.size slices."""

        return start + (index * span) // self.grid.size

    def cell_rect(self, row, col):

        grid = self.get_actual_grid_rect()
        size = self.grid.size

        left = self._grid_boundary(grid.left, grid.width, col)
        right = self._grid_boundary(grid.left, grid.width, col + 1)
        top = self._grid_boundary(grid.top, grid.height, row)
        bottom = self._grid_boundary(grid.top, grid.height, row + 1)

        return pygame.Rect(left, top, right - left, bottom - top)

    # ========================================================
    # ACTIONS
    # ========================================================

    def run_algorithm(self):

        v = self.visualizer

        if not self.check_endpoints():
            return

        if v.generator is None or v.finished:
            v.start()
        elif v.paused:
            v.pause()

    def toggle_pause(self):

        v = self.visualizer
        v.pause()

        if v.running:
            self.set_toast(
                "Paused" if v.paused else "Resumed",
                MUTED_TEXT
            )

    def step_algorithm(self):

        if not self.check_endpoints():
            return

        if self.visualizer.generator is None:
            self.visualizer.start(paused=True)

        self.visualizer.step()

    def check_endpoints(self):
        """Returns True when both start and goal are set.
        Warns via toast otherwise so Run/Step is not a
        silent no-op."""

        if (
            self.grid.start is None
            or self.grid.goal is None
        ):
            self.set_toast("Set start and goal", GOAL)
            return False

        return True

    def reset_search(self):

        self.visualizer.reset()
        self.set_toast("Search reset", MUTED_TEXT)

    def random_walls(self):

        self.visualizer.reset()
        self.grid.generate_random_walls()
        self.set_toast("Random walls", MUTED_TEXT)

    def generate_maze(self):

        self.visualizer.reset()
        self.grid.generate_maze()
        self.set_toast("Maze generated", MUTED_TEXT)

    def clear_walls(self):

        self.visualizer.reset()
        self.grid.clear_walls()
        self.set_toast("Walls cleared", MUTED_TEXT)

    def randomize_start_goal(self):

        self.visualizer.reset()
        self.grid.randomize_start_goal()
        self.set_toast("Start / Goal randomized", MUTED_TEXT)


    def random_weights(self):
        self.grid.generate_random_weights(density=0.25)
        self.set_toast("Random weights scattered", MUTED_TEXT)

    def reset_grid(self):

        self.visualizer.reset()
        self.grid.reset()
        self.set_toast("Grid reset", MUTED_TEXT)

    def change_grid_size(self, delta):
        valid_sizes = [15, 25, 35, 45]
        try:
            curr_idx = valid_sizes.index(self.grid.size)
        except ValueError:
            curr_idx = 1

        new_idx = max(0, min(len(valid_sizes) - 1, curr_idx + (1 if delta > 0 else -1)))
        new_size = valid_sizes[new_idx]

        self.visualizer.reset()
        self.grid.reset(new_size)
        self.set_toast(
            f"Grid: {self.grid.size}x{self.grid.size}",
            MUTED_TEXT
        )

    def set_edit_mode(self, mode):

        self.edit_mode = mode
        self.set_toast(f"Mode: {mode.upper()}", ACCENT)

    # ========================================================
    # GRID MOUSE INTERACTION
    # ========================================================

    def mouse_to_cell(self, position):

        grid = self.get_actual_grid_rect()

        if not grid.collidepoint(position):
            return None

        relative_x = position[0] - grid.left
        relative_y = position[1] - grid.top

        col = int(
            relative_x / grid.width * self.grid.size
        )
        row = int(
            relative_y / grid.height * self.grid.size
        )

        if (
            0 <= row < self.grid.size
            and 0 <= col < self.grid.size
        ):
            return row, col

        return None

    def edit_cell(self, position):

        cell_position = self.mouse_to_cell(position)

        if cell_position is None:
            return

        # Never edit the grid while a search is live; it
        # would desync colors and counts.
        if self.visualizer.running:
            return

        row, col = cell_position

        cell = self.grid.get(row, col)

        if cell is None:
            return

        if self.edit_mode == "wall":

            if cell.state not in (
                CellState.START,
                CellState.GOAL
            ):
                cell.state = CellState.WALL

        elif self.edit_mode == "start":
            self.grid.set_start(row, col)

        elif self.edit_mode == "goal":
            self.grid.set_goal(row, col)

        elif self.edit_mode == "erase":

            if cell.state == CellState.WALL:
                cell.state = CellState.EMPTY

        elif self.edit_mode == "weight":
            if cell.state == CellState.EMPTY:
                current_time = time.perf_counter()
                if self._last_weight_cell != (row, col) or (current_time - getattr(self, '_last_weight_time', 0) > 0.2):
                    self.grid.cycle_weight(row, col)
                    self._last_weight_cell = (row, col)
                    self._last_weight_time = current_time

    def erase_wall_at(self, position):

        if self.visualizer.running:
            return

        cell_position = self.mouse_to_cell(position)

        if cell_position is None:
            return

        row, col = cell_position

        cell = self.grid.get(row, col)

        if cell is not None and cell.state == CellState.WALL:
            cell.state = CellState.EMPTY

    # ========================================================
    # DRAWING
    # ========================================================

    def draw(self):

        screen.fill(BG)

        self.draw_header()

        self.draw_grid()

        self.draw_legend_strip()

        self.draw_panel()

        self.draw_footer()

        if self.show_help:
            self.draw_help_overlay()

        self.draw_toast()

        pygame.display.flip()


    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.set_toast(f"Theme: {'Dark' if self.dark_mode else 'Light'}", ACCENT)

    def apply_theme(self):
        theme = DARK_THEME if self.dark_mode else LIGHT_THEME
        global BG, PANEL, GRID_BACKGROUND, GRID_LINE, WALL, TEXT, MUTED_TEXT, ACCENT, BUTTON, BUTTON_HOVER, SLIDER_TRACK, TOAST_TEXT_COLOR, MODE_COLORS
        BG = theme["BG"]
        PANEL = theme["PANEL"]
        GRID_BACKGROUND = theme["GRID_BACKGROUND"]
        GRID_LINE = theme["GRID_LINE"]
        WALL = theme["WALL"]
        TEXT = theme["TEXT"]
        MUTED_TEXT = theme["MUTED_TEXT"]
        ACCENT = theme["ACCENT"]
        BUTTON = theme["BUTTON"]
        BUTTON_HOVER = theme["BUTTON_HOVER"]
        SLIDER_TRACK = theme["SLIDER_TRACK"]
        TOAST_TEXT_COLOR = TEXT
        MODE_COLORS = {
            "wall": (130, 138, 155) if self.dark_mode else (155, 165, 180),
            "start": (70, 205, 115) if self.dark_mode else (50, 160, 90),
            "goal": (235, 85, 85) if self.dark_mode else (210, 60, 60),
            "erase": (155, 120, 190) if self.dark_mode else (135, 100, 170),
            "weight": (120, 165, 210) if self.dark_mode else (80, 130, 185),
        }

    def draw_header(self):

        title = TITLE_FONT.render(
            "SearchLabs",
            True,
            TEXT
        )

        screen.blit(title, (24, 20))

        # Theme toggle button (circle with sun/moon icon) beside title
        title_width = title.get_width()
        toggle_x = 24 + title_width + 20
        toggle_y = 20 + title.get_height() // 2
        toggle_radius = 14
        self.theme_button_rect = pygame.Rect(
            toggle_x - toggle_radius,
            toggle_y - toggle_radius,
            toggle_radius * 2,
            toggle_radius * 2
        )

        mouse_pos = pygame.mouse.get_pos()
        hovered = self.theme_button_rect.collidepoint(mouse_pos)
        btn_color = BUTTON_HOVER if hovered else BUTTON

        pygame.draw.circle(screen, btn_color, (toggle_x, toggle_y), toggle_radius)

        if self.dark_mode:
            # Draw Crescent Moon icon: pale blue circle with button-color cutout
            moon_color = (110, 160, 230)
            pygame.draw.circle(screen, moon_color, (toggle_x, toggle_y), 7)
            pygame.draw.circle(screen, btn_color, (toggle_x + 3, toggle_y - 2), 6)            
        else:
            # Draw Sun icon: golden center circle with 4 small ray dots
            sun_color = (255, 215, 60)
            pygame.draw.circle(screen, sun_color, (toggle_x, toggle_y), 5)
            for dx, dy in [
                (-8, 0), (8, 0),
                (0, -8), (0, 8),
                (-6, -6), (6, -6),
                (-6, 6), (6, 6)
            ]:
                pygame.draw.circle(
                    screen,
                    sun_color,
                    (toggle_x + dx, toggle_y + dy),
                    1.5
                )         

        subtitle = SMALL_FONT.render(
            "Interactive visual search algorithm laboratory",
            True,
            MUTED_TEXT
        )

        screen.blit(subtitle, (24, 51))

    def cell_color(self, cell):

        if cell.state == CellState.EMPTY:
            if cell.weight == 0:
                return GRID_BACKGROUND
            if self.dark_mode:
                shades = {
                    1: (95, 150, 245),
                    2: (75, 120, 195),
                    3: (55, 95, 155),
                    4: (42, 70, 115),
                    5: (30, 50, 80)
                }
                return shades.get(cell.weight, (50, 90, 150))
            else:
                base_r, base_g, base_b = 220, 235, 255
                tint_step = (cell.weight - 1) * 15
                return (max(0, base_r - tint_step), max(0, base_g - tint_step), base_b)

        return {
            CellState.WALL: WALL,
            CellState.START: START,
            CellState.GOAL: GOAL,
            CellState.FRONTIER: FRONTIER,
            CellState.CURRENT: CURRENT,
            CellState.VISITED: VISITED,
            CellState.PATH: PATH
        }[cell.state]

    def draw_grid(self):

        grid = self.get_actual_grid_rect()

        pygame.draw.rect(
            screen,
            GRID_BACKGROUND,
            grid
        )

        # Show weights only if the cell size is consistently large enough (width/height > 14 pixels).
        # This avoids partially hidden numbers due to rounding/alignment issues on smaller screen layouts.
        show_weights = (grid.width // self.grid.size) > 14

        # Draw cells.
        for row in range(self.grid.size):

            for col in range(self.grid.size):

                cell = self.grid.get(row, col)

                rect = self.cell_rect(row, col)

                pygame.draw.rect(
                    screen,
                    self.cell_color(cell),
                    rect
                )

                if show_weights and cell.state == CellState.EMPTY and cell.weight > 0:
                    text_col = (230, 235, 245) if self.dark_mode else (40, 60, 90)
                    weight_surf = SMALL_FONT.render(str(cell.weight), True, text_col)
                    screen.blit(
                        weight_surf,
                        weight_surf.get_rect(center=rect.center)
                    )

        # Current-node highlight ring (only while active).
        if self.visualizer.running and self.visualizer.current:

            current_rect = self.cell_rect(*self.visualizer.current)

            pygame.draw.rect(
                screen,
                GRID_LINE,
                current_rect,
                width=2,
                border_radius=2
            )

        # Draw grid lines as complete boundaries, once.
        for index in range(self.grid.size + 1):

            # Horizontal line
            start_x = grid.left
            end_x = grid.right
            y = self._grid_boundary(grid.top, grid.height, index)

            pygame.draw.line(
                screen,
                GRID_LINE,
                (start_x, y),
                (end_x, y),
                1
            )

            # Vertical line
            start_y = grid.top
            end_y = grid.bottom
            x = self._grid_boundary(grid.left, grid.width, index)

            pygame.draw.line(
                screen,
                GRID_LINE,
                (x, start_y),
                (x, end_y),
                1
            )

    def draw_legend_strip(self):

        rect = self.get_layout()["legend_rect"]

        entries = [
            ("Start", START, False),
            ("Goal", GOAL, False),
            ("Wall", WALL, False),
            ("Frontier", FRONTIER, False),
            ("Current", CURRENT, True),
            ("Visited", VISITED, False),
            ("Path", PATH, False)
        ]

        gap = 18

        items = []
        total = 0

        for word, color, ring in entries:

            word_surf = SMALL_FONT.render(word, True, MUTED_TEXT)

            item_w = 14 + 4 + word_surf.get_width()

            items.append((word, color, ring, word_surf, item_w))
            total += item_w

        total += gap * (len(items) - 1)

        x = rect.centerx - total / 2
        y = rect.y + (rect.height - 14) // 2

        for word, color, ring, word_surf, item_w in items:

            swatch_x = round(x)
            swatch = pygame.Rect(swatch_x, y, 14, 14)

            pygame.draw.rect(screen, color, swatch)

            pygame.draw.rect(
                screen,
                GRID_LINE,
                swatch,
                width=1
            )

            if ring:
                pygame.draw.rect(
                    screen,
                    GRID_LINE,
                    swatch.inflate(-4, -4),
                    width=1
                )

            screen.blit(word_surf, (swatch_x + 18, y - 1))

            x += item_w + gap

    # ========================================================
    # RIGHT PANEL
    # ========================================================

    def draw_panel(self):

        panel = self.get_layout()["panel"]

        pygame.draw.rect(screen, PANEL, panel)

        x = panel.x + 20
        content_width = panel.width - 40

        y = TOP_PAD

        y = self.draw_algorithm_section(x, content_width, y)

        y += SECTION_GAP
        y = self.draw_speed_section(x, content_width, y)

        y += SECTION_GAP
        self.draw_section_title("CONTROLS", x, y)
        y += SECTION_TITLE_PAD

        self.layout_search_buttons(x, content_width, y)

        for button in self.search_buttons:
            button.draw(screen)

        y += len(self.search_buttons) * (
            BUTTON_HEIGHT + BUTTON_GAP
        ) + 10

        self.layout_utility_buttons(x, content_width, y)

        for button in self.utility_buttons:
            button.draw(screen)

        rows = (len(self.utility_buttons) + 1) // 2
        y += rows * (BUTTON_HEIGHT + BUTTON_GAP)

        y += SECTION_GAP
        self.draw_run_section(x, content_width, y)

    def layout_search_buttons(self, x, width, start_y):

        y = start_y

        for button in self.search_buttons:
            button.set_rect(
                x,
                y,
                width,
                BUTTON_HEIGHT
            )
            y += BUTTON_HEIGHT + BUTTON_GAP

    def layout_utility_buttons(self, x, width, start_y):

        column_width = (width - BUTTON_GAP) // 2

        for index, button in enumerate(
            self.utility_buttons
        ):

            column = index % 2
            row = index // 2

            button.set_rect(
                x + column * (column_width + BUTTON_GAP),
                start_y + row * (BUTTON_HEIGHT + BUTTON_GAP),
                column_width,
                BUTTON_HEIGHT
            )

    def draw_section_title(self, title, x, y):

        surface = SECTION_FONT.render(title, True, TEXT)

        screen.blit(surface, (x, y))

    def draw_algorithm_section(self, x, width, start_y):

        y = start_y

        self.draw_section_title("ALGORITHM", x, y)
        y += SECTION_TITLE_PAD

        # Cyclical Carousel Selector: [ ? ]  Algorithm Name  [ ? ]
        carousel_h = 32
        arrow_w = 32

        self.carousel_prev_rect = pygame.Rect(x, y, arrow_w, carousel_h)
        self.carousel_next_rect = pygame.Rect(x + width - arrow_w, y, arrow_w, carousel_h)
        carousel_box = pygame.Rect(x + arrow_w + 4, y, width - (arrow_w * 2) - 8, carousel_h)

        mouse_pos = pygame.mouse.get_pos()
        prev_hover = self.carousel_prev_rect.collidepoint(mouse_pos)
        next_hover = self.carousel_next_rect.collidepoint(mouse_pos)

        # Draw left arrow button
        pygame.draw.rect(screen, BUTTON_HOVER if prev_hover else BUTTON, self.carousel_prev_rect, border_radius=8)
        pygame.draw.rect(screen, GRID_LINE, self.carousel_prev_rect, width=1, border_radius=8)
        arrow_left = SMALL_FONT.render("<", True, TEXT)
        screen.blit(arrow_left, arrow_left.get_rect(center=self.carousel_prev_rect.center))

        # Draw right arrow button
        pygame.draw.rect(screen, BUTTON_HOVER if next_hover else BUTTON, self.carousel_next_rect, border_radius=8)
        pygame.draw.rect(screen, GRID_LINE, self.carousel_next_rect, width=1, border_radius=8)
        arrow_right = SMALL_FONT.render(">", True, TEXT)
        screen.blit(arrow_right, arrow_right.get_rect(center=self.carousel_next_rect.center))

        # Draw center box
        pygame.draw.rect(screen, BUTTON, carousel_box, border_radius=8)
        pygame.draw.rect(screen, GRID_LINE, carousel_box, width=1, border_radius=8)

        name_text = self.selected_algorithm.label if self.selected_algorithm else "Select Algorithm"
        name_surf = SMALL_FONT.render(name_text, True, ACCENT)
        screen.blit(name_surf, name_surf.get_rect(center=carousel_box.center))

        y += carousel_h + 8

        # "[Tab] cycle" hint beneath carousel.
        if len(self.algorithms) > 1:
            hint = SMALL_FONT.render(
                "[Tab] cycle",
                True,
                MUTED_TEXT
            )
            screen.blit(hint, (x, y))
            y += 16

        y += 4

        algorithm = self.selected_algorithm

        if algorithm is None:
            name = "No Algorithm Selected"
            info = [
                "No algorithm connected yet.",
                "",
                "Register a search to begin."
            ]
        else:
            name = algorithm.label
            info = [
                algorithm.strategy,
                algorithm.structure,
                algorithm.complexity,
                algorithm.optimality
            ]

        screen.blit(
            FONT.render(name, True, ACCENT),
            (x, y)
        )
        y += 24

        for line in info:

            if line:
                screen.blit(
                    SMALL_FONT.render(line, True, MUTED_TEXT),
                    (x, y)
                )

            y += LINE_GAP

        return y

    def draw_speed_section(self, x, width, start_y):

        y = start_y

        self.draw_section_title("SPEED", x, y)
        y += SECTION_TITLE_PAD

        if self.slider.value >= INSTANT_SPEED:
            speed_text = "Instant"
        else:
            speed_text = f"{self.slider.value} steps / frame"

        label = SMALL_FONT.render(
            speed_text,
            True,
            TEXT
        )

        screen.blit(label, (x, y))
        y += 22

        self.slider.set_rect(x, y, width, 14)
        self.slider.draw(screen)

        return y + 14 + 4

    def draw_run_section(self, x, width, start_y):

        y = start_y

        self.draw_section_title("CURRENT RUN", x, y)
        y += SECTION_TITLE_PAD

        # Status line.
        status_text, status_color = (
            self.visualizer.run_status()
        )

        screen.blit(
            FONT.render(status_text, True, status_color),
            (x, y)
        )

        stats_y = y + 28

        # Elapsed time (live while running and unpaused).
        if (
            self.visualizer.start_time is not None
            and self.visualizer.running
            and not self.visualizer.paused
        ):
            elapsed = (
                time.perf_counter()
                - self.visualizer.start_time
            )
        else:
            elapsed = self.visualizer.elapsed_time

        stats = [
            ("Explored", str(self.visualizer.nodes_explored)),
            ("Discovered", str(self.visualizer.nodes_discovered)),
            ("Path length", str(self.visualizer.path_length)),
            ("Runtime", f"{elapsed * 1000:.2f} ms")
        ]

        for index, (label, value) in enumerate(stats):

            line_y = stats_y + index * LINE_GAP

            screen.blit(
                SMALL_FONT.render(label, True, MUTED_TEXT),
                (x, line_y)
            )

            value_surf = SMALL_FONT.render(value, True, TEXT)

            screen.blit(
                value_surf,
                (
                    x + width - value_surf.get_width(),
                    line_y
                )
            )

    # ========================================================
    # FOOTER
    # ========================================================

    def draw_footer(self):

        layout = self.get_layout()

        height = layout["height"]
        left_width = layout["left_width"]

        line_1 = (
            "[1] Wall    [2] Start    "
            "[3] Goal    [4] Erase    "
            "[5] Weights"
        )

        line_2 = (
            "[Space] Pause    [Tab] Algorithm    "
            "[+/-] Grid    [H] Help    [Esc] Quit"
        )

        screen.blit(
            SMALL_FONT.render(line_1, True, MUTED_TEXT),
            (24, height - 52)
        )

        screen.blit(
            SMALL_FONT.render(line_2, True, MUTED_TEXT),
            (24, height - 30)
        )

        # Colored mode pill, right-aligned on line 1.
        mode_label = f"MODE: {self.edit_mode.upper()}"
        mode_surf = SMALL_FONT.render(mode_label, True, TEXT)
        pill_w = mode_surf.get_width() + 16
        pill_h = 20
        pill_x = left_width - 24 - pill_w
        pill_y = height - 52 - 3

        mode_color = MODE_COLORS.get(self.edit_mode, ACCENT)

        pill_rect = pygame.Rect(pill_x, pill_y, pill_w, pill_h)

        pygame.draw.rect(
            screen,
            mode_color,
            pill_rect,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            GRID_LINE,
            pill_rect,
            width=1,
            border_radius=10
        )

        screen.blit(
            mode_surf,
            mode_surf.get_rect(center=pill_rect.center)
        )

    # ========================================================
    # HELP OVERLAY
    # ========================================================

    def draw_help_overlay(self):

        layout = self.get_layout()

        width, height = layout["width"], layout["height"]

        # Dim the whole window.
        dim = pygame.Surface((width, height), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 185))
        screen.blit(dim, (0, 0))

        panel_w = 470
        panel_h = 350

        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (width // 2, height // 2)

        pygame.draw.rect(
            screen,
            PANEL,
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            GRID_LINE,
            panel,
            width=1,
            border_radius=10
        )

        title = SECTION_FONT.render(
            "KEYBOARD SHORTCUTS",
            True,
            TEXT
        )

        screen.blit(title, (panel.x + 24, panel.y + 18))

        lines = [
            (
                "Edit",
                "[1] Wall  [2] Start  [3] Goal  [4] Erase"
            ),
            (
                "Run",
                "[Space] Pause / Resume  [R] Reset search"
            ),
            (
                "Algorithms",
                "[Tab] Next  [Shift+Tab] Previous"
            ),
            (
                "Grid",
                "[+] / [-] Resize  [C] Clear walls  [M] Maze"
            ),
            (
                "Other",
                "[H] help Menu  [Esc] Quit"
            )
        ]

        y = panel.y + 62

        for label, desc in lines:

            screen.blit(
                SMALL_FONT.render(label, True, ACCENT),
                (panel.x + 24, y)
            )

            screen.blit(
                SMALL_FONT.render(desc, True, TEXT),
                (panel.x + 116, y)
            )

            y += 38

        footer = SMALL_FONT.render(
            "Press H or Esc to close",
            True,
            MUTED_TEXT
        )

        screen.blit(
            footer,
            footer.get_rect(
                centerx=panel.centerx,
                bottom=panel.bottom - 14
            )
        )

    # ========================================================
    # TOAST
    # ========================================================

    def draw_toast(self):

        if self.toast_text is None:
            return

        age = time.perf_counter() - self.toast_set_time

        if age >= TOAST_DURATION:
            self.toast_text = None
            return

        fade_start = TOAST_DURATION - TOAST_FADE

        if age < fade_start:
            alpha = 255
        else:
            alpha = int(
                255 * (1 - (age - fade_start) / TOAST_FADE)
            )

        alpha = max(0, min(255, alpha))

        text_surf = FONT.render(
            self.toast_text,
            True,
            self.toast_color
        )

        pad_x = 14
        pad_y = 8

        toast_w = text_surf.get_width() + pad_x * 2
        toast_h = text_surf.get_height() + pad_y * 2

        toast_surf = pygame.Surface(
            (toast_w, toast_h),
            pygame.SRCALPHA
        )

        toast_bg = (30, 34, 42) if self.dark_mode else (250, 252, 255)
        pygame.draw.rect(
            toast_surf,
            toast_bg,
            toast_surf.get_rect(),
            border_radius=8
        )

        pygame.draw.rect(
            toast_surf,
            GRID_LINE,
            toast_surf.get_rect(),
            width=1,
            border_radius=8
        )

        toast_surf.blit(text_surf, (pad_x, pad_y))

        toast_surf.set_alpha(alpha)

        grid_area = self.get_layout()["grid_area"]

        screen.blit(
            toast_surf,
            toast_surf.get_rect(
                centerx=grid_area.centerx,
                top=grid_area.y + 20
            )
        )

    # ========================================================
    # EVENT HANDLING
    # ========================================================

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, 'theme_button_rect') and self.theme_button_rect.collidepoint(event.pos):
                self.toggle_theme()
                return
            if hasattr(self, 'carousel_prev_rect') and self.carousel_prev_rect.collidepoint(event.pos):
                self.cycle_algorithm(-1)
                return
            if hasattr(self, 'carousel_next_rect') and self.carousel_next_rect.collidepoint(event.pos):
                self.cycle_algorithm(1)
                return

        if event.type == pygame.VIDEORESIZE:

            width = max(MIN_WINDOW_WIDTH, event.w)
            height = max(MIN_WINDOW_HEIGHT, event.h)

            cur_w, cur_h = screen.get_size()
            if width != cur_w or height != cur_h:
                pygame.display.set_mode(
                    (width, height),
                    pygame.RESIZABLE
                )

            return

        # The help overlay is modal: only its own close
        # keys are accepted while it is open.
        if self.show_help:

            if (
                event.type == pygame.KEYDOWN
                and event.key in (
                    pygame.K_h,
                    pygame.K_ESCAPE
                )
            ):
                self.show_help = False

            return

        for button in self.search_buttons:
            button.handle_event(event)

        for button in self.utility_buttons:
            button.handle_event(event)

        self.slider.handle_event(event)

        # Keyboard
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_1:
                self.set_edit_mode("wall")

            elif event.key == pygame.K_2:
                self.set_edit_mode("start")

            elif event.key == pygame.K_3:
                self.set_edit_mode("goal")

            elif event.key == pygame.K_4:
                self.set_edit_mode("erase")

            elif event.key == pygame.K_5:
                self.set_edit_mode("weight")

            elif event.key == pygame.K_r:
                self.reset_search()

            elif event.key == pygame.K_c:
                self.clear_walls()

            elif event.key == pygame.K_m:
                self.generate_maze()

            elif event.key == pygame.K_SPACE:
                self.toggle_pause()

            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                self.change_grid_size(1)

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.change_grid_size(-1)

            elif event.key == pygame.K_TAB:
                if event.mod & pygame.KMOD_SHIFT:
                    self.cycle_algorithm(-1)
                else:
                    self.cycle_algorithm(1)

            elif event.key == pygame.K_h:
                self.show_help = True

            elif event.key == pygame.K_ESCAPE:
                pygame.event.post(
                    pygame.event.Event(pygame.QUIT)
                )



        # Mouse
        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if self.mouse_to_cell(event.pos) is not None:

                    if self.visualizer.running:
                        # Editing blocked mid-search.
                        return

                    # Clear stale results before editing.
                    if (
                        self.visualizer.finished
                        or self.visualizer.nodes_explored
                    ):
                        self.visualizer.reset()

                    self.mouse_drawing = True
                    self.edit_cell(event.pos)

            elif event.button == 3:

                # Begin a right-click erase drag. Holding the
                # right button lets you clear several walls in
                # one stroke, mirroring left-click wall
                # drawing.
                if self.visualizer.running:
                    return

                # Clear stale search results before editing.
                if (
                    self.visualizer.finished
                    or self.visualizer.nodes_explored
                ):
                    self.visualizer.reset()

                self.mouse_erasing = True
                self.erase_wall_at(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:
                self.mouse_drawing = False

            elif event.button == 3:
                self.mouse_erasing = False

        elif event.type == pygame.MOUSEMOTION:

            if self.mouse_drawing:
                self.edit_cell(event.pos)

            elif self.mouse_erasing:
                self.erase_wall_at(event.pos)

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self):

        v = self.visualizer

        if v.running and not v.paused and not v.finished:
            if self.slider.value >= INSTANT_SPEED:
                while v.running and not v.finished:
                    v.step()
            else:
                for _ in range(self.slider.value):
                    if not v.running or v.finished:
                        break
                    v.step()

        # Surface a "not implemented" notice if a scaffold
        # algorithm was just run.
        if v.not_implemented:
            self.set_toast(v.not_implemented, GOAL)
            v.not_implemented = None


# ============================================================
# MAIN
# ============================================================

def main():

    app = Application()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            app.handle_event(event)

        app.update()

        app.draw()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
