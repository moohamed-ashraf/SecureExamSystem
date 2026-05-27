"""Prime generation using Miller-Rabin."""

from __future__ import annotations

import random

from rsa.mod_exp import mod_exp


def miller_rabin(n: int, k: int = 20) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    r = 0
    d = n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_exp(a, d, n)

        if x == 1 or x == n - 1:
            continue

        composite = True
        for _ in range(r - 1):
            x = mod_exp(x, 2, n)
            if x == n - 1:
                composite = False
                break

        if composite:
            return False

    return True


def generate_prime(bits: int) -> int:
    if bits < 8:
        raise ValueError("Prime bit length must be at least 8")

    while True:
        candidate = random.getrandbits(bits)
        candidate |= 1 << (bits - 1)
        candidate |= 1
        if miller_rabin(candidate):
            return candidate
