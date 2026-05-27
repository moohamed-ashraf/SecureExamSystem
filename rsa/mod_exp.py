"""Modular exponentiation (square-and-multiply). No pow(a,b,m)."""

from __future__ import annotations


def mod_exp(base: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0

    result = 1
    base = base % modulus

    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        exponent >>= 1
        if exponent:
            base = (base * base) % modulus

    return result
