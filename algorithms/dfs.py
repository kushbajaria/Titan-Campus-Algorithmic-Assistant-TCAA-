def dfs_cycle_and_topo(graph):
    color = {v: 0 for v in graph}  # 0=white,1=gray,2=black
    postorder = []
    has_cycle = False

    def visit(u):
        nonlocal has_cycle
        color[u] = 1
        for neighbor in graph[u]:
            # unpack neighbor if it's weighted
            if isinstance(neighbor, tuple):
                v = neighbor[0]
            else:
                v = neighbor

            if color[v] == 0:
                visit(v)
            elif color[v] == 1:
                has_cycle = True
        color[u] = 2
        postorder.append(u)

    for node in graph:
        if color[node] == 0:
            visit(node)

    if has_cycle:
        return True, []

    topo = list(reversed(postorder))
    return False, topo
