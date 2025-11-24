from collections import deque

def bfs_shortest_paths(graph, start):
    dist = {v: float('inf') for v in graph}
    parent = {v: None for v in graph}
    visited = set()
    q = deque([start])
    visited.add(start)
    dist[start] = 0
    order = []

    while q:
        u = q.popleft()
        order.append(u)


        for v, _ in graph[u]:
            if v not in visited:
                visited.add(v)
                dist[v] = dist[u] + 1  # BFS hop count
                parent[v] = u
                q.append(v)

    return dist, parent, order


def reconstruct_path(parent, start, target):
    rev_path = []
    cur = target

    while cur is not None:
        rev_path.append(cur)
        if cur == start:
            break
        cur = parent.get(cur, None)

    if not rev_path or rev_path[-1] != start:
        return []

    return list(reversed(rev_path))
