# SearchLabs 

SearchLabs is an interactive, real-time pathfinding algorithm visualizer built with **Python** and **Pygame**. It provides a rich laboratory environment for exploring, comparing, and writing graph search algorithms on customizable grid worlds.

---

## Key Features

- **Multiple Algorithms**: Compare BFS, DFS, Dijkstra, A*, Greedy Best-First Search, and more side-by-side.
- **Braided Multi-Path Mazes**: Generate mazes with multiple alternative paths and loops (avoiding single-solution bottlenecks so sub-optimal algorithms like DFS and Greedy can take different routes).
- **Weighted Terrain (1–5)**: Paint terrain weights (2–5) with blue gradient shading and clear center-rendered numbers. Dijkstra, A*, and Greedy factor terrain weights into path cost calculations.
- **Dark & Light Modes**: Instantly toggle between Dark and Light themes via the header icon button.
- **Adjustable Grid Sizes**: Resize grids (15x15, 25x25, 35x35, 45x45).
- **Interactive Controls**: Click and drag to draw walls, place Start/Goal nodes, scatter random walls or weights, adjust playback speed, and pause/step search execution.

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Pygame

### Installation
```bash
pip install pygame
```

### Running the Application
```bash
python main.py
```

---

## How to Create Your Own Search Algorithms

SearchLabs uses a strict **separation of concerns**: search algorithms are pure Python **generator functions** that do **not** import Pygame. Instead, they communicate with the visualizer exclusively through a generator event protocol defined in `grid.py`.

### 1. The Event Protocol
Algorithms yield specific event dataclasses imported from `grid.py`:
- `Current(row, col)`: Signals the node currently being expanded/processed.
- `Discover(row, col)`: Signals a neighbor discovered and added to the frontier.
- `PathNode(row, col)`: Yielded in reverse order upon finding the goal to reconstruct the final path.
- `Finished(found=True/False)`: Signals the completion of the search.

### 2. Algorithm Template
Here is the standard structure for writing your own search algorithm (e.g. in a new file `my_algorithm.py`):

```python
from grid import Current, Discover, PathNode, Finished

def my_algorithm(grid, start, goal):
    """
    grid: The Grid instance.
    start: (row, col) tuple of the start position.
    goal: (row, col) tuple of the goal position.
    """
    if start is None or goal is None:
        yield Finished(found=False)
        return

    # Initialize data structures (e.g. queue, stack, or min-heap)
    frontier = [start]
    came_from = {start: None}
    visited = {start}

    while frontier:
        # Pop next node according to your search strategy
        current = frontier.pop(0) # e.g. FIFO for BFS, LIFO for DFS, min-heap for Dijkstra/A*

        # Yield Current event so the visualizer highlights it
        yield Current(current[0], current[1])

        if current == goal:
            # Rebuild path from came_from dictionary
            path = []
            curr = goal
            while curr is not None:
                path.append(curr)
                curr = came_from.get(curr)
            
            # Yield PathNode for each cell in the final path
            for r, c in path:
                yield PathNode(r, c)
            
            yield Finished(found=True)
            return

        # Explore neighbors
        for neighbor in grid.neighbors(current[0], current[1]):
            if neighbor.state == CellState.WALL: # or CellState check
                continue
            
            pos = (neighbor.row, neighbor.col)
            if pos not in visited:
                visited.add(pos)
                came_from[pos] = current
                frontier.append(pos)
                
                # Note: For weighted algorithms (Dijkstra/A*), factor in neighbor.weight:
                # step_cost = neighbor.weight
                
                yield Discover(pos[0], pos[1])

    # If frontier exhausts without finding goal
    yield Finished(found=False)
```

### 2. File Layout
Algorithms are grouped by category so the project stays easy to extend. Move your algorithm file into the matching folder and import it from there:

```text
algorithms/
    standard/
        bfs.py
        dfs.py
        greedy.py
        dijkstra.py
        astar.py
        thetastar.py        # optional research algorithm
    bidirectional/           # add Bidirectional BFS/Dijkstra here later
```

Each module is a pure generator (no `pygame` imports) that yields the event protocol from `grid.py`.

### 3. Registering Your Algorithm in `main.py`
Algorithms are organized into **categories/tabs** in the top navigation bar (`Standard` and `Bidirectional`):
- `Standard` holds the classic searches (BFS, DFS, Dijkstra, A*, Greedy, ...).
- `Bidirectional` is a scaffold category ready for your bidirectional searches.

To add a new algorithm to a category:
1. Place its generator module under the matching `algorithms/<category>/` folder and import it at the top of `main.py`:
   ```python
   from algorithms.standard.my_algorithm import my_algorithm   # or algorithms.bidirectional...
   ```
2. Register it in the matching list of `self.algorithms_by_category` inside `Application.__init__`:
   ```python
   "My Category": [
       ...
       Algorithm(
           "MY",                  # button label
           "My Custom Algorithm", # Full title
           my_algorithm,          # Generator function reference
           "Description of strategy...",
           "Data structure...",
           "Time/Space Complexity...",
           "Optimal: Yes/No"
       ),
   ]
   ```
3. Pick the category tab from the top navigation bar to select it in the carousel.

The `Bidirectional` category starts empty on purpose - selecting it shows an empty state so you can implement the algorithms yourself without any placeholder search behavior.
