from heapq import heappush, heappop

def dijkstra(graph, start):
    # initialize distances and parents for all nodes
    distances = {node: float('inf') for node in graph}
    distances[start] = 0

    parent = {node: None for node in graph}

    pq = []
    heappush(pq, (0, start))
    visited = set()

    while pq:
        current_dist, u = heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        for edge in graph[u]:

            # Support both weighted and unweighted
            if isinstance(edge, tuple):
                v, w = edge
            else:
                # If unweighted, treat weight as 1
                v, w = edge, 1

            # Dijkstra cannot handle negative weights
            if w < 0:
                raise ValueError("Dijkstra cannot be used with negative edge weights")

            if v in visited:
                continue

            new_dist = current_dist + w

            if new_dist < distances[v]:
                distances[v] = new_dist
                parent[v] = u
                heappush(pq, (new_dist, v))

    return distances, parent


def rebuild_path(parent, target):
    path = []
    cur = target

    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)

    path.reverse()
    return path
