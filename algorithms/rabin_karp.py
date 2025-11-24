def rabin_karp(text, pattern):
    d = 256          # number of characters in input alphabet
    q = 101          # prime modulus (classic RK)

    n = len(text)
    m = len(pattern)

    if m == 0:
        return []

    if m > n:
        return []

    # initial values
    p = 0       # hash of pattern
    t = 0       # hash of current text window
    h = 1

    # precompute h = d^(m-1) % q
    for _ in range(m - 1):
        h = (h * d) % q

    # initial hash for pattern and first text window
    for i in range(m):
        p = (d * p + ord(pattern[i])) % q
        t = (d * t + ord(text[i])) % q

    occurrences = []

    # slide over text
    for s in range(n - m + 1):
        if p == t:
            # verify characters (to avoid collision issues)
            match = True
            for j in range(m):
                if text[s + j] != pattern[j]:
                    match = False
                    break
            if match:
                occurrences.append(s)

        # Recompute hash for next window
        if s < n - m:
            t = (d * (t - ord(text[s]) * h) + ord(text[s + m])) % q
            if t < 0:
                t += q

    return occurrences
