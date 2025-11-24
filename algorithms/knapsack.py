def dp_optimal_scheduler(tasks, available_time):
    """
    tasks = [(name, time, value)]
    Solve 0/1 knapsack to maximize value.
    """
    n = len(tasks)
    dp = [[0] * (available_time + 1) for _ in range(n + 1)]

    # Build DP table
    for i in range(1, n + 1):
        name, t, v = tasks[i - 1]
        for cap in range(available_time + 1):
            if t > cap:
                dp[i][cap] = dp[i - 1][cap]
            else:
                dp[i][cap] = max(dp[i - 1][cap], dp[i - 1][cap - t] + v)

    # Recover chosen tasks
    chosen = []
    cap = available_time
    total_time = 0

    for i in range(n, 0, -1):
        name, t, v = tasks[i - 1]
        if dp[i][cap] != dp[i - 1][cap]:  # task was used
            chosen.append((name, t, v))
            cap -= t
            total_time += t

    chosen.reverse()
    total_value = dp[n][available_time]

    return chosen, total_time, total_value
