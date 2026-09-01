from collections import deque

from grid import (
    CellState,
    Current,
    Discover,
    PathNode,
    Finished,
)



def bidirectional_bfs(grid, start, goal):
    """Bidirectional BFS.

    Expand two FIFO frontiers concurrently - one outward from ``start``
    and one backward from ``goal`` - until the two searches meet. When a
    meeting cell is found, stitch the forward and backward
    ``came_from`` trees together to reconstruct a path, then yield
    ``PathNode`` events and ``Finished(found=True)``.

    NOTE: This is a stub. Replace the body with a real generator.
    """
    def reconstruct_path(meeting_point, came_from_start, came_from_goal):          
        path = []
        node = meeting_point

          
        while node is not None:
            path.append(node)
            node = came_from_start[node]

        path.reverse()

        node = came_from_goal[meeting_point]

        while node is not None:
            path.append(node)
            node = came_from_goal[node]     

        return path

        

    if start is None or goal is None:
        yield Finished(found=False)
        return


    came_from_start = {start: None}
    came_from_goal = {goal: None}
    frontier_start = deque([start])
    frontier_goal = deque([goal])

    while frontier_start and frontier_goal:

        current_start = frontier_start.popleft()
        current_goal = frontier_goal.popleft()

        # Announce the node we are expanding now.
        yield Current(current_start[0], current_start[1])
        yield Current(current_goal[0], current_goal[1])
        # Check if Node is in came_from_start or came_from_goal

        for neighbor in grid.neighbors(current_start[0], current_start[1]):

            position = (neighbor.row, neighbor.col)

            # Walls are not traversable.
            if neighbor.state == CellState.WALL:
                continue
            
            if position not in came_from_start:
                came_from_start[position] = current_start
                frontier_start.append(position)
                yield Discover(position[0], position[1])

            if position in came_from_goal:
                meeting_point = position
                path = reconstruct_path(meeting_point, came_from_start, came_from_goal)

                for cell in path:
                  yield PathNode(cell[0], cell[1])

                yield Finished(found=True)
                return
            
        for neighbor in grid.neighbors(current_goal[0], current_goal[1]):

            position = (neighbor.row, neighbor.col)

            # Walls are not traversable.
            if neighbor.state == CellState.WALL:
                continue
            
            if position not in came_from_goal:
                came_from_goal[position] = current_goal
                frontier_goal.append(position)
                yield Discover(position[0], position[1])

            if position in came_from_start:
                meeting_point = position
                path = reconstruct_path(meeting_point, came_from_start, came_from_goal)

                for cell in path:
                  yield PathNode(cell[0], cell[1])

                yield Finished(found=True)
                return

    # Frontier exhausted without reaching the goal.
    yield Finished(found=False)
