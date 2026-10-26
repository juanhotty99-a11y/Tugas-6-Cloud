#!/usr/bin/env python3
"""
Tugas 6 - Soal 1 Chord.

Ruang identifier m = 5 bit (0..31). Node aktual (lingkaran yang diarsir pada
gambar soal): 1, 4, 7, 12, 15, 20, 27.

  a. Finger table:  FT_p[i] = succ(p + 2^(i-1)),  i = 1..m
  b. Lookup key k dari node p (aturan pada buku Tanenbaum):
       - jika p < k <= FT_p[1]  -> teruskan ke FT_p[1] (successor), selesai
       - selain itu teruskan ke FT_p[j] dengan FT_p[j] <= k < FT_p[j+1]
         (finger terjauh yang tidak melewati k)
"""

M     = 5
RING  = 2 ** M
NODES = [1, 4, 7, 12, 15, 20, 27]


def succ(k):
    k %= RING
    for n in sorted(NODES):
        if n >= k:
            return n
    return min(NODES)


def in_interval(x, a, b):
    """x berada pada interval melingkar (a, b]"""
    x, a, b = x % RING, a % RING, b % RING
    if a < b:
        return a < x <= b
    return x > a or x <= b


def finger_table(p):
    return [(i, (p + 2 ** (i - 1)) % RING, succ(p + 2 ** (i - 1))) for i in range(1, M + 1)]


def print_finger_table(p):
    print(f"Finger table node {p}")
    print(f"  {'i':>2} | {'p + 2^(i-1)':>14} | {'FT[i] = succ':>12}")
    for i, start, s in finger_table(p):
        expr = f"{p}+{2 ** (i - 1)}={p + 2 ** (i - 1)}"
        if p + 2 ** (i - 1) >= RING:
            expr += f"->{start}"
        print(f"  {i:>2} | {expr:>14} | {s:>12}")
    print()


def lookup(start, key):
    p, path = start, [start]
    while True:
        ft = [s for _, _, s in finger_table(p)]
        if p == key:
            return path
        if in_interval(key, p, ft[0]):
            print(f"  node {p:>2}: {key} di ({p}, {ft[0]}] -> successor FT[1] = {ft[0]}")
            path.append(ft[0])
            return path
        nxt = ft[0]
        for f in reversed(ft):
            if in_interval(f, p, key - 1):
                nxt = f
                break
        print(f"  node {p:>2}: FT = {ft} -> finger terjauh yang <= {key} adalah {nxt}")
        p = nxt
        path.append(p)


if __name__ == "__main__":
    print(f"m = {M}, ruang id 0..{RING - 1}, node aktual = {NODES}\n")
    for node in (1, 12, 20, 27):
        print_finger_table(node)

    print("Lookup key 26 dari node 1")
    path = lookup(1, 26)
    print("  Urutan lookup: " + " -> ".join(str(n) for n in path))
    print(f"  Key 26 disimpan di succ(26) = {succ(26)}")
