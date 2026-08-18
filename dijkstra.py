import heapq

from grid import (
    CellState,
    Current,
    Discover,
    PathNode,
    Finished,
)


def dijkstra(grid, start, goal):
    if start is None or goal is None:
        yield Finished(found=False)
        return

    came_from = {start: None}
    cost_so_far = {start: 0}
    frontier = [(cost_so_far[start], start)]

    while frontier:

        current = heapq.heappop(frontier)[1]

        # Announce the node we are expanding now.
        yield Current(current[0], current[1])
        # Check if Node is the Goal
        if current == goal:

            path = []
            node = goal

            while node is not None:
                path.append(node)
                node = came_from[node]

            path.reverse()
            # Draw out the path from start to goal
            for cell in path:
                yield PathNode(cell[0], cell[1])

            yield Finished(found=True)
            return

        for neighbor in grid.neighbors(current[0], current[1]):

            position = (neighbor.row, neighbor.col)

            new_cost = cost_so_far[current] + neighbor.weight

            # Walls are not traversable.
            if neighbor.state == CellState.WALL:
                continue


            if position not in came_from or new_cost < cost_so_far[position]:
                cost_so_far[position] = new_cost
                came_from[position] = current
                heapq.heappush(frontier,(cost_so_far[position], position))
                yield Discover(position[0], position[1])

    # Frontier exhausted without reaching the goal.
    yield Finished(found=False)