def rebuild_path(parent, target):
    path = []
    cur = target

    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)

    path.reverse()
    return path