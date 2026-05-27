"""AES MixColumns transformation."""

from __future__ import annotations

from typing import List


def _xtime(a: int) -> int:
    a <<= 1
    if a & 0x100:
        a ^= 0x11B
    return a & 0xFF


def _gf_mul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a = _xtime(a)
        b >>= 1
    return result & 0xFF


def mix_columns(state: List[int]) -> None:
    for col in range(4):
        i = col * 4
        s0, s1, s2, s3 = state[i], state[i + 1], state[i + 2], state[i + 3]
        state[i] = _gf_mul(0x02, s0) ^ _gf_mul(0x03, s1) ^ s2 ^ s3
        state[i + 1] = s0 ^ _gf_mul(0x02, s1) ^ _gf_mul(0x03, s2) ^ s3
        state[i + 2] = s0 ^ s1 ^ _gf_mul(0x02, s2) ^ _gf_mul(0x03, s3)
        state[i + 3] = _gf_mul(0x03, s0) ^ s1 ^ s2 ^ _gf_mul(0x02, s3)


def inv_mix_columns(state: List[int]) -> None:
    for col in range(4):
        i = col * 4
        s0, s1, s2, s3 = state[i], state[i + 1], state[i + 2], state[i + 3]
        state[i] = _gf_mul(0x0E, s0) ^ _gf_mul(0x0B, s1) ^ _gf_mul(0x0D, s2) ^ _gf_mul(0x09, s3)
        state[i + 1] = _gf_mul(0x09, s0) ^ _gf_mul(0x0E, s1) ^ _gf_mul(0x0B, s2) ^ _gf_mul(0x0D, s3)
        state[i + 2] = _gf_mul(0x0D, s0) ^ _gf_mul(0x09, s1) ^ _gf_mul(0x0E, s2) ^ _gf_mul(0x0B, s3)
        state[i + 3] = _gf_mul(0x0B, s0) ^ _gf_mul(0x0D, s1) ^ _gf_mul(0x09, s2) ^ _gf_mul(0x0E, s3)
