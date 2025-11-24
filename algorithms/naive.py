def naive_string_match(text, pattern):
    n = len(text)
    m = len(pattern)

    if m == 0:
        return []  # no empty-pattern matches allowed

    occurrences = []

    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            occurrences.append(i)

    return occurrences
