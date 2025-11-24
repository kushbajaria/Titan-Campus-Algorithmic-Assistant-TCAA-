def greedy_scheduler(tasks, available_time):
    """
    tasks = [(name, time, value), ...]
    available_time = int
    """
    # Sort by value/time ratio (descending)
    tasks_sorted = sorted(tasks, key=lambda x: x[2] / x[1], reverse=True)

    chosen = []
    total_time = 0
    total_value = 0

    for name, t, v in tasks_sorted:
        if total_time + t <= available_time:
            chosen.append((name, t, v))
            total_time += t
            total_value += v

    return chosen, total_time, total_value
