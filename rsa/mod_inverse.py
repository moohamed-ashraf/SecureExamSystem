"""Modular multiplicative inverse."""

from __future__ import annotations

from rsa.gcd import extended_gcd


def mod_inverse(a: int, m: int) -> int:
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m
