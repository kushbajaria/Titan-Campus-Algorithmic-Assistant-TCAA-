from heapq import heappush, heappop

def prim(graph, start):
    if start not in graph:
        raise ValueError("Start node does not exist in graph.")

    visited = set()
    mst_edges = []
    total_cost = 0

    pq = []
    visited.add(start)

    # Push edges from the start node (handle unweighted edges)
    for edge in graph[start]:
        if isinstance(edge, tuple):
            neighbor, weight = edge
        else:
            neighbor, weight = edge, 1  # default weight for unweighted graph
        heappush(pq, (weight, start, neighbor))

    while pq:
        weight, u, v = heappop(pq)

        if v in visited:
            continue

        # Accept the edge
        visited.add(v)
        mst_edges.append((u, v, weight))
        total_cost += weight

        # Push all outgoing edges from v
        for edge in graph[v]:
            if isinstance(edge, tuple):
                neighbor, w = edge
            else:
                neighbor, w = edge, 1

            if neighbor not in visited:
                heappush(pq, (w, v, neighbor))

    # Check for disconnected graph
    disconnected = len(visited) != len(graph)

    return mst_edges, total_cost, disconnected
