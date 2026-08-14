# SearchLabs — Project Context & Architecture

SearchLabs is a Python and Pygame-based interactive pathfinding visualizer. It allows users to draw grids, set start/goal nodes, place walls/weighted terrain, and visualize various graph search algorithms step-by-step in real time.

---

## 1. Core Architecture & Design Philosophy

SearchLabs enforces a strict **separation of concerns** between the visualization engine (Pygame) and the search algorithms:
- **Pure Algorithms via Generators**: Search algorithms do **not** import Pygame. Instead, they are implemented as Python generator functions that yield visualization events defined in `grid.py`.
- **Event Protocol**: The visualizer consumes these yielded events (`Current`, `Discover`, `PathNode`, `Finished`) to update cell states and render the search progression frame-by-frame.

---

## 2. Module Breakdown

- **`main.py`**: The application entrypoint. Manages the Pygame window loop, UI panels, user inputs (mouse drawing, algorithm selection, playback speed controls, clearing/resetting), and coordinates the generator-based stepping of active search algorithms.
- **`grid.py`**: Defines grid data structures, `Grid` class, `CellState` enum (`EMPTY`, `WALL`, `START`, `GOAL`, `FRONTIER`, `CURRENT`, `VISITED`, `PATH`), and the generator event protocol dataclasses (`Current`, `Discover`, `PathNode`, `Finished`).
- **Algorithm Modules (User-Implemented)**:
  - **`bfs.py`**: Breadth-First Search (FIFO queue, unweighted shortest path).
  - **`dfs.py`**: Depth-First Search (LIFO stack, non-optimal exploration).
  - **`dijkstra.py`**: Dijkstra's Algorithm (Priority queue / min-heap with cost relaxation).
  - **`astar.py`**: A* Search (Priority queue with heuristic function $f(n) = g(n) + h(n)$).
  - **`greedy.py`**: Greedy Best-First Search (Priority queue ordered purely by heuristic $h(n)$).

---

## 3. The Generator Event Protocol

Algorithms communicate with the renderer exclusively by yielding events:
```python
from grid import Current, Discover, PathNode, Finished

# Example pattern inside a search algorithm generator:
yield Current(row, col)           # Node currently being expanded
yield Discover(neighbor_row, neighbor_col)  # Node added to frontier
# ... when goal is found ...
yield PathNode(path_row, path_col)          # Node part of final reconstructed path
yield Finished(found=True)
```

---

## 4. Setup & Running

### Requirements
- Python 3.10+
- `pygame`

### Installation & Execution
```bash
pip install pygame
python main.py
```

---

## 5. Guidelines for AI Assistants & Developers
1. **Never import `pygame` inside algorithm modules** (`bfs.py`, `dfs.py`, `dijkstra.py`, `astar.py`, `greedy.py`).
2. **Respect the Generator Contract**: Algorithms must yield events rather than mutating the grid directly or blocking with synchronous loops.
3. **AI Context Efficiency**: When assisting with algorithm implementation or bug fixes, focus strictly on the algorithm logic and adherence to the `grid.py` event protocol.
